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

class Repository:

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> RepositoryResponse[EmailUser | None]:
        result = await session.execute(
            select(EmailUser).where(EmailUser.email == email)
        )
        return RepositoryResponse[EmailUser | None](
            status=200,
            message="User searched successfully",
            data=result.scalar_one_or_none()
        )

    @staticmethod
    async def register(data: RegisterEmailRequest, session: AsyncSession) -> RepositoryResponse:
        try:
            user_exists_response = await Repository.get_user_by_email(data.email, session)
            if user_exists_response.data:
                return RepositoryResponse(
                    status=400,
                    message="User with this email already exists",
                    data={"email": data.email}
                )

            new_user = User(
                id=Utils.generate_uuid(),
                is_active=True,
                last_login=None,
                user_auth_type=UserAuthType.EMAIL
            )
            session.add(new_user)
            await session.flush()

            new_email_user = EmailUser(
                id=Utils.generate_uuid(),
                email=data.email,
                password=EmailUtils.hash_password(data.password),
                email_verified=False,
                user_id=new_user.id
            )
            session.add(new_email_user)
            await session.commit()



            return RepositoryResponse(
                status=201,
                message="User data saved successfully",
                data={"email": new_email_user.email, "user_id": new_email_user.user_id}
            )

        except Exception as e:
            await session.rollback()  # <- important
            return RepositoryResponse(
                status=500,
                message=f"An error occurred: {str(e)}"
            )
        
    @staticmethod
    async def verify_user_email(email: str, user_id: str, session: AsyncSession) -> RepositoryResponse:
        try:
            result = await session.execute(
                select(EmailUser).where(
                    EmailUser.email == email,
                    EmailUser.user_id == user_id
                )
            )
            email_user = result.scalar_one_or_none()

            if not email_user:
                return RepositoryResponse(
                    status=404,
                    message="Email user not found",
                    data=None
                )
            if email_user.email_verified:
                return RepositoryResponse(
                    status=400,
                    message="Email already verified",
                    data={"email": email_user.email, "user_id": email_user.user_id}
                )
            email_user.email_verified = True
            await session.commit()

            return RepositoryResponse(
                status=200,
                message="Email verified successfully",
                data={"email": email_user.email, "user_id": email_user.user_id}
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=500,
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
                    status=404,
                    message="Email user not found",
                    data=None
                )

            email_user.last_login = AppUtils.get_current_timestamp()
            await session.commit()

            return RepositoryResponse(
                status=200,
                message="Last login updated successfully",
                data={"email": email_user.email, "user_id": email_user.user_id}
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=500,
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
                    status=404,
                    message="Email user not found",
                    data=None
                )

            email_user.password = EmailUtils.hash_password(new_password)
            await session.commit()

            return RepositoryResponse(
                status=200,
                message="Password updated successfully",
                data={"email": email_user.email, "user_id": email_user.user_id}
            )

        except Exception as e:
            await session.rollback()
            return RepositoryResponse(
                status=500,
                message=f"An error occurred: {str(e)}"
            )