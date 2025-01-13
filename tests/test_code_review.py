import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from src.main import app
from src.schemas.code_review import CodeReviewRequest, CandidateLevel


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_review_code_success(
    client,
    github_service_settings,
    ai_service_settings,
    mock_code_files,
    mock_response,
    monkeypatch
):
    async def mock_get_files(*args, **kwargs):
        return mock_code_files

    async def mock_send_message(self, messages):
        return "Code review result"

    monkeypatch.setattr(
        "src.services.github_service.service.GitHubService.get_repository_files",
        mock_get_files
    )
    monkeypatch.setattr(
        "src.services.ai_service.service.AIService.send_message",
        mock_send_message
    )

    response = client.post(
        "/code-review/review",
        json={
            "assignment_description": "Create a REST API with FastAPI",
            "github_repo_url": "https://github.com/test/test",
            "candidate_level": "Middle"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "found_files" in data
    assert "ai_review_result" in data
    assert data["ai_review_result"] == "Code review result"
    assert len(data["found_files"]) == len(mock_code_files)
    assert all(file in data["found_files"] for file in ["test.py", "main.py"])


@pytest.mark.asyncio
async def test_review_code_github_error(
    client,
    github_service_settings,
    ai_service_settings,
    monkeypatch
):
    async def mock_error(*args, **kwargs):
        raise ValueError("GitHub API Error")

    monkeypatch.setattr(
        "src.services.github_service.service.GitHubService.get_repository_files",
        mock_error
    )

    response = client.post(
        "/code-review/review",
        json={
            "assignment_description": "Create a REST API with FastAPI",
            "github_repo_url": "https://github.com/test/test",
            "candidate_level": "Middle"
        }
    )

    assert response.status_code == 500
    assert "Failed to process code review" in response.json()["detail"]


@pytest.mark.asyncio
async def test_review_code_ai_error(
    client,
    github_service_settings,
    ai_service_settings,
    mock_code_files,
    monkeypatch
):
    async def mock_get_files(*args, **kwargs):
        return mock_code_files

    async def mock_ai_error(*args, **kwargs):
        raise ValueError("OpenAI API Error")

    monkeypatch.setattr(
        "src.services.github_service.service.GitHubService.get_repository_files",
        mock_get_files
    )
    monkeypatch.setattr(
        "src.services.ai_service.service.AIService.send_code_review_message",
        mock_ai_error
    )

    response = client.post(
        "/code-review/review",
        json={
            "assignment_description": "Create a REST API with FastAPI",
            "github_repo_url": "https://github.com/test/test",
            "candidate_level": "Middle"
        }
    )

    assert response.status_code == 500
    assert "Failed to process code review" in response.json()["detail"]


@pytest.mark.asyncio
async def test_review_code_invalid_request(client):
    response = client.post(
        "/code-review/review",
        json={
            "assignment_description": "hi",
            "github_repo_url": "https://github.com/test/test",
            "candidate_level": "Middle"
        }
    )

    assert response.status_code == 422
    assert "string should have at least 10 characters" in response.json()["detail"][0]["msg"].lower()


def test_valid_code_review_request():
    valid_data = {
        "assignment_description": "Create a REST API with FastAPI and PostgreSQL",
        "github_repo_url": "https://github.com/username/repo",
        "candidate_level": "Middle"
    }
    request = CodeReviewRequest(**valid_data)
    assert request.assignment_description == valid_data["assignment_description"]
    assert str(request.github_repo_url) == valid_data["github_repo_url"]
    assert request.candidate_level == valid_data["candidate_level"]


def test_assignment_description_validation():
    with pytest.raises(ValidationError) as exc_info:
        CodeReviewRequest(
            assignment_description="Hi there",
            github_repo_url="https://github.com/username/repo",
            candidate_level="Middle"
        )
    assert "String should have at least" in str(exc_info.value)

    with pytest.raises(ValidationError):
        CodeReviewRequest(
            assignment_description="",
            github_repo_url="https://github.com/username/repo",
            candidate_level="Middle"
        )

    long_description = "test " * 2501
    with pytest.raises(ValidationError):
        CodeReviewRequest(
            assignment_description=long_description,
            github_repo_url="https://github.com/username/repo",
            candidate_level="Middle"
        )


def test_github_url_validation():
    with pytest.raises(ValidationError):
        CodeReviewRequest(
            assignment_description="Create a REST API with FastAPI",
            github_repo_url="not_a_url",
            candidate_level="Middle"
        )

    with pytest.raises(ValidationError) as exc_info:
        CodeReviewRequest(
            assignment_description="Create a REST API with FastAPI",
            github_repo_url="https://gitlab.com/username/repo",
            candidate_level="Middle"
        )
    assert "URL must be a GitHub repository URL" in str(exc_info.value)

    valid_urls = [
        "https://github.com/username/repo",
        "http://github.com/username/repo-name",
        "https://github.com/org/repo-with-hyphens"
    ]
    for url in valid_urls:
        request = CodeReviewRequest(
            assignment_description="Create a REST API with FastAPI",
            github_repo_url=url,
            candidate_level="Middle"
        )
        assert str(request.github_repo_url) == url


def test_candidate_level_validation():
    with pytest.raises(ValidationError) as exc_info:
        CodeReviewRequest(
            assignment_description="Create a REST API with FastAPI",
            github_repo_url="https://github.com/username/repo",
            candidate_level="Expert"
        )
    assert "Input should be" in str(exc_info.value)

    valid_levels = [level.value for level in CandidateLevel]
    for level in valid_levels:
        request = CodeReviewRequest(
            assignment_description="Create a REST API with FastAPI",
            github_repo_url="https://github.com/username/repo",
            candidate_level=level
        )
        assert request.candidate_level == level


def test_request_creation_with_spaces():
    request = CodeReviewRequest(
        assignment_description="  Create a REST API with FastAPI  ",
        github_repo_url="  https://github.com/username/repo  ",
        candidate_level="  Middle  "
    )
    assert request.assignment_description == "  Create a REST API with FastAPI  "
    assert str(request.github_repo_url) == "https://github.com/username/repo"
    assert request.candidate_level == "Middle"