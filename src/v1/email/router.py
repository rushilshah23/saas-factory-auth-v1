from fastapi import APIRouter
from .helpers import RegisterEmailRequest, LoginEmailRequest
from .service import Service
from src.helpers.response import APIResponse
from fastapi.responses import JSONResponse
from src.db import SessionDependency
router = APIRouter(tags=["Email"])

@router.post("/register")
async def register(request:RegisterEmailRequest, session: SessionDependency) -> APIResponse:
    service_response = await Service.register(request,session)
    return JSONResponse(
        status_code=service_response.status,
        content=service_response.to_dict()
    )

