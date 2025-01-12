class CodeReviewException(Exception):
    """Base exception for code review service"""
    pass


class GitHubAPIError(CodeReviewException):
    """Raised when there's an error with GitHub API"""
    pass


class OpenAIError(CodeReviewException):
    """Raised when there's an error with OpenAI API"""
    pass
