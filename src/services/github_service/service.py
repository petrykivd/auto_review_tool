from typing import Dict, List
from urllib.parse import urlparse

from github import Github, GithubException
from loguru import logger
from pydantic import HttpUrl


from src.core.exceptions import GitHubAPIError
from src.services.github_service.config import get_github_service_settings

settings = get_github_service_settings()


class GitHubService:

    def __init__(self):
        self.client = Github(login_or_token=settings.TOKEN)

    async def get_repository_files(self, repo_url: HttpUrl) -> List[Dict[str, str]]:
        try:
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            logger.info(f"Fetching repository files for {repo_url}")
            contents = repo.get_contents("")
            files = []

            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    files.append({
                        "path": file_content.path,
                        "size": file_content.size,
                        "type": "file",
                        "url": file_content.url
                    })
            logger.info(f"Found {len(files)} files in {repo_url}")
            logger.info(f"Files: {[file['path'] for file in files]}")
            return files

        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise GitHubAPIError(f"Failed to fetch repository files: {str(e)}")

    async def get_file_content(self, repo_url: HttpUrl, file_path: str) -> str:
        try:
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.client.get_repo(f"{owner}/{repo_name}")

            file_content = repo.get_contents(file_path)
            if isinstance(file_content, list):
                raise GitHubAPIError(f"Path {file_path} is a directory")

            return file_content.decoded_content.decode('utf-8')

        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise GitHubAPIError(f"Failed to fetch file content: {str(e)}")

    async def get_repository_info(self, repo_url: HttpUrl) -> Dict[str, str]:
        try:
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.client.get_repo(f"{owner}/{repo_name}")

            return {
                "name": repo.name,
                "description": repo.description or "",
                "default_branch": repo.default_branch,
                "language": repo.language or "",
                "size": repo.size,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat()
            }

        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise GitHubAPIError(f"Failed to fetch repository info: {str(e)}")

    @staticmethod
    def _parse_github_url(url: HttpUrl) -> tuple[str, str]:
        try:
            path = urlparse(str(url)).path.strip("/")
            owner, repo = path.split("/")[:2]
            return owner, repo
        except Exception as e:
            raise ValueError(f"Invalid GitHub repository URL: {url}. Error: {str(e)}")


def get_github_service() -> GitHubService:
    return GitHubService()
