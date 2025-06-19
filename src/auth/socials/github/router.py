from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from src.db import SessionDependency
from src.helpers.status_codes import StatusCodes
from src.configs.secrets import SecretUtils
from src.utils.cookie import CookieUtils
from src.helpers.token import TokenEnum
from .service import Service

router = APIRouter(tags=["Social - Github"])

@router.get("/login/github")
async def login_github() -> JSONResponse:
    client_id = SecretUtils.get_secret_value(SecretUtils.SECRETS.GITHUB_CLIENT_ID)
    redirect_uri = SecretUtils.get_secret_value(SecretUtils.SECRETS.GITHUB_REDIRECT_URI)

    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=read:user user:email"
    )
    

    return JSONResponse(content={"url": url})

@router.get("/callback")
async def auth_github_callback(request: Request, code: str, session: SessionDependency):
    service_response = await Service.auth_callback(code, session)

    # Determine frontend URL (e.g. your app's dashboard or login success page)
    frontend_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.SERVER_BASE_URL)

    if service_response.status == StatusCodes.HTTP_201_CREATED:
        tokens = service_response.data.get("tokens")
        # Redirect with cookies for web
        redirect_response = RedirectResponse(url=frontend_url)

        CookieUtils.set_cookie(
            redirect_response,
            TokenEnum.ACCESS_TOKEN.value,
            tokens.get("access_token"),
            expires=int(tokens.get("access_token_expiry")),
        )
        CookieUtils.set_cookie(
            redirect_response,
            TokenEnum.REFRESH_TOKEN.value,
            tokens.get("refresh_token"),
            expires=int(tokens.get("refresh_token_expiry")),
        )


        return redirect_response

    # If token generation failed, just redirect to frontend without cookies
    return RedirectResponse(url=frontend_url)

@router.get("/success")
async def github_success(
    access: str,
    refresh: str,
    access_token_expiry: int,
    refresh_token_expiry: int,
):
    # OPTIONAL: Provide a success endpoint if you want to handle token setting via frontend
    response = RedirectResponse(
        url=SecretUtils.get_secret_value(SecretUtils.SECRETS.SERVER_BASE_URL)
    )

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
