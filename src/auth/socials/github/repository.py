from src.auth.socials.github.domain import GithubUserDomain
from src.auth.socials.github.models import GithubUser
from sqlmodel.ext.asyncio.session import AsyncSession
from src.helpers.response import RepositoryResponse
from src.helpers.status_codes import StatusCodes
from sqlmodel import select, delete
from .models import GithubUser

class GithubUserRepository:

    @staticmethod
    async def get_user_by_github_user_id(github_user_id:str,session:AsyncSession):
        result:GithubUser | None = (await session.execute(
            select(GithubUser)
            .where(GithubUser.provider_user_id == github_user_id)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message="Github account doesn't exists",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="Github account exists",
            data=GithubUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )
    @staticmethod
    async def get_github_user_by_email(email:str,session:AsyncSession):
        result:GithubUser | None = (await session.execute(
            select(GithubUser)
            .where(GithubUser.email == email)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message="Github account doesn't exists",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="Github account exists",
            data=GithubUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )  

    @staticmethod
    async def create_github_user(data:GithubUserDomain,session:AsyncSession)-> RepositoryResponse[GithubUserDomain|None]:
        try:
            github_user_exists_repository_response = await GithubUserRepository.get_user_by_github_user_id(github_user_id=data.provider_user_id,session=session)
            if github_user_exists_repository_response.status == StatusCodes.HTTP_200_OK and github_user_exists_repository_response.data is not None:
                return RepositoryResponse(
                    data=GithubUserDomain.from_model(model_obj=github_user_exists_repository_response.data),
                    message="The given github user already exists",
                    status=StatusCodes.HTTP_200_OK
                )
            github_user = GithubUser(
                id=data.id,
                provider_user_id=data.provider_user_id,
                social_user_id=data.social_user_id,
                email=data.email

            )

            session.add(github_user)

            await session.commit()
            return RepositoryResponse(
                data=GithubUserDomain.from_model(model_obj=github_user),
                message="Github user created successfully",
                status=StatusCodes.HTTP_201_CREATED
            )
        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                data=None,
                message=f"Error Github user repository - {e}",
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_github_user_by_social_user_id(
        social_user_id: str, session: AsyncSession
    ) -> RepositoryResponse[GithubUserDomain | None]:
        result: GithubUser | None = (await session.execute(
            select(GithubUser)
            .where(GithubUser.social_user_id == social_user_id)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message="Github user doesn't exist with the given social user ID",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="Github user exists",
            data=GithubUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )