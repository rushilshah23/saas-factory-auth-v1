from fastapi import BackgroundTasks, APIRouter, Request
from fastapi.responses import JSONResponse
from src.db import SessionDependency
from src.helpers.status_codes import StatusCodes
from src.helpers.response import APIResponse
from src.configs.secrets import SecretUtils
from httpx import AsyncClient
from fastapi import HTTPException
from .service import Service
from src.utils.cookie import CookieUtils
from src.helpers.token import TokenEnum
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["Social - Google"])


@router.get("/success")
async def google_success(
    request: Request,
    access: str,
    refresh: str,
    access_token_expiry: int,
    refresh_token_expiry: int
):
    response = RedirectResponse(url="http://127.0.0.1:8000/docs")  # 👈 or your frontend route

    # Set cookies
    CookieUtils.set_cookie(
        response,
        TokenEnum.ACCESS_TOKEN.value,
        access,
        expires=access_token_expiry,
    )

    CookieUtils.set_cookie(
        response,
        TokenEnum.REFRESH_TOKEN.value,
        refresh,
        expires=refresh_token_expiry,
    )

    return response


@router.get("/login/google")
async def login_google() -> JSONResponse:
    return JSONResponse(
        content={
            "url":f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_CLIENT_ID)}&redirect_uri={SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_REDIRECT_URI)}&scope=openid%20profile%20email"
        }
    )

@router.get("/callback")
async def auth_google_callback(request: Request, code: str, session: SessionDependency):
    service_response = await Service.auth_callback(code, session)

    # Redirect to frontend
    redirect_response = RedirectResponse(url=f"{SecretUtils.get_secret_value(SecretUtils.SECRETS.SERVER_BASE_URL)}")

    if service_response.status == StatusCodes.HTTP_201_CREATED:
        tokens = service_response.data.get("tokens")

        # Set tokens in cookies on this redirect response
        CookieUtils.set_cookie(
            redirect_response,
            TokenEnum.ACCESS_TOKEN.value,
            tokens.get("access_token"),
            expires=int(tokens.get("access_token_expiry"))
        )
        CookieUtils.set_cookie(
            redirect_response,
            TokenEnum.REFRESH_TOKEN.value,
            tokens.get("refresh_token"),
            expires=int(tokens.get("refresh_token_expiry"))
        )

    return redirect_response
    