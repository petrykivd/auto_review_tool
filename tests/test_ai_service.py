import pytest
from openai import OpenAIError as InternalOpenAIError, AsyncOpenAI
from src.core.exceptions import OpenAIError
from src.services.ai_service.prompts import CodeReviewPrompts
from src.services.ai_service.service import AIService, get_ai_service
from src.services.ai_service.schemas import Message


@pytest.fixture
def ai_service(ai_service_settings):
    return AIService()


@pytest.mark.asyncio
async def test_send_message_success(ai_service, mock_response, monkeypatch):
    monkeypatch.setattr(ai_service, "client", mock_response)

    messages = [
        Message(role="system", content="test system"),
        Message(role="user", content="test user")
    ]

    response = await ai_service.send_message(messages)

    assert response == "Code review result"


@pytest.mark.asyncio
async def test_send_message_api_error(ai_service, monkeypatch):
    class MockCompletions:
        @staticmethod
        async def create(**kwargs):
            raise InternalOpenAIError("API Error")

    class MockChat:
        completions = MockCompletions()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr(ai_service, "client", MockClient())

    messages = [
        Message(role="system", content="test system"),
        Message(role="user", content="test user")
    ]

    with pytest.raises(OpenAIError) as exc_info:
        await ai_service.send_message(messages)
    assert "Failed to get AI response" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_code_review_message(
    ai_service,
    mock_code_files,
    mock_response,
    monkeypatch,
):
    monkeypatch.setattr(ai_service, "client", mock_response)

    response = await ai_service.send_code_review_message(
        code_files=mock_code_files,
        assignment_description="Test assignment",
        candidate_level="Middle",
    )

    assert response == "Code review result"


def test_prepare_message_to_send():
    system_message = "Test system message"
    user_message = "Test user message"

    messages = AIService.prepare_message_to_send(system_message, user_message)

    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[0].content == system_message
    assert messages[1].role == "user"
    assert messages[1].content == user_message


def test_get_ai_service():
    service = get_ai_service()

    assert isinstance(service, AIService)
    assert isinstance(service.client, AsyncOpenAI)
    assert service.model == "gpt-4-turbo"


def test_system_message_format():
    assert "{Observation_1}" in CodeReviewPrompts.SYSTEM_MESSAGE
    assert "{Observation_2}" in CodeReviewPrompts.SYSTEM_MESSAGE
    assert "{Score}" in CodeReviewPrompts.SYSTEM_MESSAGE
    assert "{Candidate_Level}" in CodeReviewPrompts.SYSTEM_MESSAGE
    assert "{Summary_Of_Performance}" in CodeReviewPrompts.SYSTEM_MESSAGE


def test_generate_review_prompt(mock_code_files):
    assignment_description = "Test assignment"
    candidate_level = "Middle"

    prompt = CodeReviewPrompts.generate_review_prompt(
        mock_code_files,
        assignment_description,
        candidate_level
    )

    assert candidate_level in prompt
    assert assignment_description in prompt
    assert "test.py" in prompt
    assert "main.py" in prompt
    assert "def test_hello_world():" in prompt
    assert "def main():" in prompt
    assert "Assignment Description:" in prompt
    assert "Code Files:" in prompt