from .utils import Utils
from src.utils import Utils as AppUtils
from .helpers import (
    RegisterEmailRequest,
    LoginEmailRequest,
    AccessTokenPayload
    # VerifyEmailRequest,
    # ForgotPasswordRequest,
    # ResetPasswordRequest,
    # LogoutRequest
)
from src.helpers.response import APIResponse
from .repository import Repository
from sqlmodel import Session
from src.configs.secrets import SecretUtils

class Service:
    @staticmethod
    async def register(data: RegisterEmailRequest, session: Session) -> APIResponse:
        if data.password != data.confirm_password:
            return APIResponse.error("Passwords do not match", status=400)
        repository_response = await Repository.register(data, session)
        if repository_response.status == 201:
            base_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_VERIFICATION_BASE_URL)
            token = await AppUtils.generate_access_token({"email": data.email, "user_id": repository_response.data.get("user_id")})
            verification_link = f"{base_url}/api/v1/email/verify-email?token={token}"

            await AppUtils.send_email(
                subject="Verify your email",
                recipient=data.email,
                body=f"Welcome to our app!\n\nPlease verify your email by clicking the following link:\n{verification_link}"
            )
        return APIResponse(status=repository_response.status,
                            message=repository_response.message,
                            data=repository_response.data)
    
    @staticmethod
    async def verify_user(token: str, session: Session) -> APIResponse:
        email_data = await AppUtils.verify_access_token(token)
        if not email_data:
            return APIResponse.error("Invalid or expired token", status=400)
        
        email = email_data.get("email")
        user_id = email_data.get("user_id")
        
        if not email or not user_id:
            return APIResponse.error("Invalid token data", status=400)
        
        repository_response = await Repository.verify_user_email(email, user_id, session)
        return APIResponse(status=repository_response.status,
                            message=repository_response.message,
                            data=repository_response.data)

    @staticmethod
    async def login(data: LoginEmailRequest, session: Session) -> APIResponse:
        email_user_repository_response = await Repository.get_user_by_email(data.email, session)
        email_user = email_user_repository_response.data
        if not email_user:
            return APIResponse(message=f"Email user {data.email} not found", status=404)
        
        if not email_user.email_verified:
            return APIResponse(message="Email not verified", status=403)
        
        if not Utils().verify_password(data.password, email_user.password):
            return APIResponse(message="Invalid credentials", status=401)

        payload = AccessTokenPayload(
            email=email_user.email,
            user_id=email_user.user_id
        )         
        token = await AppUtils.generate_access_token(payload.model_dump())
        if not token:
            return APIResponse.error("Failed to generate access token", status=500)
        
        expires_in_minutes = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        expires_in_seconds = expires_in_minutes * 60
        await Repository.update_last_login(email_user.id, session)
        return APIResponse(message="Access token generated",data={"access_token": token, "token_type": "bearer", "expires_in":expires_in_seconds }, status=200)

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