import pytest
from github import GithubException
from src.core.exceptions import GitHubAPIError
from src.services.github_service.service import GitHubService
from tests.conftest import MockFileContent, MockRepo


@pytest.fixture
def github_service(github_service_settings):
    return GitHubService()


@pytest.mark.asyncio
async def test_get_repository_files_with_directory(github_service, monkeypatch):
    test_files = [
        MockFileContent("src", 0, "", is_dir=True),
        MockFileContent("src/test.py", 100, "print('test')"),
        MockFileContent("src/nested", 0, "", is_dir=True),
        MockFileContent("src/nested/deep.py", 100, "print('deep')")
    ]
    mock_repo = MockRepo(test_files)

    github_service.client.get_repo = lambda _: mock_repo

    files = await github_service.get_repository_files("https://github.com/test/test")

    assert len(files) == 2
    assert any(f.path == "src/test.py" for f in files)
    assert any(f.path == "src/nested/deep.py" for f in files)
    assert all(f.content in ["print('test')", "print('deep')"] for f in files)


@pytest.mark.asyncio
async def test_skip_unsupported_extensions(github_service, monkeypatch):
    test_files = [
        MockFileContent("test.py", 100, "print('test')"),
        MockFileContent("test.txt", 200, "plain text")
    ]
    mock_repo = MockRepo(test_files)

    github_service.client.get_repo = lambda _: mock_repo

    files = await github_service.get_repository_files("https://github.com/test/test")

    assert len(files) == 1
    assert files[0].path == "test.py"


@pytest.mark.asyncio
async def test_github_api_error(github_service, monkeypatch):
    def raise_error(*args, **kwargs):
        raise GithubException(404, {"message": "Not Found"})

    github_service.client.get_repo = raise_error

    with pytest.raises(GitHubAPIError) as exc_info:
        await github_service.get_repository_files("https://github.com/test/test")
    assert "Failed to fetch repository files" in str(exc_info.value)


@pytest.mark.asyncio
async def test_skip_large_files(github_service, monkeypatch):
    test_files = [
        MockFileContent("test.py", 100, "print('test')"),
        MockFileContent("large.py", 2000000, "large file content")
    ]
    mock_repo = MockRepo(test_files)

    github_service.client.get_repo = lambda _: mock_repo

    files = await github_service.get_repository_files("https://github.com/test/test")

    assert len(files) == 1
    assert files[0].path == "test.py"


@pytest.mark.asyncio
async def test_parse_github_url_invalid():
    service = GitHubService()
    invalid_url = "https://github.com/invalid"

    with pytest.raises(ValueError) as exc_info:
        service._parse_github_url(invalid_url)
    assert "Invalid GitHub repository URL" in str(exc_info.value)