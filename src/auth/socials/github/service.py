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
from .domain import GithubUserDomain
from src.auth.socials.domain import SocialUserDomain
from src.utils.misc import MiscUtils
from .repository import GithubUserRepository
from src.auth.repository import GlobalUserRepository
from src.utils.jwt import JWTUtils
from src.helpers.token import GithubUserTokenPayload, TokenEnum
from src.helpers.response import RepositoryResponse
class Service:

    @staticmethod
    async def auth_callback(code: str, session: SessionDependency) -> APIResponse:
        async with AsyncClient() as client:
            token_data = {
                "code": code,
                "client_id": SecretUtils.get_secret_value(SecretUtils.SECRETS.GITHUB_CLIENT_ID),
                "client_secret": SecretUtils.get_secret_value(SecretUtils.SECRETS.GITHUB_CLIENT_SECRET),
                "redirect_uri": SecretUtils.get_secret_value(SecretUtils.SECRETS.GITHUB_REDIRECT_URI),
            }
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data=token_data,
                headers={"Accept": "application/json"}
            )

            if response.status_code != StatusCodes.HTTP_200_OK.value:
                raise HTTPException(
                    status_code=StatusCodes.HTTP_400_BAD_REQUEST.value,
                    detail="Failed to get access token"
                )

            tokens = response.json()
            github_access_token = tokens.get("access_token")
            if not github_access_token:
                raise HTTPException(
                    status_code=StatusCodes.HTTP_400_BAD_REQUEST.value,
                    detail="Access token missing in response"
                )

            user_info = await Utils.get_github_user_info(github_access_token)

            github_create_user_service_response: APIResponse[GithubUserDomain | None] = await Service.find_or_create_github_user(user_info, session)
            if github_create_user_service_response.data is None or github_create_user_service_response.status not in [StatusCodes.HTTP_201_CREATED, StatusCodes.HTTP_200_OK]:
                return APIResponse(
                    data=None,
                    message=github_create_user_service_response.message,
                    status=github_create_user_service_response.status
                )
            if github_create_user_service_response.status in [StatusCodes.HTTP_201_CREATED, StatusCodes.HTTP_200_OK]:
                github_user_domain = github_create_user_service_response.data
                if github_user_domain is None:
                    return APIResponse(
                        data=None,
                        message="User creation failed",
                        status=StatusCodes.HTTP_400_BAD_REQUEST
                    )
                
                social_user_repository_response = await SocialAuthRepository.get_user_by_social_user_id(
                    social_user_id=github_user_domain.social_user_id,
                    session=session
                )
                
                if social_user_repository_response.status != StatusCodes.HTTP_200_OK or social_user_repository_response.data is None:
                    return APIResponse(
                        message=social_user_repository_response.message,
                        status=social_user_repository_response.status,
                        data=None
                    )

                github_user_token_payload = GithubUserTokenPayload.from_dict({
                    "token_type": TokenEnum.ACCESS_TOKEN.value,
                    "is_active": True,
                    "global_user_id": social_user_repository_response.data.global_user_id,
                    "exp": None,
                    "email": github_user_domain.email,
                    "user_type": UserAuthType.GITHUB.value,
                    "provider_user_id": github_user_domain.provider_user_id
                })

                access_token = JWTUtils.generate_access_token(payload=github_user_token_payload)
                refresh_token = JWTUtils.generate_refresh_token(payload=github_user_token_payload)
                return APIResponse(
                    data={
                        "tokens": {
                            "access_token": access_token,
                            "access_token_expiry": SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_SECONDS),
                            "refresh_token": refresh_token,
                            "refresh_token_expiry": SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_SECONDS)
                        }
                    },
                    message="GitHub user tokens generated!",
                    status=StatusCodes.HTTP_201_CREATED
                )
            
            return APIResponse(
                message=github_create_user_service_response.message,
                data=None,
                status=github_create_user_service_response.status
            )

    # @staticmethod
    # async def find_or_create_github_user(user_info: dict, session: SessionDependency) -> APIResponse[GithubUserDomain | None]:
    #     email = user_info.get("email")
    #     github_id = user_info.get("id")
    #     from src.auth.service import GlobalUserService

    #     global_user_response: APIResponse[GlobalUserDomain | None] = await GlobalUserService.get_email_globally(email=email, session=session)

    #     if global_user_response.status == StatusCodes.HTTP_200_OK and global_user_response.data:
    #         global_user = global_user_response.data
    #     else:
    #         global_user = GlobalUserDomain.from_dict({
    #             "id": MiscUtils.generate_uuid(),
    #             "user_auth_type": UserAuthType.GITHUB.value,
    #             "is_active": True,
    #             "last_login": None,
    #             "created_at": MiscUtils.get_current_timestamp()
    #         })
    #         create_global_user_response = await GlobalUserRepository.create(obj=global_user, session=session)
    #         if create_global_user_response.status != StatusCodes.HTTP_201_CREATED or not create_global_user_response.data:
    #             await session.rollback()
    #             return APIResponse(
    #                 data=None,
    #                 message=create_global_user_response.message,
    #                 status=create_global_user_response.status
    #             )
    #         global_user = create_global_user_response.data

    #     social_user_id = MiscUtils.generate_uuid()
    #     social_user = SocialUserDomain.from_dict({
    #         "id": social_user_id,
    #         "provider_user_id": github_id,
    #         "global_user_id": global_user.id,
    #         "provider": UserAuthType.GITHUB.value
    #     })
    #     social_user_response = await SocialAuthRepository.create(data=social_user, session=session)
    #     if social_user_response.status not in [StatusCodes.HTTP_201_CREATED, StatusCodes.HTTP_200_OK] or not social_user_response.data:
    #         await session.rollback()
    #         return APIResponse(
    #             data=None,
    #             message=social_user_response.message,
    #             status=social_user_response.status
    #         )

    #     github_user = GithubUserDomain.from_dict({
    #         "id": github_id,
    #         "social_user_id": social_user_id,
    #         "provider_user_id": github_id,
    #         "email": email
    #     })
    #     github_user_response = await GithubUserRepository.create_github_user(data=github_user, session=session)

    #     if github_user_response.status == StatusCodes.HTTP_201_CREATED:
    #         await session.commit()
    #     else:
    #         await session.rollback()

    #     return APIResponse(
    #         data=github_user_response.data,
    #         message=github_user_response.message,
    #         status=github_user_response.status
    #     )




    @staticmethod
    async def find_or_create_github_user(
        user_info: dict, 
        session: SessionDependency
    ) -> APIResponse[GithubUserDomain | None]:
        # Extract essential user information
        email = user_info.get("email")
        github_id = str(user_info.get("id"))
        
        # Validate required fields
        if not email or not github_id:
            return APIResponse(
                data=None,
                message="Missing email or GitHub ID in user info",
                status=StatusCodes.HTTP_400_BAD_REQUEST
            )

        try:
            # 1️⃣ Check for existing GitHub authentication
            social_response:RepositoryResponse[SocialUserDomain|None] = await SocialAuthRepository.get_user_by_provider_and_provider_id(
                provider=UserAuthType.GITHUB,
                provider_id=github_id,
                session=session
            )

            

            if social_response.status == StatusCodes.HTTP_200_OK and social_response.data is not None:
                github_user_res = await GithubUserRepository.get_github_user_by_social_user_id(
                    social_user_id=social_response.data.id,
                    session=session
                )
                
                
                if github_user_res.status == StatusCodes.HTTP_200_OK and github_user_res.data:
                    return APIResponse(
                        data=github_user_res.data,
                        message="GitHub authentication found",
                        status=StatusCodes.HTTP_200_OK
                    )
                return APIResponse(
                    data=None,
                    message="Social record exists but GitHub user missing",
                    status=StatusCodes.HTTP_404_NOT_FOUND
                )

            # 2️⃣ Find or create global user
            from src.auth.service import GlobalUserService
            global_user_res = await GlobalUserService.get_email_globally(email, session)
            if not global_user_res.data:
                # Create new global user
                new_global = GlobalUserDomain.from_dict({

                    "id":MiscUtils.generate_uuid(),
                    "user_auth_type":UserAuthType.GITHUB.value,
                    "is_active":True,
                    "last_login":None,
                    "created_at":MiscUtils.get_current_timestamp()
                }
                )
                global_user_res = await GlobalUserRepository.create(new_global, session)
                if  global_user_res.data is None or global_user_res.status != StatusCodes.HTTP_201_CREATED:
                    await session.rollback()
                    return APIResponse(
                        data=None,
                        message=f"Global user creation failed: {global_user_res.message}",
                        status=global_user_res.status
                    )
            
            global_user = global_user_res.data

            # 3️⃣ Create social authentication record
            new_social = SocialUserDomain.from_dict({

                "id":MiscUtils.generate_uuid(),
                "provider":UserAuthType.GITHUB.value,
                "provider_user_id":github_id,
                "global_user_id":global_user.id
            }
            )
            social_res = await SocialAuthRepository.create(new_social, session)
            if not social_res.data:
                return APIResponse(
                    data=None,
                    message=f"Social authentication creation failed: {social_res.message}",
                    status=social_res.status
                )

            # 4️⃣ Create GitHub user profile
            new_github = GithubUserDomain.from_dict({

                "id":MiscUtils.generate_uuid(),
                "provider_user_id":github_id,
                "social_user_id":new_social.id,
                "email":email
            }
            )
            github_res = await GithubUserRepository.create_github_user(new_github, session)
            if not github_res.data:
                return APIResponse(
                    data=None,
                    message=f"GitHub profile creation failed: {github_res.message}",
                    status=github_res.status
                )

            return APIResponse(
                data=github_res.data,
                message="GitHub authentication created",
                status=StatusCodes.HTTP_201_CREATED
            )

        except Exception as e:
            await session.rollback()
            return APIResponse(
                data=None,
                message=f"System error: {str(e)}",
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR
            )