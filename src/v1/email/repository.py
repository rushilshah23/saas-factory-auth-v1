from src.db import SessionDependency
from .helpers import RegisterEmailRequest
from .models import EmailUser
from src.v1.models import User
from src.utils import Utils
from .utils import Utils as EmailUtils
from src.helpers.response import RepositoryResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete
from src.v1.helpers import UserAuthType
from typing import Optional
from src.utils import Utils as AppUtils
from src.helpers.status_codes import StatusCodes
from datetime import datetime
from enum import Enum



class Repository:
    @staticmethod
    def serialize_model(obj):
        def serialize(item):
            if isinstance(item, datetime):
                return item.isoformat()
            if isinstance(item, Enum):
                return item.value
            return item
        
        return {key: serialize(value) for key, value in obj.model_dump().items()}
    

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> RepositoryResponse[EmailUser | None]:
        result = await session.execute(
            select(EmailUser).where(EmailUser.email == email)
        )
        return RepositoryResponse[EmailUser | None](
            status=StatusCodes.HTTP_200_OK,
            message="User searched successfully",
            data=result.scalar_one_or_none()
        )

    @staticmethod
    async def register(data: RegisterEmailRequest, session: AsyncSession) -> RepositoryResponse:
        try:
            user_exists_response = await Repository.get_user_by_email(data.email, session)
            if user_exists_response.data:
                if user_exists_response.data.email_verified is False:
                    return RepositoryResponse(
                    status=StatusCodes.HTTP_208_ALREADY_REPORTED,
                    message="User with this email already exists but not verified",
                    data={"email_user": Repository.serialize_model(user_exists_response.data)}
                )
                return RepositoryResponse(
                    status=StatusCodes.HTTP_400_BAD_REQUEST,
                    message="User with this email already exists",
                    data={"email": data.email}
                )

            new_user = User(
                id=Utils.generate_uuid(),
                is_active=True,
                last_login=None,
                user_auth_type=UserAuthType.EMAIL,
                created_at=AppUtils.get_current_timestamp()
            )
            session.add(new_user)
            await session.flush()

            new_email_user = EmailUser(
                id=Utils.generate_uuid(),
                email=data.email,
                password=EmailUtils.hash_password(data.password),
                email_verified=False,
                user_id=new_user.id,
                password_updated_at=AppUtils.get_current_timestamp()
            )
            session.add(new_email_user)
            await session.commit()



            return RepositoryResponse(
                status=StatusCodes.HTTP_201_CREATED,
                message="User data saved successfully",
                data={"email_user": Repository.serialize_model(new_email_user), "user": Repository.serialize_model(new_user)}
            )

        except Exception as e:
            await session.rollback()  # <- important
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An error occurred: {str(e)}"
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
            email_user = result.scalar_one_or_none()

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
                    data={"email": email_user.email, "user_id": email_user.user_id}
                )
            email_user.email_verified = True
            await session.commit()

            return RepositoryResponse(
                status=StatusCodes.HTTP_200_OK,
                message="Email verified successfully",
                data={"email": email_user.email, "user_id": email_user.user_id}
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

            email_user.last_login = AppUtils.get_current_timestamp()
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
            email_user = result.scalar_one_or_none()

            if not email_user:
                return RepositoryResponse(
                    status=StatusCodes.HTTP_404_NOT_FOUND,
                    message="Email user not found",
                    data=None
                )

            email_user.password = EmailUtils.hash_password(new_password)
            email_user.password_updated_at = AppUtils.get_current_timestamp()

            await session.commit()

            return RepositoryResponse(
                status=StatusCodes.HTTP_200_OK,
                message="Password updated successfully",
                data={"email": email_user.email, "user_id": email_user.user_id}
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An error occurred: {str(e)}"
            )