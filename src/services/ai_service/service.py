from typing import List
from openai import AsyncOpenAI
from openai import OpenAIError as InternalOpenAIError
from loguru import logger

from src.core.exceptions import OpenAIError
from src.services.ai_service.config import get_ai_service_settings
from src.services.ai_service.prompts import CodeReviewPrompts
from src.services.ai_service.schemas import Message
from src.services.github_service.schemas import CodeFile
from src.utils.rate_limiter import retry_with_backoff

settings = get_ai_service_settings()


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.API_KEY)
        self.model: str = settings.MODEL

    @retry_with_backoff(retries=3, backoff_factor=2)
    async def send_message(
        self,
        messages: List[Message],
    ) -> str:
        try:
            logger.debug(f"Sending message to OpenAI with model {self.model}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[msg.model_dump() for msg in messages],
            )

            logger.debug("Successfully received response from OpenAI")
            return response.choices[0].message.content

        except InternalOpenAIError as e:
            error_msg = str(e).lower()
            if 'rate limit' in error_msg:
                retry_after = getattr(e, 'retry_after', 20)
                raise OpenAIError(
                    message="Rate limit exceeded",
                    status_code=429,
                    retry_after=retry_after
                )
            else:
                raise OpenAIError(
                    message="Failed to get AI response",
                    status_code=getattr(e, 'status_code', 500)
                )
        except Exception as e:
            raise OpenAIError(
                message=f"Unexpected error: {str(e)}",
                status_code=500
            )

    async def send_code_review_message(
        self,
        code_files: List[CodeFile],
        assignment_description: str,
        candidate_level: str,
    ) -> str:
        messages = self.prepare_message_to_send(
            system_message=CodeReviewPrompts.SYSTEM_MESSAGE,
            user_message=CodeReviewPrompts.generate_review_prompt(
                code_files=code_files,
                assignment_description=assignment_description,
                candidate_level=candidate_level
            )
        )
        logger.info("Preparing code review request...")
        logger.debug(f"Number of files to review: {len(code_files)}")
        logger.debug(f"Candidate level: {candidate_level}")

        ai_review = await self.send_message(messages)
        logger.info("Successfully received code review from AI")
        return ai_review

    @staticmethod
    def prepare_message_to_send(
        system_message: str,
        user_message: str,
    ) -> List[Message]:
        return [
            Message(role="system", content=system_message),
            Message(role="user", content=user_message)
        ]


def get_ai_service() -> AIService:
    return AIService()
