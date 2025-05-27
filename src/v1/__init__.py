

from .email import router as email_router



from fastapi import APIRouter


v1_router = APIRouter(tags=["v1"] ,prefix="/v1")


v1_router.include_router(email_router)

__all__ = (
    v1_router
)
