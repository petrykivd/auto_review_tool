from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class GitHubServiceSettings(BaseSettings):
    TOKEN: str
    REVIEW_ALL_FILES: bool = True
    SUPPORTED_EXTENSIONS: set = {'.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs'}
    MAX_FILE_SIZE: int = 1024 * 1024  # 1MB

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GITHUB_",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_github_service_settings() -> GitHubServiceSettings:
    return GitHubServiceSettings()
