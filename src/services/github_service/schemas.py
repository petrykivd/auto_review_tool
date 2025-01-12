from pydantic import BaseModel


class CodeFile(BaseModel):
    path: str
    content: str
    size: int
    type: str
    url: str
