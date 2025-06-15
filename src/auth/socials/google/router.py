from fastapi import BackgroundTasks, APIRouter, Request
from fastapi.responses import JSONResponse
from src.db import SessionDependency
from src.helpers.status_codes import StatusCodes
from src.helpers.response import APIResponse
from src.configs.secrets import SecretUtils
from httpx import AsyncClient
from fastapi import HTTPException
from .service import Service

router = APIRouter(tags=["Social - Google"])

@router.get("/login/google")
async def login_google() -> JSONResponse:
    return JSONResponse(
        content={
            "url":f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_CLIENT_ID)}&redirect_uri={SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_REDIRECT_URI)}&scope=openid%20profile%20email"
        }
    )

@router.get("/callback")
async def auth_google_callback(request:Request, code:str, session: SessionDependency):

    servcie_response = await Service.auth_callback(code,session)

    