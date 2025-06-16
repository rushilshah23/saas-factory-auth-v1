from src.auth.socials.google.domain import GoogleUserDomain
from src.auth.socials.google.models import GoogleUser
from sqlmodel.ext.asyncio.session import AsyncSession
from src.helpers.response import RepositoryResponse
from src.helpers.status_codes import StatusCodes
from sqlmodel import select, delete
from .models import GoogleUser

class GoogleUserRepository:

    @staticmethod
    async def get_user_by_google_user_id(gogole_user_id:str,session:AsyncSession):
        result:GoogleUser | None = (await session.execute(
            select(GoogleUser)
            .where(GoogleUser.provider_user_id == gogole_user_id)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message="Google account doesn't exists",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="GOogle account exists",
            data=GoogleUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )
    @staticmethod
    async def get_google_user_by_email(email:str,session:AsyncSession):
        result:GoogleUser | None = (await session.execute(
            select(GoogleUser)
            .where(GoogleUser.email == email)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message="Google account doesn't exists",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="GOogle account exists",
            data=GoogleUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )  

    @staticmethod
    async def create_google_user(data:GoogleUserDomain,session:AsyncSession)-> RepositoryResponse[GoogleUserDomain|None]:
        try:
            google_user_exists_repository_response = await GoogleUserRepository.get_user_by_google_user_id(gogole_user_id=data.provider_user_id,session=session)
            if google_user_exists_repository_response.status == StatusCodes.HTTP_200_OK and google_user_exists_repository_response.data is not None:
                return RepositoryResponse(
                    data=GoogleUserDomain.from_model(model_obj=google_user_exists_repository_response.data),
                    message="The given google user already exists",
                    status=StatusCodes.HTTP_200_OK
                )
            google_user = GoogleUser(
                id=data.id,
                provider_user_id=data.provider_user_id,
                social_user_id=data.social_user_id,
                email=data.email

            )

            session.add(google_user)

            await session.commit()
            return RepositoryResponse(
                data=GoogleUserDomain.from_model(model_obj=google_user),
                message="Google user created successfully",
                status=StatusCodes.HTTP_201_CREATED
            )
        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                data=None,
                message=f"Error Google user repository - {e}",
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR
            )

