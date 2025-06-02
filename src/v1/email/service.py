from .utils import Utils
from .helpers import (
    RegisterEmailRequest,
    LoginEmailRequest,
    # VerifyEmailRequest,
    # ForgotPasswordRequest,
    # ResetPasswordRequest,
    # LogoutRequest
)
from src.helpers.response import APIResponse
from .repository import Repository
from sqlmodel import Session

class Service:
    @staticmethod
    async def register(data: RegisterEmailRequest, session: Session) -> APIResponse:
        if data.password != data.confirm_password:
            return APIResponse.error("Passwords do not match", status=400)
        repository_response = await Repository.register(data, session)
        return APIResponse(status=repository_response.status,
                            message=repository_response.message,
                            data=repository_response.data)

    @staticmethod
    async def login(data: LoginEmailRequest, session: Session) -> APIResponse:
        email_user_repository_response = await Repository.get_user_by_email(data.email, session)
        email_user = email_user_repository_response.data
        if not email_user:
            return APIResponse.error(f"Email user {data.email} not found", status=404)
            
        if not Utils.verify_password(data.password, email_user.password):
            return APIResponse.error("Invalid credentials", status=401)
            
        if not email_user.email_verified:
            return APIResponse.error("Email not verified", status=403)
            
        token = Utils.generate_token({"sub": email_user.email})
        await Repository.update_last_login(email_user.id, session)
        return APIResponse.success({"access_token": token, "token_type": "bearer"})

    # @staticmethod
    # async def verify_email(data: VerifyEmailRequest, session: Session) -> APIResponse:
    #     email = Utils.validate_token(data.token)
    #     if not email:
    #         return APIResponse.error("Invalid token", status=400)
    #     return await Repository.verify_user_email(email, session)

    # @staticmethod
    # async def forgot_password(data: ForgotPasswordRequest, session: Session) -> APIResponse:
    #     user = await Repository.get_user_by_email(data.email, session)
    #     if not user:
    #         return APIResponse.error("User not found", status=404)
            
    #     reset_token = Utils.generate_password_reset_token(data.email)
    #     return await Repository.save_password_reset_token(
    #         user.id, reset_token, session
    #     )

    # @staticmethod
    # async def reset_password(data: ResetPasswordRequest, session: Session) -> APIResponse:
    #     if data.new_password != data.confirm_password:
    #         return APIResponse.error("Passwords do not match", status=400)
            
    #     email = Utils.validate_password_reset_token(data.token)
    #     if not email:
    #         return APIResponse.error("Invalid or expired token", status=400)
            
    #     return await Repository.update_user_password(
    #         email, data.new_password, session
    #     )

    # @staticmethod
    # async def logout(data: LogoutRequest, session: Session) -> APIResponse:
    #     return await Repository.invalidate_token(data.token, session)