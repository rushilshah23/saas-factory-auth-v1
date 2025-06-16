from src.db import SessionDependency
from src.db import SessionDependency
from src.helpers.status_codes import StatusCodes
from src.configs.secrets import SecretUtils
from httpx import AsyncClient
from fastapi import HTTPException
from src.helpers.response import APIResponse
from .utils import Utils
from src.auth.socials.repository import SocialAuthRepository
from src.auth.helpers import UserAuthType
from src.auth.domain import GlobalUserDomain
from .domain import GoogleUserDomain
from src.auth.socials.domain import SocialUserDomain
from src.utils.misc import MiscUtils
from .repository import GoogleUserRepository
from src.auth.repository import GlobalUserRepository
from src.utils.jwt import JWTUtils
from src.helpers.token import GoogleUserTokenPayload, UserTokenPayload, TokenEnum
class Service:

    @staticmethod
    async def auth_callback(code:str, session:SessionDependency) -> APIResponse:
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
            
            if response.status_code != StatusCodes.HTTP_200_OK.value:
                raise HTTPException(status_code=StatusCodes.HTTP_400_BAD_REQUEST.value, detail="Failed to get access token")
            
            tokens = response.json()
            google_access_token = tokens["access_token"]
            id_token = tokens["id_token"]


            user_info = await Utils.get_google_user_info(google_access_token)

            # Find or create user
            google_create_user_service_response:APIResponse[GoogleUserDomain|None] = await Service.find_or_create_google_user(user_info, session)
            if google_create_user_service_response.status in [StatusCodes.HTTP_201_CREATED,StatusCodes.HTTP_200_OK]:
                google_user_domain = google_create_user_service_response.data
                if google_user_domain is None:
                    return APIResponse(
                        data=google_create_user_service_response.data,
                        message=google_create_user_service_response.message,
                        status=google_create_user_service_response.status
                    )
                social_user_repository_response = await SocialAuthRepository.get_user_by_social_user_id(social_user_id=google_user_domain.social_user_id,session=session)
                if social_user_repository_response.status != StatusCodes.HTTP_200_OK or social_user_repository_response.data is None:
                    return APIResponse(
                        message = social_user_repository_response.message,
                        status=social_user_repository_response.status,
                        data=social_user_repository_response.data
                    )
                google_user_token_payload = GoogleUserTokenPayload.from_dict(
                    {
                        "token_type":TokenEnum.ACCESS_TOKEN.value,
                        "is_active":True,
                        "global_user_id":social_user_repository_response.data.global_user_id,
                        "exp":None,
                        "email":google_user_domain.email,
                        "user_type":UserAuthType.GOOGLE.value,
                        "provider_user_id":google_user_domain.provider_user_id
                    }
                )
                access_token = JWTUtils.generate_access_token(payload=google_user_token_payload)

                refresh_token = JWTUtils.generate_refresh_token(payload=google_user_token_payload)

                return APIResponse(
                    data={
                        "tokens":{

                        "access_token":access_token,
                        "access_token_expiry":SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_SECONDS),
                        "refresh_token":refresh_token,
                        "refresh_token_expiry":SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_SECONDS)

                        }
                    },
                    message="Google user tokens generated !",
                    status=StatusCodes.HTTP_201_CREATED
                )
            else:
                return APIResponse(
                    message=google_create_user_service_response.message,
                    data=google_create_user_service_response.data,
                    status=google_create_user_service_response.status
                )
                


    @staticmethod
    async def find_or_create_google_user(user_info: dict, session: SessionDependency) -> APIResponse[GoogleUserDomain|None]:
        email = user_info["email"]
        google_id = user_info["sub"]
        from src.auth.service import GlobalUserService

        # First, check if a global user already exists for this email
        global_user_response: APIResponse[GlobalUserDomain | None] = await GlobalUserService.get_email_globally(email=email,session=session)

        if global_user_response.status == StatusCodes.HTTP_200_OK and global_user_response.data:
            global_user = global_user_response.data
        else:
            # If not found, create a new global user
            global_user = GlobalUserDomain.from_dict({
                "id": MiscUtils.generate_uuid(),
                "user_auth_type": UserAuthType.GOOGLE.value,
                "is_active": True,
                "last_login": None,
                "created_at": MiscUtils.get_current_timestamp()
            })
            create_global_user_response = await GlobalUserRepository.create(obj=global_user, session=session)
            if create_global_user_response.status != StatusCodes.HTTP_201_CREATED or not create_global_user_response.data:
                await session.rollback()
                return APIResponse(
                    data=None,
                    message=create_global_user_response.message,
                    status=create_global_user_response.status
                )
            global_user = create_global_user_response.data

        # Create SocialUser
        social_user_id = MiscUtils.generate_uuid()
        social_user = SocialUserDomain.from_dict({
            "id": social_user_id,
            "provider_user_id": google_id,
            "global_user_id": global_user.id,
            "provider": UserAuthType.GOOGLE.value
        })
        social_user_response = await SocialAuthRepository.create(data=social_user, session=session)
        if social_user_response.status not in [StatusCodes.HTTP_201_CREATED, StatusCodes.HTTP_200_OK] or not social_user_response.data:
            await session.rollback()
            return APIResponse(
                data=None,
                message=social_user_response.message,
                status=social_user_response.status
            )

        # Create GoogleUser
        google_user = GoogleUserDomain.from_dict({
            "id": google_id,
            "social_user_id": social_user_id,
            "provider_user_id": google_id,
            "email": email
        })
        google_user_response = await GoogleUserRepository.create_google_user(data=google_user, session=session)

        if google_user_response.status == StatusCodes.HTTP_201_CREATED:
            await session.commit()
        else:
            await session.rollback()

        return APIResponse(
            data=google_user_response.data,
            message=google_user_response.message,
            status=google_user_response.status
        )












# from src.db import SessionDependency
# from src.helpers.status_codes import StatusCodes
# from src.configs.secrets import SecretUtils
# from httpx import AsyncClient, HTTPError
# from fastapi import HTTPException
# from src.helpers.response import APIResponse
# from .utils import Utils
# from src.auth.socials.repository import SocialAuthRepository
# from src.auth.helpers import UserAuthType
# from src.auth.domain import GlobalUserDomain
# from .domain import GoogleUserDomain
# from src.auth.socials.domain import SocialUserDomain
# from src.utils.misc import MiscUtils
# from .repository import GoogleUserRepository
# from src.auth.repository import GlobalUserRepository
# from src.utils.jwt import JWTUtils
# from src.helpers.token import GoogleUserTokenPayload, TokenEnum


# class Service:
#     # Cache secrets at class level
#     GOOGLE_CLIENT_ID = SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_CLIENT_ID)
#     GOOGLE_CLIENT_SECRET = SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_CLIENT_SECRET)
#     GOOGLE_REDIRECT_URI = SecretUtils.get_secret_value(SecretUtils.SECRETS.GOOGLE_REDIRECT_URI)

#     @staticmethod
#     async def auth_callback(code: str, session: SessionDependency) -> APIResponse:
#         try:
#             async with AsyncClient(timeout=10) as client:
#                 token_data = {
#                     "code": code,
#                     "client_id": Service.GOOGLE_CLIENT_ID,
#                     "client_secret": Service.GOOGLE_CLIENT_SECRET,
#                     "redirect_uri": Service.GOOGLE_REDIRECT_URI,
#                     "grant_type": "authorization_code"
#                 }
#                 response = await client.post("https://oauth2.googleapis.com/token", data=token_data)

#                 if response.status_code != StatusCodes.HTTP_200_OK.value:
#                     return APIResponse(
#                         message="Failed to get access token from Google",
#                         status=StatusCodes.HTTP_400_BAD_REQUEST
#                     )

#                 tokens = response.json()
#                 google_access_token = tokens.get("access_token")
#                 if not google_access_token:
#                     return APIResponse(
#                         message="Access token missing in Google response",
#                         status=StatusCodes.HTTP_400_BAD_REQUEST
#                     )

#                 user_info = await Utils.get_google_user_info(google_access_token)
                
#         except HTTPError as e:
#             return APIResponse(
#                 message=f"Error connecting to Google: {str(e)}",
#                 status=StatusCodes.HTTP_503_SERVICE_UNAVAILABLE
#             )
#         except Exception as e:
#             return APIResponse(
#                 message=f"Unexpected error: {str(e)}",
#                 status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#         # Find or create user
#         google_create_response = await Service.find_or_create_google_user(user_info, session)
#         if not google_create_response.data or google_create_response.data not in [StatusCodes.HTTP_200_OK, StatusCodes.HTTP_201_CREATED] :
#             return google_create_response

#         google_user = google_create_response.data

#         # Get social user
#         social_user_response = await SocialAuthRepository.get_user_by_social_user_id(
#             social_user_id=google_user.social_user_id, session=session
#         )
#         if social_user_response.status != StatusCodes.HTTP_200_OK or not social_user_response.data:
#             return APIResponse(
#                 message="Social user retrieval failed",
#                 status=StatusCodes.HTTP_400_BAD_REQUEST,
#                 data=None
#             )

#         # Create JWT tokens
#         payload_dict = {
#             "token_type": TokenEnum.ACCESS_TOKEN.value,
#             "is_active": True,
#             "global_user_id": social_user_response.data.global_user_id,
#             "exp": MiscUtils.get_jwt_expiry_timestamp(),
#             "email": google_user.email,
#             "user_type": UserAuthType.GOOGLE.value,
#             "provider_user_id": google_user.provider_user_id
#         }

#         google_user_token_payload = GoogleUserTokenPayload.from_dict(payload_dict)
#         access_token = JWTUtils.generate_access_token(google_user_token_payload)
#         refresh_token = JWTUtils.generate_refresh_token(google_user_token_payload)

#         return APIResponse(
#             data={
#                 "access_token": access_token,
#                 "refresh_token": refresh_token
#             },
#             message="Google user tokens generated!",
#             status=StatusCodes.HTTP_200_OK
#         )

#     @staticmethod
#     async def find_or_create_google_user(user_info: dict, session: SessionDependency) -> APIResponse[GoogleUserDomain | None]:
#         email = user_info.get("email")
#         google_id = user_info.get("sub")

#         if not email or not google_id:
#             return APIResponse(
#                 data=None,
#                 message="Invalid user info received from Google",
#                 status=StatusCodes.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # Check if Google user already exists
#             existing_google_user = await GoogleUserRepository.get_user_by_google_user_id(google_id, session=session)
#             if existing_google_user:
#                 return APIResponse(
#                     data=existing_google_user,
#                     message="Google user already exists",
#                     status=StatusCodes.HTTP_200_OK
#                 )

#             async with session.begin():
#                 # Check or create global user
#                 from src.auth.service import GlobalUserService

#                 global_user_response = await GlobalUserService.get_email_globally(email=email, session=session)
#                 if global_user_response.status == StatusCodes.HTTP_200_OK and global_user_response.data:
#                     global_user = global_user_response.data
#                 else:
#                     global_user = GlobalUserDomain.from_dict({
#                         "id": MiscUtils.generate_uuid(),
#                         "user_auth_type": UserAuthType.GOOGLE.value,
#                         "is_active": True,
#                         "last_login": None,
#                         "created_at": MiscUtils.get_current_timestamp()
#                     })
#                     create_global = await GlobalUserRepository.create(global_user, session=session)
#                     if create_global.status != StatusCodes.HTTP_201_CREATED:
#                         raise Exception(create_global.message)
#                     global_user = create_global.data

#                 # Create social user
#                 social_user_id = MiscUtils.generate_uuid()
#                 social_user = SocialUserDomain.from_dict({
#                     "id": social_user_id,
#                     "provider_user_id": google_id,
#                     "global_user_id": global_user.id,
#                     "provider": UserAuthType.GOOGLE.value
#                 })
#                 social_user_response = await SocialAuthRepository.create(social_user, session=session)
#                 if social_user_response.status != StatusCodes.HTTP_201_CREATED:
#                     raise Exception(social_user_response.message)

#                 # Create Google user
#                 google_user = GoogleUserDomain.from_dict({
#                     "id": google_id,
#                     "social_user_id": social_user_id,
#                     "provider_user_id": google_id,
#                     "email": email
#                 })
#                 google_user_response = await GoogleUserRepository.create_google_user(google_user, session=session)
#                 if google_user_response.status != StatusCodes.HTTP_201_CREATED:
#                     raise Exception(google_user_response.message)

#                 return APIResponse(
#                     data=google_user_response.data,
#                     message="Google user created",
#                     status=StatusCodes.HTTP_201_CREATED
#                 )

#         except Exception as e:
#             await session.rollback()
#             return APIResponse(
#                 data=None,
#                 message=f"Error creating Google user: {str(e)}",
#                 status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR
#             )
