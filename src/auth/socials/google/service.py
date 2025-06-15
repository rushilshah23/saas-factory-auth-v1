from src.db import SessionDependency
from src.db import SessionDependency
from src.helpers.status_codes import StatusCodes
from src.configs.secrets import SecretUtils
from httpx import AsyncClient
from fastapi import HTTPException
from src.helpers.response import APIResponse
from .utils import Utils
class Service:

    @staticmethod
    async def auth_callback(code:str, session:SessionDependency):
        async with AsyncClient() as client:
            token_data = {
                "code": code,
                "client_id": SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_CLIENT_ID),
                "client_secret":SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_CLIENT_SECRET),
                "redirect_uri": SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_REDIRECT_URI),
                "grant_type": "authorization_code"
            }
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data=token_data
            )
            
            if response.status_code != StatusCodes.HTTP_200_OK:
                raise HTTPException(status_code=StatusCodes.HTTP_400_BAD_REQUEST.value, detail="Failed to get access token")
            
            tokens = response.json()
            access_token = tokens["access_token"]
            id_token = tokens["id_token"]


            user_info = await Utils.get_google_user_info(access_token)
            
            # Find or create user
            user = await Service.find_or_create_google_user(user_info, session)

    # @staticmethod
    # async def find_or_create_google_user(user_info: dict, session: SessionDependency) -> User:
        # email = user_info["email"]
        # google_id = user_info["sub"]
        
        # # Check if social account exists
        # result = await session.execute(
        #     select(SocialAccount)
        #     .where(SocialAccount.provider == "google")
        #     .where(SocialAccount.provider_user_id == google_id)
        # )
        # social_account = result.scalars().first()
        
        # if social_account:
        #     # Get existing user
        #     result = await session.execute(
        #         select(User).where(User.id == social_account.user_id)
        #     )
        #     return result.scalars().first()
        
        # # Check if email exists in users table
        # result = await session.execute(
        #     select(User).where(User.email == email)
        # )
        # existing_user = result.scalars().first()
        
        # if existing_user:
        #     # Link Google account to existing user
        #     new_social_account = SocialAccount(
        #         provider="google",
        #         provider_user_id=google_id,
        #         user_id=existing_user.id
        #     )
        #     session.add(new_social_account)
        #     await session.commit()
        #     return existing_user
        
        # # Create new user
        # new_user = User(
        #     email=email,
        #     full_name=user_info.get("name", ""),
        #     is_active=True,
        #     created_at=datetime.utcnow()
        # )
        # session.add(new_user)
        # await session.flush()  # To get the new user ID
        
        # # Create social account
        # new_social_account = SocialAccount(
        #     provider="google",
        #     provider_user_id=google_id,
        #     user_id=new_user.id
        # )
        # session.add(new_social_account)
        
        # await session.commit()
        # return new_user