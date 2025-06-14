from fastapi import APIRouter, Depends
from src.v1.service import Service
from src.helpers.response import APIResponse
from .email import router as email_router

from fastapi.responses import JSONResponse













v1_router = APIRouter(tags=["v1"] ,prefix="/v1")


v1_router.include_router(email_router)




@v1_router.get("/authenticate")
async def authenticate(authenticated_user = Depends(Service.authenticate)):
    return JSONResponse(
        status_code=authenticated_user.status.value,
        
        content=authenticated_user.data
    )

