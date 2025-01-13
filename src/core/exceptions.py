from typing import Optional
from fastapi import status


class BaseAPIError(Exception):
    """Base class for API errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        retry_after: Optional[int] = None
    ):
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(self.message)


class GitHubAPIError(BaseAPIError):
    """GitHub API specific errors."""
    pass


class RateLimitError(GitHubAPIError):
    """Rate limit exceeded error."""
    pass


class OpenAIError(BaseAPIError):
    """OpenAI API specific errors."""
    pass
