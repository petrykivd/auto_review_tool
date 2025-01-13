import pytest


class MockFileContent:
    def __init__(self, path: str, size: int, content: str, is_dir: bool = False):
        self.path = path
        self.size = size
        self.type = "dir" if is_dir else "file"
        self.url = f"https://api.github.com/repos/test/test/contents/{path}"
        self._content = content

    @property
    def decoded_content(self):
        return self._content.encode('utf-8')


class MockRepo:
    def __init__(self, files):
        self.files = files
        self.contents_calls = []

    def get_contents(self, path=""):
        self.contents_calls.append(path)
        matching_files = []
        for file in self.files:
            if path == "":
                if "/" not in file.path:
                    matching_files.append(file)
            elif file.path.startswith(path + "/"):
                remaining_path = file.path[len(path) + 1:]
                if "/" not in remaining_path:
                    matching_files.append(file)
        return matching_files


@pytest.fixture
def github_service_settings(monkeypatch):
    class Settings:
        TOKEN = "test_token"
        SUPPORTED_EXTENSIONS = [".py", ".js"]
        REVIEW_ALL_FILES = False
        MAX_FILE_SIZE = 1000000

    monkeypatch.setattr(
        "src.services.github_service.service.settings",
        Settings()
    )
    return Settings()


@pytest.fixture
def ai_service_settings(monkeypatch):
    class Settings:
        API_KEY = "test-key"
        MODEL = "gpt-4-turbo"

    monkeypatch.setattr(
        "src.services.ai_service.service.settings",
        Settings()
    )
    return Settings()


@pytest.fixture
def mock_response():
    class MockResponse:
        class Choice:
            class Message:
                content = "Code review result"

            message = Message()

        choices = [Choice()]

    class MockCompletions:
        @staticmethod
        async def create(**kwargs):
            return MockResponse()

    class MockChat:
        completions = MockCompletions()

    class MockClient:
        chat = MockChat()

    return MockClient()


@pytest.fixture
def mock_code_files():
    from src.services.github_service.schemas import CodeFile

    return [
        CodeFile(
            path="test.py",
            size=100,
            type="file",
            url="https://github.com/test/test.py",
            content="def test_hello_world():\n    pass"
        ),
        CodeFile(
            path="main.py",
            size=200,
            type="file",
            url="https://github.com/test/main.py",
            content="def main():\n    pass"
        )
    ]
