from .domain import GlobalUserDomain
from src.auth.models import GlobalUser
from sqlmodel.ext.asyncio.session import AsyncSession
from src.helpers.response import RepositoryResponse
from src.helpers.status_codes import StatusCodes
from sqlmodel import select, delete


class GlobalUserRepository:

    @staticmethod
    async def create(obj: GlobalUserDomain, session: AsyncSession) -> RepositoryResponse[GlobalUser | None]:
        try:
            new_user = GlobalUser(
                id=obj.id,
                created_at=obj.created_at,
                is_active=obj.is_active,
                last_login=obj.last_login,
                user_auth_type=obj.user_auth_type
            )     

            session.add(new_user)
            await session.flush()

            global_user_domain =  GlobalUserDomain.from_model(new_user)

            return RepositoryResponse(
                message=f"Global user created successfully",
                data=global_user_domain,
                status=StatusCodes.HTTP_201_CREATED
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                message=f"Failed to create global user - {e}",
                data=None,
                status=StatusCodes.HTTP_400_BAD_REQUEST
            )


    @staticmethod
    async def get_user_by_global_user_id(global_user_id: str, session: AsyncSession) -> RepositoryResponse[GlobalUserDomain | None]:
        query_result:GlobalUser = (await session.execute(
            select(GlobalUser).where(GlobalUser.id == global_user_id)
        )).scalar_one_or_none()

        if query_result is None:
            return RepositoryResponse(
                status=StatusCodes.HTTP_404_NOT_FOUND,
                message=f"User {global_user_id} doesn't exists",
                data=None
            )

        domain_obj = GlobalUserDomain.from_model(model_obj=query_result)

        return RepositoryResponse(
            status=StatusCodes.HTTP_200_OK,
            message="User searched successfully",
            data=domain_obj
        )