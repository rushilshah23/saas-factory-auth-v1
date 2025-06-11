from fastapi import APIRouter
from .helpers import (
    RegisterEmailRequest,
    LoginEmailRequest,
    # VerifyEmailRequest,
    # ForgotPasswordRequest,
    # ResetPasswordRequest,
    # LogoutRequest
)
from .service import Service
from src.helpers.response import APIResponse
from fastapi.responses import JSONResponse
from src.db import SessionDependency

router = APIRouter(tags=["Email"], prefix="/email")

@router.post("/register")
async def register(request: RegisterEmailRequest, session: SessionDependency) -> APIResponse:
    service_response = await Service.register(request, session)
    return JSONResponse(
        status_code=service_response.status,
        content=service_response.to_dict()
    )

@router.get("/verify-email")
async def verify_user(token: str, session: SessionDependency) -> APIResponse:
    service_response = await Service.verify_user(token, session)
    return JSONResponse(
        status_code=service_response.status,
        content=service_response.to_dict()
    )

@router.post("/login")
async def login(request: LoginEmailRequest, session: SessionDependency) -> APIResponse:
    service_response = await Service.login(request, session)
    response =  JSONResponse(
        status_code=service_response.status,
        content=service_response.to_dict()
    )
    if service_response.status == 200:
        # set in cookie
        response.set_cookie(
            key="access_token",
            value=service_response.data.get("access_token"),
            httponly=True,
            secure=True,
            samesite="Lax",
            expires=service_response.data.get("expires_in")
        )
    return response





# @router.post("/forgot-password")
# async def forgot_password(request: ForgotPasswordRequest, session: SessionDependency) -> APIResponse:
#     service_response = await Service.forgot_password(request, session)
#     return JSONResponse(
#         status_code=service_response.status,
#         content=service_response.to_dict()
#     )

# @router.post("/reset-password")
# async def reset_password(request: ResetPasswordRequest, session: SessionDependency) -> APIResponse:
#     service_response = await Service.reset_password(request, session)
#     return JSONResponse(
#         status_code=service_response.status,
#         content=service_response.to_dict()
#     )

# @router.post("/logout")
# async def logout(request: LogoutRequest, session: SessionDependency) -> APIResponse:
#     service_response = await Service.logout(request, session)
#     return JSONResponse(
#         status_code=service_response.status,
#         content=service_response.to_dict()
#     )