# AI Code Reviewer

AI-powered code review tool that analyzes GitHub repositories and provides detailed feedback based on code quality, best practices, and candidate level.

## Features

- Automatic code review for GitHub repositories
- Customizable review criteria based on candidate level (Junior/Middle/Senior)
- Integration with OpenAI GPT for intelligent analysis
- Redis caching for improved performance
- Docker support for easy deployment

## Requirements

- Python 3.10 or higher
- Poetry for dependency management
- GitHub API token
- OpenAI API key
- Docker and Docker Compose (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/petrykivd/auto_review_tool.git
cd auto_review_tool
```

2. Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

Required environment variables:
```env
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_api_key_here
```
Other variables are specified in .env.example and are optional

## Usage

1. **Run the application:**
<br>
   You can use the commands described below or use the Makefile
<details>
<summary>🚀 Option 1: Docker Setup (with Redis)</summary>

### Docker setup
Run `docker compose up`
</details>
<br>
<details>
<summary>💻 Option 2: Local Setup (without Redis)</summary>

### Local setup without Redis
1. Run `poetry install`
2. Run `poetry run uvicorn src.main:app --reload`
</details>
<br>
<details>
<summary>🔧 Option 3: Makefile</summary>

### Makefile
Run `make run`
</details>


2. Send a POST request to `/code-review/review` endpoint:
```json
{
    "assignment_description": "Create a REST API using FastAPI",
    "github_repo_url": "https://github.com/username/repo",
    "candidate_level": "Junior"
}
```

3. The API will return a detailed review including:
- List of analyzed files
- Review from AI in text format

## Development

### Running Tests
```bash
poetry run pytest
```
or
```bash
make test
```

### Linting
```bash
poetry run flake8 src
```
or
```bash
make lint
```
### Test Coverage
```bash
poetry run pytest --cov=src tests/ --cov-report=html
```
or
```bash
make coverage-html
```

## Future Improvements
Regarding scaling this system, I see several important points we can improve. First, when working with GitHub API, it would be cool to make batch requests instead of separate requests for each file, and process them in parallel. Of course, we'll need to improve the rate limiting system to avoid exceeding API limits.
For large repositories, we can take a smart approach: split them into smaller parts and process them in parallel. By the way, we might not need to analyze all the code - we can first identify the main files worth checking (using file names and also through AI).
For the AI part, we can go several ways. To start with, we can use powerful models through AWS (higher limits) and other LLM services. We can also set up a fallback mechanism that will allow us to use multiple API keys and switch them when limits are exceeded or if a service fails. Also we can use batch requests to AI services.
And of course, we can't do without queues - they'll help manage the load and prevent the system from crashing when lots of requests come in at once.
I think this approach will let our system work fine even under heavy load, while still providing quality code analysis results.
It would be interesting to hear other solutions to these problems too.

<p align="center">
<img style="width: 100%;" src="https://i.postimg.cc/nzykWKNd/result.gif">
</p>