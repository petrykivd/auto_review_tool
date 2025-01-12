from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class CandidateLevel(str, Enum):
    JUNIOR = "Junior"
    MIDDLE = "Middle"
    SENIOR = "Senior"


class CodeReviewRequest(BaseModel):
    assignment_description: str = Field(
        description="Description of the programming assignment"
    )
    github_repo_url: HttpUrl = Field(
        description="URL of the GitHub repository to review"
    )
    candidate_level: CandidateLevel = Field(
        description=f"Level of the candidate"
    )


class CodeReviewResponse(BaseModel):
    found_files: list[str] = Field(
        default_factory=list,
        description="List of files found in repository",
    )
    comments: list[str] = Field(
        default_factory=list,
        description="List of review comments and suggestions"
    )
    rating: int = Field(
        ge=1,
        le=10,
        description="Overall rating from 1 to 10"
    )
    conclusion: str = Field(
        description="Summary and recommendations"
    )


class ErrorResponse(BaseModel):
    detail: str = Field(
        description="Error message"
    )
