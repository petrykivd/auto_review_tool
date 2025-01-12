from fastapi import FastAPI

from src.core.config import get_settings
from src.api.routes.code_review import router as code_review_router
settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(code_review_router)
