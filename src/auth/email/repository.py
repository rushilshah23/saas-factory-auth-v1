from src.db import SessionDependency
from .helpers import RegisterEmailRequest
from .models import EmailUser
from .utils import EmailUserUtils
from src.helpers.response import RepositoryResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete
from src.auth.helpers import UserAuthType
from typing import Optional
from src.utils.misc import MiscUtils
from src.helpers.status_codes import StatusCodes
from datetime import datetime
from enum import Enum
from .domain import EmailUserDomain
from src.auth.repository import GlobalUserRepository 
from src.auth.domain import GlobalUserDomain

class EmailUserRepository:

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> RepositoryResponse[EmailUserDomain | None]:
        query_result = (await session.execute(
            select(EmailUser).where(EmailUser.email == email)
        )).scalar_one_or_none()

        if query_result is None:
            return RepositoryResponse(
                status=StatusCodes.HTTP_404_NOT_FOUND,
                message=f"Email user {email} not found",
                data=None
            )

        domain_obj = EmailUserDomain.from_model(model_obj=query_result)

        return RepositoryResponse(
            status=StatusCodes.HTTP_200_OK,
            message="User searched successfully",
            data=domain_obj
        )

    @staticmethod
    async def get_email_user_by_global_user_id(global_user_id: str, session: AsyncSession) -> RepositoryResponse[EmailUserDomain | None]:
        query_result:EmailUser = (await session.execute(
            select(EmailUser).where(EmailUser.global_user_id == global_user_id)
        )).scalar_one_or_none()

        if query_result is None:
            return RepositoryResponse(
                status=StatusCodes.HTTP_404_NOT_FOUND,
                message=f"Email User with global_user_id {global_user_id} doesn't exists",
                data=None
            )

        domain_obj = EmailUserDomain.from_model(model_obj=query_result)

        return RepositoryResponse(
            status=StatusCodes.HTTP_200_OK,
            message="User searched successfully",
            data=domain_obj
        )

    @staticmethod
    async def create(data: EmailUserDomain, session: AsyncSession) -> RepositoryResponse[EmailUserDomain|None]:
        try:
            user_exists_response = await EmailUserRepository.get_user_by_email(data.email, session)
            if user_exists_response.data:
                if user_exists_response.data.email_verified is False:
                    return RepositoryResponse(
                    status=StatusCodes.HTTP_208_ALREADY_REPORTED,
                    message="User with this email already exists but not verified",
                    data=user_exists_response.data
                )
                return RepositoryResponse(
                    status=StatusCodes.HTTP_400_BAD_REQUEST,
                    message="User with this email already exists",
                    data={"email": data.email}
                )



            new_email_user = EmailUser(
                id=data.id,
                email=data.email,
                email_verified=data.email_verified,
                global_user_id=data.global_user_id,
                password=data.password,
                password_updated_at=data.password_updated_at
            )
            session.add(new_email_user)
            await session.commit()



            return RepositoryResponse(
                status=StatusCodes.HTTP_201_CREATED,
                message="User data saved successfully",
                data=EmailUserDomain.from_model(new_email_user)
            )

        except Exception as e:

            await session.rollback()  # <- important
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"EmailUser Repository error - : {str(e)}"
            )
        
    @staticmethod
    async def verify_user_email(email: str, email_user_id: str, session: AsyncSession) -> RepositoryResponse:
        try:
            result = await session.execute(
                select(EmailUser).where(
                    EmailUser.email == email,
                    EmailUser.id == email_user_id
                )
            )
            email_user:EmailUser = result.scalar_one_or_none()

            if not email_user:
                return RepositoryResponse(
                    status=StatusCodes.HTTP_404_NOT_FOUND,
                    message=f"Email user {email} not found",
                    data=None
                )
            if email_user.email_verified:
                return RepositoryResponse(
                    status=StatusCodes.HTTP_400_BAD_REQUEST,
                    message="Email already verified",
                    data={"email": email_user.email, "user_id": email_user.id}
                )
            email_user.email_verified = True
            await session.commit()

            return RepositoryResponse(
                status=StatusCodes.HTTP_200_OK,
                message="Email verified successfully",
                data={"email": email_user.email, "user_id": email_user.id}
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An error occurred: {str(e)}"
            )
        
    
    @staticmethod
    async def update_last_login(email_user_id: str, session: AsyncSession) -> RepositoryResponse:
        try:
            result = await session.execute(
                select(EmailUser).where(EmailUser.id == email_user_id)
            )
            email_user = result.scalar_one_or_none()

            if not email_user:
                return RepositoryResponse(
                    status=StatusCodes.HTTP_404_NOT_FOUND,
                    message="Email user not found",
                    data=None
                )

            email_user.last_login = MiscUtils.get_current_timestamp()
            await session.commit()

            return RepositoryResponse(
                status=StatusCodes.HTTP_200_OK,
                message="Last login updated successfully",
                data={"email": email_user.email, "user_id": email_user.user_id}
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An error occurred: {str(e)}"
            )
        
    @staticmethod
    async def update_password(email: str, new_password: str, session: AsyncSession) -> RepositoryResponse:
        try:
            result = await session.execute(
                select(EmailUser).where(EmailUser.email == email)
            )
            email_user:EmailUser|None = result.scalar_one_or_none()

            if not email_user:
                return RepositoryResponse(
                    status=StatusCodes.HTTP_404_NOT_FOUND,
                    message="Email user not found",
                    data=None
                )

            email_user.password = EmailUserUtils.hash_password(new_password)
            email_user.password_updated_at = MiscUtils.get_current_timestamp()

            await session.commit()

            return RepositoryResponse(
                status=StatusCodes.HTTP_200_OK,
                message="Password updated successfully",
                data=EmailUserDomain.from_model(model_obj=email_user).to_dict()
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An error occurred: {str(e)}"
            )