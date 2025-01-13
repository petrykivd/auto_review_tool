from typing import List

from src.services.github_service.schemas import CodeFile


class CodeReviewPrompts:
    SYSTEM_MESSAGE = """
    You are a code review assistant for a Python project.
    Analyze the repository provided using the following details:
    Downsides:
    - {Observation_1}
    - {Observation_2}

    Rating: {Score}/5 (for {Candidate_Level})

    Conclusion:
    {Summary_Of_Performance}
    """

    @staticmethod
    def generate_review_prompt(
        code_files: List[CodeFile],
        assignment_description: str,
        candidate_level: str
    ) -> str:
        files_content = "\n\n".join(
            f"File: {file.path}\n```\n{file.content}\n```"
            for file in code_files
        )

        return f"""
            Please review the following code for a {candidate_level} level candidate.

            Assignment Description:
            {assignment_description}

            Code Files:
            {files_content}
            """
