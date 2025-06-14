from .utils import Utils
from src.utils import Utils as AppUtils
from .helpers import (
    RegisterEmailRequest,
    LoginEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)
from src.helpers.response import APIResponse
from .repository import Repository
from sqlmodel import Session
from src.configs.secrets import SecretUtils
from fastapi import Request
from src.v1.service import Service as AppService
from src.helpers.token import TokenPayload
from src.helpers.status_codes import StatusCodes
class Service:
    @staticmethod
    async def register(data: RegisterEmailRequest, session: Session) -> APIResponse:
        if data.password != data.confirm_password:
            return APIResponse("Passwords do not match", status=StatusCodes.HTTP_400_BAD_REQUEST)
        repository_response = await Repository.register(data, session)
        if repository_response.status == StatusCodes.HTTP_201_CREATED:
            base_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.SERVER_BASE_URL)
            payload = TokenPayload(
                email=data.email,
                user_id=repository_response.data.get("user_id")
            )
            if not payload:
                return APIResponse("Failed to generate token payload", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)
            token =  AppUtils.generate_access_token(payload)
            if not token:
                return APIResponse("Failed to generate verification token", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)
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
            return APIResponse("Invalid or expired token", status=StatusCodes.HTTP_400_BAD_REQUEST)
        
        email = email_data.email
        user_id = email_data.user_id
        
        if not email or not user_id:
            return APIResponse("Invalid token data", status=StatusCodes.HTTP_400_BAD_REQUEST)
        
        repository_response = await Repository.verify_user_email(email, user_id, session)
        return APIResponse(status=repository_response.status,
                            message=repository_response.message,
                            data=repository_response.data)

    @staticmethod
    async def login(data: LoginEmailRequest, session: Session) -> APIResponse:
        email_user_repository_response = await Repository.get_user_by_email(data.email, session)
        email_user = email_user_repository_response.data
        if not email_user:
            return APIResponse(message=f"Email user {data.email} not found", status=StatusCodes.HTTP_404_NOT_FOUND)
        
        if not email_user.email_verified:
            return APIResponse(message="Email not verified", status=StatusCodes.HTTP_403_FORBIDDEN)
        
        if not Utils().verify_password(data.password, email_user.password):
            return APIResponse(message="Invalid credentials", status=StatusCodes.HTTP_401_UNAUTHORIZED)

        payload = TokenPayload(
            email=email_user.email,
            user_id=email_user.user_id,
            is_active=email_user.email_verified,
            is_verified=email_user.email_verified,
            exp=None
        )         
        access_token =   AppUtils.generate_access_token(payload)
        refresh_token =  AppUtils.generate_refresh_token(payload)
        if not access_token or not refresh_token:
            return APIResponse("Failed to generate tokens", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token_expires_in_minutes = float(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token_expires_in_seconds = access_token_expires_in_minutes * 60
        print(f"Access token expires in: {access_token_expires_in_minutes} mins")
        print(f"Access token expires in: {access_token_expires_in_seconds} seconds")

        refresh_token_expires_in_minutes = float(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES))
        refresh_token_expires_in_seconds = refresh_token_expires_in_minutes * 60
        await Repository.update_last_login(email_user.user_id, session)
        tokens = {
            "access_token": access_token,
            "access_token_expiry": access_token_expires_in_seconds,
            "refresh_token": refresh_token,
            "refresh_token_expiry": refresh_token_expires_in_seconds,
            "user_id": email_user.user_id,
            "email": email_user.email
        }
        print(tokens)
        return APIResponse(message="Access token generated",data={"tokens": tokens, "token_type": "bearer" }, status=StatusCodes.HTTP_200_OK)


    @staticmethod
    async def refresh_token(request:Request, session: Session) -> APIResponse:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return APIResponse(message="Missing refresh token", status=StatusCodes.HTTP_401_UNAUTHORIZED)
        payload =  AppUtils.verify_refresh_token(refresh_token)
        print(refresh_token)
        print(payload)
        if not payload:
            return APIResponse(message="Invalid or expired refresh token. Please login again", status=StatusCodes.HTTP_401_UNAUTHORIZED)
        refresh_token_renew_threshold = float(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_RENEW_THRESHOLD))
        print(f"Current timestamp: {AppUtils.get_current_timestamp()}")
        print(f"Refresh token expiry: {payload.exp}")
        print(f"Refresh token renew threshold: {refresh_token_renew_threshold}")
        print(f"Time left for refresh token renewal: {payload.exp - AppUtils.get_current_timestamp()} seconds")

        if payload.exp - AppUtils.get_current_timestamp() < refresh_token_renew_threshold*60:
            # Regenerate access and refresh tokens
            access_token = AppUtils.generate_access_token(payload)
            refresh_token = AppUtils.generate_refresh_token(payload)
            if not access_token or not refresh_token:
                return APIResponse("Failed to generate tokens", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)
            access_token_expires_in_minutes = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
            access_token_expires_in_seconds = access_token_expires_in_minutes * 60
            refresh_token_expires_in_minutes = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES))
            refresh_token_expires_in_seconds = refresh_token_expires_in_minutes * 60
            tokens = {
                "access_token": access_token,
                "access_token_expiry": access_token_expires_in_seconds,
                "refresh_token": refresh_token,
                "refresh_token_expiry": refresh_token_expires_in_seconds,
                "user_id": payload.user_id,
                "email": payload.email
            }
            return APIResponse(
                message="Tokens renewed successfully",
                data={"tokens": tokens, "token_type": "bearer"},
                status=StatusCodes.HTTP_200_OK
            )
        else:
            return APIResponse(message="Refresh token is still valid, no need to renew", status=StatusCodes.HTTP_201_CREATED)
        


    @staticmethod
    async def forgot_password(data: ForgotPasswordRequest, session: Session) -> APIResponse:
        user = await Repository.get_user_by_email(data.email, session)
        if not user:
            return APIResponse("User not found", status=StatusCodes.HTTP_404_NOT_FOUND)
        
        payload = TokenPayload(email=user.data.email,user_id=user.data.user_id,is_active=user.data.email_verified,is_verified=user.data.email_verified)
            
        reset_token = AppUtils.generate_password_reset_token(payload)
        # send reset token via email
        base_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.CLIENT_BASE_URL)
        reset_link = f"{base_url}/api/v1/email/reset-password?token={reset_token}"
        await AppUtils.send_email(
            subject="Password Reset Request",
            recipient=data.email,
            body=f"To reset your password, please click the following link:\n{reset_link}\n\nIf you did not request this, please ignore this email."
        )
        if not reset_token:
            return APIResponse("Failed to generate password reset token", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)
        return APIResponse(
            message="Password reset link sent to your email",
            data={"reset_link": reset_link},
            status=StatusCodes.HTTP_200_OK
        )

    @staticmethod
    async def reset_password(data: ResetPasswordRequest, token:str, session: Session) -> APIResponse:
        if data.new_password != data.confirm_password:
            return APIResponse("Passwords do not match", status=StatusCodes.HTTP_400_BAD_REQUEST)
            
        payload = AppUtils.verify_password_reset_token(token=token)
        if not payload:
            return APIResponse("Invalid or expired token", status=StatusCodes.HTTP_400_BAD_REQUEST)
        email = payload.email
        if not email:
            return APIResponse("Invalid token data", status=StatusCodes.HTTP_400_BAD_REQUEST)
        return await Repository.update_password(
            email, data.new_password, session
        )

    @staticmethod
    async def change_password(request:Request,data: ChangePasswordRequest, session: Session) -> APIResponse:
        # check_old_password

        auth_user:APIResponse = await AppService.authenticate(request)
        if auth_user.status != StatusCodes.HTTP_200_OK:
            return APIResponse(message="Authentication failed", status=auth_user.status)
        old_password = data.old_password
        if not old_password:
            return APIResponse("Old password is required", status=StatusCodes.HTTP_400_BAD_REQUEST)
        if not auth_user.data.get("email"):
            return APIResponse(message="Email not found in token", status=StatusCodes.HTTP_400_BAD_REQUEST)
        if not auth_user.data.get("user_id"):
            return APIResponse(message="User ID not found in token", status=StatusCodes.HTTP_400_BAD_REQUEST)
        if auth_user.data.get("email") != data.email_id:
            return APIResponse(message="Email in token does not match the provided email", status=StatusCodes.HTTP_400_BAD_REQUEST)
        if data.new_password != data.confirm_password:
            return APIResponse(message="Passwords do not match", status=StatusCodes.HTTP_400_BAD_REQUEST)
        
        # verify old password
        email_user = await Repository.get_user_by_email(auth_user.data.get("email"), session)
        if not email_user:
            return APIResponse(message="User not found", status=StatusCodes.HTTP_404_NOT_FOUND)
        if not Utils().verify_password(old_password, email_user.data.password):
            return APIResponse(message="Old password is incorrect", status=StatusCodes.HTTP_401_UNAUTHORIZED)
        
        # update password
        if not email_user.data:
            return APIResponse(message="User ID not found", status=StatusCodes.HTTP_400_BAD_REQUEST)
        if not data.new_password:
            return APIResponse(message="New password is required", status=StatusCodes.HTTP_400_BAD_REQUEST)

        await Repository.update_password(
            email_user.data.email, data.new_password, session
        )

        return APIResponse(
            message="Password changed successfully",
            status=StatusCodes.HTTP_200_OK
        )


    @staticmethod
    async def logout(request:Request, session: Session) -> APIResponse:

        return APIResponse(
            message="Logged out successfully",
            status=StatusCodes.HTTP_200_OK
        )