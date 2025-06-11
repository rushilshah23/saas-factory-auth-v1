from src.utils import Utils as AppUtils
from src.helpers.response import APIResponse
from fastapi import HTTPException, Request
from src.helpers.response import APIResponse
class Service:

    async def authenticate(request:Request):
        token = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            token = request.cookies.get("access_token")

        if not token:
            raise HTTPException(status_code=401, detail="Missing access token")

        payload = await AppUtils.verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return APIResponse(
            status=200,
            message="User authenticated successfully",
            data={
                "user_id": payload.get("user_id"),
                "email": payload.get("email")
            }
        )