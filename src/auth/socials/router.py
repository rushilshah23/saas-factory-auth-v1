from fastapi import APIRouter, FastAPI
from .google.router import router as google_router


social_router  = APIRouter(tags=["Social - Google"])


social_router.include_router(router=google_router, prefix="/google")



