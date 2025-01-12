from pydantic_settings import BaseSettings
from functools import lru_cache


class GitHubServiceSettings(BaseSettings):

    TOKEN: str

    class Config:
        env_file = ".env"
        env_prefix = "GITHUB_"
        extra = "allow"


@lru_cache()
def get_github_service_settings() -> GitHubServiceSettings:
    return GitHubServiceSettings()
