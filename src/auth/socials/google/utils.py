from fastapi import HTTPException
from httpx import AsyncClient
from src.helpers.status_codes import StatusCodes



class Utils:
    @staticmethod    
    async def get_google_user_info(access_token: str) -> dict:
        async with AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != StatusCodes.HTTP_200_OK:
                raise HTTPException(status_code=StatusCodes.HTTP_400_BAD_REQUEST.value, detail="Invalid access token")
            return response.json()