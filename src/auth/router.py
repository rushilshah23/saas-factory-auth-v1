from fastapi import APIRouter, Depends
from src.auth.service import GlobalUserService
from src.helpers.response import APIResponse
from .email import router as email_router
from .socials import social_router
from fastapi.responses import JSONResponse


router = APIRouter(tags=["Auth"] ,prefix="/auth")


router.include_router(email_router, prefix="/email")
router.include_router(social_router, prefix="/socials")



@router.get("/authenticate")
async def authenticate(authenticated_user = Depends(GlobalUserService.authenticate)):
    return JSONResponse(
        status_code=authenticated_user.status.value,
        
        content=authenticated_user.to_dict()
    )

