from fastapi import APIRouter, Request, BackgroundTasks
from .helpers import (
    RegisterEmailRequest,
    LoginEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)
from .service import Service
from src.v1.service import Service as AppService
from src.helpers.response import APIResponse
from fastapi.responses import JSONResponse
from src.db import SessionDependency
from .utils import Utils
from src.helpers.token import CookieNames
from src.helpers.status_codes import StatusCodes

router = APIRouter(tags=["Email"], prefix="/email")

@router.post("/register")
async def register(request: RegisterEmailRequest, session: SessionDependency, background_tasks:BackgroundTasks) -> APIResponse:
    service_response = await Service.register(request, session,background_tasks=background_tasks)
    return JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )

@router.get("/verify-email")
async def verify_user(token: str, session: SessionDependency) -> APIResponse:
    service_response = await Service.verify_user(token, session)
    return JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )

@router.post("/login")
async def login(request: LoginEmailRequest, session: SessionDependency) -> APIResponse:
    service_response = await Service.login(request, session)
    response =  JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )
    if service_response.status == StatusCodes.HTTP_200_OK:
        print(f"Access expires in: {service_response.data.get('tokens').get('access_token_expiry')}")
        print(f"Refresh expires in: {service_response.data.get('tokens').get('refresh_token_expiry')}")
        # set in cookie
        Utils.set_cookie(response, CookieNames.ACCESS_TOKEN.value, service_response.data.get("tokens").get("access_token"),
                        expires=int(service_response.data.get('tokens').get("access_token_expiry")))

        Utils.set_cookie(response, CookieNames.REFRESH_TOKEN.value, service_response.data.get("tokens").get("refresh_token"),
                        expires=int(service_response.data.get('tokens').get("refresh_token_expiry")))
    elif service_response.status == StatusCodes.HTTP_201_CREATED:
        pass
    else:
        response.delete_cookie(CookieNames.ACCESS_TOKEN.value)
        response.delete_cookie(CookieNames.REFRESH_TOKEN.value)
    return response



@router.post("/refresh-token")
async def refresh_token(request:Request,session: SessionDependency) -> APIResponse:
    service_response = await Service.refresh_token(request, session)
    response = JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )
    if service_response.status == StatusCodes.HTTP_200_OK:
        # set in cookie
        Utils.set_cookie(response, CookieNames.ACCESS_TOKEN.value, service_response.data.get("tokens").get("access_token"),
                        expires=int(service_response.data.get('tokens').get("access_token_expiry")))
        Utils.set_cookie(response,CookieNames.REFRESH_TOKEN.value, service_response.data.get("tokens").get("refresh_token"),
                        expires=int(service_response.data.get('tokens').get("refresh_token_expiry")))
    elif service_response.status == StatusCodes.HTTP_201_CREATED:
        pass
    else:
        response.delete_cookie(CookieNames.ACCESS_TOKEN.value)
        response.delete_cookie(CookieNames.REFRESH_TOKEN.value)

    return response




@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, session: SessionDependency, background_tasks:BackgroundTasks) -> APIResponse:
    service_response = await Service.forgot_password(request, session, background_tasks=background_tasks)
    return JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest,token:str, session: SessionDependency) -> APIResponse:
    service_response = await Service.reset_password(request, token, session)
    return JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )

@router.post("/change-password")
async def change_password(request:Request,data: ChangePasswordRequest, session: SessionDependency) -> APIResponse:

    service_response = await Service.change_password(request,data, session)
    return JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )

@router.post("/logout")
async def logout(request: Request, session: SessionDependency) -> APIResponse:
    service_response = await Service.logout(request, session)
    response  = JSONResponse(
        status_code=service_response.status.value,
        content=service_response.to_dict()
    )
    response.delete_cookie(CookieNames.ACCESS_TOKEN.value)
    response.delete_cookie(CookieNames.REFRESH_TOKEN.value)
    return response