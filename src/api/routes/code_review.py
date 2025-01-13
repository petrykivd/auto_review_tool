from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from src.schemas.code_review import (
    CodeReviewResponse,
    ErrorResponse,
    CodeReviewRequest
)
from src.services.ai_service.service import AIService, get_ai_service
from src.services.cache.service import RedisService, get_redis_service
from src.services.github_service.service import GitHubService, get_github_service

router = APIRouter(prefix="/code-review", tags=["code-review"])


@router.post(
    "/review",
    response_model=CodeReviewResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def review_code(
    request: CodeReviewRequest,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service),
    cache_service: RedisService = Depends(get_redis_service)
) -> CodeReviewResponse:
    try:
        logger.info(
            f"Starting code review for repository: {request.github_repo_url}, "
            f"candidate level: {request.candidate_level}"
        )
        cache_key = cache_service.generate_key(
            "code_review",
            repo_url=str(request.github_repo_url),
            candidate_level=request.candidate_level
        )

        if cached_response := await cache_service.get(cache_key):
            logger.info("Returning cached review result")
            return CodeReviewResponse.model_validate_json(cached_response)

        files = await github_service.get_repository_files(request.github_repo_url)
        file_names = [file.path for file in files]
        ai_review = await ai_service.send_code_review_message(
            code_files=files,
            assignment_description=request.assignment_description,
            candidate_level=request.candidate_level
        )
        response = CodeReviewResponse(
            found_files=file_names,
            ai_review_result=ai_review,
        )
        await cache_service.set(cache_key, response.model_dump_json())
        return response

    except Exception as e:
        logger.error(f"Error processing review request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process code review: {str(e)}"
        )
