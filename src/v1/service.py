from src.utils import Utils as AppUtils
from src.helpers.response import APIResponse
from fastapi import HTTPException, Request
from src.helpers.response import APIResponse
from src.helpers.token import CookieNames, TokenPayload
from src.helpers.status_codes import StatusCodes

class Service:

    async def authenticate(request:Request):
        token = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        

        if not token:
            token = request.cookies.get(CookieNames.ACCESS_TOKEN.value)

        if not token:
            raise HTTPException(status_code=StatusCodes.HTTP_401_UNAUTHORIZED.value, detail="Missing access token")

        payload = await AppUtils.verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=StatusCodes.HTTP_401_UNAUTHORIZED.value, detail="Invalid or expired token")

        return APIResponse(
            status=StatusCodes.HTTP_200_OK,
            message="User authenticated successfully",
            data=payload.to_dict()
        )