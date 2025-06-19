from fastapi import APIRouter, FastAPI
from .google.router import router as google_router
from .github.router import router as github_router

social_router  = APIRouter(tags=["Social Authentication"])


social_router.include_router(router=google_router, prefix="/google")
social_router.include_router(router=github_router, prefix="/github")




