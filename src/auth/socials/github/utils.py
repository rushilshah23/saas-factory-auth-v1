from fastapi import HTTPException
from httpx import AsyncClient
from src.helpers.status_codes import StatusCodes

class Utils:
    @staticmethod    
    async def get_github_user_info(access_token: str) -> dict:
        async with AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != StatusCodes.HTTP_200_OK.value:
                print(response.text)
                raise HTTPException(
                    status_code=StatusCodes.HTTP_400_BAD_REQUEST.value,
                    detail="Invalid access token"
                )
            
            user_data = response.json()

            # Optionally fetch email if not public
            if not user_data.get("email"):
                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if email_response.status_code == StatusCodes.HTTP_200_OK.value:
                    emails = email_response.json()
                    primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                    user_data["email"] = primary_email
            
            return user_data
