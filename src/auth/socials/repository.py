from src.auth.helpers import UserAuthType 
from .domain import SocialUserDomain
from .models import SocialUser


from sqlmodel.ext.asyncio.session import AsyncSession
from src.helpers.response import RepositoryResponse
from src.helpers.status_codes import StatusCodes
from sqlmodel import select, delete



class SocialAuthRepository:

    @staticmethod
    async def get_user_by_provider_and_provider_id(provider:UserAuthType, provider_id:str, session:AsyncSession):
        result:SocialUser | None = (await session.execute(
            select(SocialUser)
            .where(SocialUser.provider == provider)
            .where(SocialUser.provider_user_id == provider_id)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message="Social account doesn't exists",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="Social account exists",
            data=SocialUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )
        
    @staticmethod
    async def get_user_by_social_user_id(social_user_id:str, session:AsyncSession):
        result:SocialUser | None = (await session.execute(
            select(SocialUser)
            .where(SocialUser.id == social_user_id)
        )).scalar_one_or_none()

        if result is None:
            return RepositoryResponse(
                message=f"Social account doesn't exists with social Id - {social_user_id}",
                data=None,
                status=StatusCodes.HTTP_404_NOT_FOUND
            )
        return RepositoryResponse(
            message="Social account exists",
            data=SocialUserDomain.from_model(model_obj=result),
            status=StatusCodes.HTTP_200_OK
        )
        
    @staticmethod
    async def create(data: SocialUserDomain, session: AsyncSession) -> RepositoryResponse[SocialUserDomain|None]:
        try:
            user_exists_response = await SocialAuthRepository.get_user_by_provider_and_provider_id(provider=data.provider, provider_id=data.provider_user_id, session=session)
            if user_exists_response.data is not None and user_exists_response.status == StatusCodes.HTTP_200_OK:

                return RepositoryResponse(
                    status=StatusCodes.HTTP_200_OK,
                    message="SOcial User with provided provider and provider_id already exists",
                    data=user_exists_response.data
                )



            new_social_user = SocialUser(
                id=data.id,
                global_user_id=data.global_user_id,
                provider=data.provider,
                provider_user_id=data.provider_user_id
            )
            session.add(new_social_user)
            await session.flush()



            return RepositoryResponse(
                status=StatusCodes.HTTP_201_CREATED,
                message="User data saved successfully",
                data=SocialUserDomain.from_model(model_obj=new_social_user)
            )

        except Exception as e:

            await session.rollback()  # <- important
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"EmailUser Repository error - : {str(e)}"
            )