from src.helpers.response import APIResponse
from fastapi import HTTPException, Request
from src.helpers.response import APIResponse
from src.helpers.token import TokenEnum
from src.helpers.status_codes import StatusCodes
from src.utils.jwt import JWTUtils
from src.helpers.token import UserTokenPayload, EmailUserTokenPayload, GoogleUserTokenPayload, GithubUserTokenPayload
from src.db import SessionDependency
from src.auth.email.repository import EmailUserRepository
from src.auth.email.domain import EmailUserDomain
from src.auth.socials.google.repository import GoogleUserRepository
from src.auth.socials.google.domain import GoogleUserDomain
from .repository import GlobalUserRepository
from src.helpers.response import RepositoryResponse
from src.auth.socials.repository import SocialAuthRepository
from src.auth.socials.domain import SocialUserDomain
from src.auth.socials.github.domain import GithubUserDomain
from src.auth.socials.github.repository import GithubUserRepository
from src.auth.helpers import UserAuthType


class GlobalUserService:

    async def authenticate(request:Request)-> APIResponse[UserTokenPayload | None]:
        token = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]


        if not token:
            token = request.cookies.get(TokenEnum.ACCESS_TOKEN.value)

        if not token:
            raise HTTPException(status_code=StatusCodes.HTTP_401_UNAUTHORIZED.value, detail="Missing access token")

        payload = await JWTUtils.verify_access_token(token=token, expected_token_type=UserTokenPayload)
        if payload.user_type == UserAuthType.GOOGLE.value:
            payload = GoogleUserTokenPayload.from_dict(payload.to_dict())
        if payload.user_type == UserAuthType.GITHUB.value:
            payload = GithubUserTokenPayload.from_dict(payload.to_dict())  
        if payload.user_type == UserAuthType.EMAIL.value:
            payload = EmailUserTokenPayload.from_dict(payload.to_dict())
        if not payload:
            raise HTTPException(status_code=StatusCodes.HTTP_401_UNAUTHORIZED.value, detail="Invalid or expired token")

        return APIResponse(
            status=StatusCodes.HTTP_200_OK,
            message="User authenticated successfully",
            data=payload
        )
    
    # @staticmethod
    # async def get_email_globally(email:str, session:SessionDependency):
    #     # Check in email users
    #     email_repository_response:RepositoryResponse[EmailUserDomain|None] = await EmailUserRepository.get_user_by_email(email=email,session=session)
    #     if email_repository_response.status == StatusCodes.HTTP_200_OK and email_repository_response.data is not None:
    #         global_user_repository_response = await GlobalUserRepository.get_user_by_global_user_id(email_repository_response.data.global_user_id,session=session)
    #         if global_user_repository_response.status == StatusCodes.HTTP_200_OK and global_user_repository_response.data is not None:
    #             return APIResponse(
    #                 data=global_user_repository_response.data,
    #                 message=f"Global user with email - {email} exists",
    #                 status=StatusCodes.HTTP_200_OK
    #             )
    #     # Check in social - google users
    #     google_repository_response:RepositoryResponse[GoogleUserDomain|None] = await GoogleUserRepository.get_google_user_by_email(email=email,session=session)
    #     if google_repository_response.status == StatusCodes.HTTP_200_OK and google_repository_response.data is not None:
    #         social_repository_response = await SocialAuthRepository.get_user_by_social_user_id(social_user_id=google_repository_response.data.social_user_id,session=session)
    #         if social_repository_response.status == StatusCodes.HTTP_200_OK and social_repository_response.data is not None:
    #             global_user_repository_response = await GlobalUserRepository.get_user_by_global_user_id(social_repository_response.data.global_user_id,session=session)
    #             if global_user_repository_response.status == StatusCodes.HTTP_200_OK and global_user_repository_response.data is not None:
    #                 return APIResponse(
    #                     data=global_user_repository_response.data,
    #                     message=f"Global user with email - {email} exists",
    #                     status=StatusCodes.HTTP_200_OK
    #                 )

    #     return APIResponse(
    #         data=None,
    #         message=f"No global user with email Id - {email} found",
    #         status=StatusCodes.HTTP_404_NOT_FOUND
    #     )




    @staticmethod
    async def get_email_globally(email: str, session: SessionDependency):
        # Check in email users
        email_repository_response: RepositoryResponse[EmailUserDomain | None] = await EmailUserRepository.get_user_by_email(email=email, session=session)
        if email_repository_response.status == StatusCodes.HTTP_200_OK and email_repository_response.data is not None:
            global_user_repository_response = await GlobalUserRepository.get_user_by_global_user_id(email_repository_response.data.global_user_id, session=session)
            if global_user_repository_response.status == StatusCodes.HTTP_200_OK and global_user_repository_response.data is not None:
                return APIResponse(
                    data=global_user_repository_response.data,
                    message=f"Global user with email - {email} exists",
                    status=StatusCodes.HTTP_200_OK
                )

        # Check in social - google users
        google_repository_response: RepositoryResponse[GoogleUserDomain | None] = await GoogleUserRepository.get_google_user_by_email(email=email, session=session)
        if google_repository_response.status == StatusCodes.HTTP_200_OK and google_repository_response.data is not None:
            social_repository_response = await SocialAuthRepository.get_user_by_social_user_id(social_user_id=google_repository_response.data.social_user_id, session=session)
            if social_repository_response.status == StatusCodes.HTTP_200_OK and social_repository_response.data is not None:
                global_user_repository_response = await GlobalUserRepository.get_user_by_global_user_id(social_repository_response.data.global_user_id, session=session)
                if global_user_repository_response.status == StatusCodes.HTTP_200_OK and global_user_repository_response.data is not None:
                    return APIResponse(
                        data=global_user_repository_response.data,
                        message=f"Global user with email - {email} exists",
                        status=StatusCodes.HTTP_200_OK
                    )

        # Check in social - github users
        github_repository_response: RepositoryResponse[GithubUserDomain | None] = await GithubUserRepository.get_github_user_by_email(email=email, session=session)
        if github_repository_response.status == StatusCodes.HTTP_200_OK and github_repository_response.data is not None:
            social_repository_response = await SocialAuthRepository.get_user_by_social_user_id(social_user_id=github_repository_response.data.social_user_id, session=session)
            if social_repository_response.status == StatusCodes.HTTP_200_OK and social_repository_response.data is not None:
                global_user_repository_response = await GlobalUserRepository.get_user_by_global_user_id(social_repository_response.data.global_user_id, session=session)
                if global_user_repository_response.status == StatusCodes.HTTP_200_OK and global_user_repository_response.data is not None:
                    return APIResponse(
                        data=global_user_repository_response.data,
                        message=f"Global user with email - {email} exists",
                        status=StatusCodes.HTTP_200_OK
                    )

        return APIResponse(
            data=None,
            message=f"No global user with email Id - {email} found",
            status=StatusCodes.HTTP_404_NOT_FOUND
        )
