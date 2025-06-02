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
from src.configs.secrets import SecretUtils


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

            base_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_VERIFICATION_BASE_URL)
            verification_link = f"{base_url}?email={data.email}&token={new_email_user.id}"

            await Utils.send_email(
                subject="Verify your email",
                recipient=data.email,
                body=f"Welcome to our app!\n\nPlease verify your email by clicking the following link:\n{verification_link}"
            )

            return RepositoryResponse(
                status=201,
                message="Verify the email to complete registration through the link sent to your email",
                data={"email": new_email_user.email}
            )

        except Exception as e:
            await session.rollback()  # <- important
            return RepositoryResponse(
                status=500,
                message=f"An error occurred: {str(e)}"
            )