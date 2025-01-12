from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List


class CandidateLevel(str, Enum):
    JUNIOR = "Junior"
    MIDDLE = "Middle"
    SENIOR = "Senior"


class CodeReviewRequest(BaseModel):
    assignment_description: str = Field(
        min_length=10,
        max_length=10000,
        description="Detailed description of the programming assignment"
    )
    github_repo_url: HttpUrl = Field(
        description="URL of the GitHub repository to review"
    )
    candidate_level: CandidateLevel = Field(
        description="Level of the candidate (Junior/Middle/Senior)"
    )

    @field_validator('assignment_description')
    def validate_description(cls, value: str) -> str:
        if len(value.split()) < 3:
            raise ValueError("Assignment description must be at least 3 words")
        return value

    @field_validator('github_repo_url')
    def validate_github_url(cls, value: HttpUrl) -> HttpUrl:
        url_str = str(value)
        if not url_str.startswith(('https://github.com/', 'http://github.com/')):
            raise ValueError("URL must be a GitHub repository URL")
        return value

    @field_validator('candidate_level')
    def validate_candidate_level(cls, value: str) -> str:
        if value not in [level.value for level in CandidateLevel]:
            raise ValueError(
                f"Candidate level must be one of: "
                f"{', '.join([level.value for level in CandidateLevel])}"
            )
        return value


class CodeReviewResponse(BaseModel):
    found_files: List[str] = Field(
        default_factory=list,
        description="List of files found and analyzed in repository",
    )
    ai_review_result: str = Field(
        description="Detailed AI review result with analysis and recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "found_files": ["main.py", "tests/test_main.py"],
                "ai_review_result": "Comprehensive code review with "
                                    "specific recommendations..."
            }
        }


class ErrorResponse(BaseModel):
    detail: str = Field(
        description="Error message"
    )
