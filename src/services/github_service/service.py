from typing import List
from urllib.parse import urlparse

from github import Github, GithubException, Auth
from loguru import logger
from pydantic import HttpUrl

from src.core.exceptions import GitHubAPIError
from src.services.github_service.config import get_github_service_settings
from src.services.github_service.schemas import CodeFile

settings = get_github_service_settings()


class GitHubService:

    def __init__(self):
        self.client = Github(auth=Auth.Token(settings.TOKEN))
        self.supported_extensions = settings.SUPPORTED_EXTENSIONS
        self.review_all = settings.REVIEW_ALL_FILES
        self.max_file_size = settings.MAX_FILE_SIZE

    async def get_repository_files(self, repo_url: HttpUrl) -> List[CodeFile]:
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
                    continue
                if not self.review_all and not any(
                    file_content.path.endswith(ext)
                    for ext in self.supported_extensions
                ):
                    logger.warning(f"Skipping file {file_content.path}"
                                   f"due to unsupported extension")
                    continue
                if file_content.size > self.max_file_size:
                    logger.warning(
                        f"Skipping {file_content.path}: file too large "
                        f"({file_content.size} bytes)")
                    continue
                try:
                    curr_file_content = file_content.decoded_content.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(
                        f"Skipping {file_content.path}: unable to decode content")
                    continue
                files.append(
                    CodeFile(
                        path=file_content.path,
                        size=file_content.size,
                        type="file",
                        url=file_content.url,
                        content=curr_file_content
                    )
                )
            logger.info(f"Found {len(files)} files in {repo_url}")
            logger.info(f"Files: {[file.path for file in files]}")
            return files

        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise GitHubAPIError(f"Failed to fetch repository files: {str(e)}")

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
