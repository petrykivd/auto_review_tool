from fastapi import APIRouter, HTTPException
from loguru import logger

from src.schemas.code_review import CodeReviewResponse, ErrorResponse, CodeReviewRequest

router = APIRouter(prefix="/code-review", tags=["code-review"])


@router.post(
    "/review",
    response_model=CodeReviewResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def review_code(request: CodeReviewRequest) -> CodeReviewResponse:
    try:
        logger.info(
            f"Received review request for repository: {request.github_repo_url}"
            f", candidate level: {request.candidate_level}"
        )

        return CodeReviewResponse(
            found_files=["main.py", "tests/test_main.py"],
            comments=[
                "Good use of type hints",
                "Consider adding more documentation",
                "Tests could be more comprehensive"
            ],
            rating=8,
            conclusion="Overall good code quality with room for improvement in documentation and testing."
        )

    except Exception as e:
        logger.error(f"Error processing review request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process code review: {str(e)}"
        )
