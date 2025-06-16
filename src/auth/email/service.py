from src.utils.jwt import JWTUtils
from src.utils.email import EmailUtils
from src.utils.misc import MiscUtils

from .helpers import (
    RegisterEmailRequest,
    LoginEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)
from src.helpers.response import APIResponse
from sqlmodel import Session
from src.configs.secrets import SecretUtils
from fastapi import Request
from src.helpers.token import EmailUserTokenPayload, UserTokenPayload, TokenEnum
from src.helpers.status_codes import StatusCodes
from fastapi import BackgroundTasks
from src.auth.repository import GlobalUserRepository
from src.auth.domain import GlobalUserDomain
from src.auth.helpers import UserAuthType
from .domain import EmailUserDomain
from .utils import EmailUserUtils
from .repository import EmailUserRepository

class EmailUserService:
    @staticmethod
    async def register(data: RegisterEmailRequest, session: Session, background_tasks: BackgroundTasks) -> APIResponse:
        if data.password != data.confirm_password:
            return APIResponse(message="Passwords do not match", status=StatusCodes.HTTP_400_BAD_REQUEST)

        try:
            global_user_domain_obj = GlobalUserDomain(
                id=MiscUtils.generate_uuid(),
                created_at=MiscUtils.get_current_timestamp(),
                is_active=False,
                last_login=None,
                user_auth_type=UserAuthType.EMAIL
            )
            global_user_response = await GlobalUserRepository.create(obj=global_user_domain_obj, session=session)
            
            if global_user_response.status != StatusCodes.HTTP_201_CREATED or not global_user_response.data:
                await session.rollback()
                return APIResponse(message=global_user_response.message, status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)

            global_user = global_user_response.data

            email_user_domain_obj = EmailUserDomain(
                id=MiscUtils.generate_uuid(),
                email=data.email,
                password=EmailUserUtils.hash_password(data.password),
                email_verified=False,
                global_user_id=global_user.id,
                password_updated_at=None
            )
            email_user_response = await EmailUserRepository.create(data=email_user_domain_obj, session=session)

            if email_user_response.status in [StatusCodes.HTTP_201_CREATED, StatusCodes.HTTP_208_ALREADY_REPORTED]:
                if email_user_response.status == StatusCodes.HTTP_201_CREATED:
                    await session.commit()

                email_user = email_user_response.data
                if email_user is None:
                    await session.rollback()
                    return APIResponse(
                        message="Failed to create email user",
                        status=StatusCodes.HTTP_400_BAD_REQUEST,
                        
                    )
                base_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.SERVER_BASE_URL)

                payload = EmailUserTokenPayload.from_dict(
                    {

                    "email":email_user.email,
                    "email_user_id":email_user.id,
                    "email_verified":email_user.email_verified,
                    "exp":None,
                    "global_user_id":global_user.id,
                    "is_active":global_user.is_active,
                    "token_type":TokenEnum.VERIFY_EMAIL_TOKEN.value
                    }
                )
                token = JWTUtils.generate_access_token(payload)
                verification_link = f"{base_url}/api/auth/email/verify-email?token={token}"
                background_tasks.add_task(
                    EmailUtils.send_email,
                    subject="Verify your email",
                    recipient=email_user.email,
                    body=f"Welcome!\nVerify your email: {verification_link}"
                )
                print("debug 2")

                return APIResponse(
                    message="Email verification link sent",
                    data=payload.to_dict(),
                    status=email_user_response.status
                )

            else:
                await session.rollback()
                return APIResponse(
                    message=email_user_response.message or "Failed to create email user",
                    status=email_user_response.status
                )

        except Exception as e:
            await session.rollback()
            return APIResponse(message=f"EmailUser service error -: {e}", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)


    
    @staticmethod
    async def verify_user(token: str, session: Session) -> APIResponse:
        token_data:EmailUserTokenPayload = await JWTUtils.verify_access_token(token=token, expected_token_type=EmailUserTokenPayload)
        if not token_data:
            return APIResponse(message="Invalid or expired token", status=StatusCodes.HTTP_400_BAD_REQUEST)
        print("======TOKEN DATA==========")
        print(token_data)
        print("==========================")
        email = token_data.email
        email_user_id = token_data.email_user_id
        
        if not email or not email_user_id:
            return APIResponse("Invalid token data", status=StatusCodes.HTTP_400_BAD_REQUEST)
        
        repository_response = await EmailUserRepository.verify_user_email(email, email_user_id, session)
        return APIResponse(status=repository_response.status,
                            message=repository_response.message,
                            data=repository_response.data)

    @staticmethod
    async def login(data: LoginEmailRequest, session: Session) -> APIResponse:
        email_user_repository_response = await EmailUserRepository.get_user_by_email(data.email, session)
        email_user = email_user_repository_response.data
        if not email_user:
            return APIResponse(message=f"Email user {data.email} not found", status=StatusCodes.HTTP_404_NOT_FOUND)
        
        if not email_user.email_verified:
            return APIResponse(message="Email not verified", status=StatusCodes.HTTP_403_FORBIDDEN)
        
        if not EmailUserUtils().verify_password(data.password, email_user.password):
            return APIResponse(message="Invalid credentials", status=StatusCodes.HTTP_401_UNAUTHORIZED)

        payload = EmailUserTokenPayload.from_dict({
            "email":email_user.email,
            "email_user_id":email_user.id,
            "is_active":email_user.email_verified,
            "email_verified":email_user.email_verified,
            "global_user_id":email_user.global_user_id,
            "exp":None,
            "token_type":TokenEnum.ACCESS_TOKEN.value
        }
        )         
        access_token = JWTUtils.generate_access_token(payload)
        refresh_token = JWTUtils.generate_refresh_token(payload)
        if not access_token or not refresh_token:
            return APIResponse("Failed to generate tokens", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token_expires_in_seconds = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_SECONDS))
        print(f"Access token expires in: {access_token_expires_in_seconds} seconds")

        refresh_token_expires_in_seconds = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_SECONDS))
        await EmailUserRepository.update_last_login(email_user.id, session)
        tokens = {
            "access_token": access_token,
            "access_token_expiry": access_token_expires_in_seconds,
            "refresh_token": refresh_token,
            "refresh_token_expiry": refresh_token_expires_in_seconds,
            "user_id": email_user.id,
            "email": email_user.email,

        }
        print(tokens)
        return APIResponse(message="Access token generated",data={"tokens": tokens, "token_type": "bearer" }, status=StatusCodes.HTTP_200_OK)


    @staticmethod
    async def refresh_token(request:Request, session: Session) -> APIResponse:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return APIResponse(message="Missing refresh token", status=StatusCodes.HTTP_401_UNAUTHORIZED)
        payload:EmailUserTokenPayload =  JWTUtils.verify_refresh_token(token=refresh_token, expected_token_type=EmailUserTokenPayload)
        print(refresh_token)
        print(payload)
        if  payload is None:
            return APIResponse(message="Invalid or expired refresh token. Please login again", status=StatusCodes.HTTP_401_UNAUTHORIZED)
        refresh_token_renew_threshold = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_RENEW_THRESHOLD_SECONDS))


        if payload.exp - MiscUtils.get_current_timestamp_numeric() < refresh_token_renew_threshold:
            # Regenerate access and refresh tokens
            access_token = JWTUtils.generate_access_token(payload)
            refresh_token = JWTUtils.generate_refresh_token(payload)
            if not access_token or not refresh_token:
                return APIResponse("Failed to generate tokens", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)
            access_token_expires_in_seconds = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_SECONDS))
            refresh_token_expires_in_seconds = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_SECONDS))
            tokens = {
                "access_token": access_token,
                "access_token_expiry": access_token_expires_in_seconds,
                "refresh_token": refresh_token,
                "refresh_token_expiry": refresh_token_expires_in_seconds,
            }
            return APIResponse(
                message="Tokens renewed successfully",
                data={"tokens": tokens, "token_type": "bearer"},
                status=StatusCodes.HTTP_200_OK
            )
        else:
            return APIResponse(message="Refresh token is still valid, no need to renew", status=StatusCodes.HTTP_208_ALREADY_REPORTED)
        


    @staticmethod
    async def forgot_password(data: ForgotPasswordRequest, session: Session, background_tasks:BackgroundTasks) -> APIResponse:
        email_user_repository_response = await EmailUserRepository.get_user_by_email(data.email, session)
        if  email_user_repository_response.status != StatusCodes.HTTP_200_OK:
            return APIResponse(message="User not found", status=StatusCodes.HTTP_404_NOT_FOUND)
        email_user:EmailUserDomain = email_user_repository_response.data
        if email_user is None:
            return APIResponse(message="User not found", status=StatusCodes.HTTP_404_NOT_FOUND)
        global_user_repository_response = await GlobalUserRepository.get_user_by_global_user_id(global_user_id=email_user.global_user_id,session=session)
        if global_user_repository_response.status != StatusCodes.HTTP_200_OK or email_user_repository_response.status != StatusCodes.HTTP_200_OK:
            return APIResponse(message=f"{data.email} doesn't exists")
        global_user:GlobalUserDomain|None = global_user_repository_response.data
        if global_user is None:
            return APIResponse(message=f"{data.email} doesn't exists")

        payload = EmailUserTokenPayload.from_dict({
            "token_type":TokenEnum.RESET_PASSWORD_TOKEN.value,
            "is_active":global_user.is_active,
            "global_user_id":email_user.global_user_id,
            "email":email_user.email,
            "email_user_id":email_user.id,
            "email_verified":email_user.email_verified,
            "user_type":UserAuthType(UserAuthType.EMAIL.value)
            }
            )
            
        reset_token = JWTUtils.generate_password_reset_token(payload)
        if not reset_token:
            return APIResponse(message="Failed to generate password reset token", status=StatusCodes.HTTP_500_INTERNAL_SERVER_ERROR)
        # send reset token via email
        base_url = SecretUtils.get_secret_value(SecretUtils.SECRETS.CLIENT_BASE_URL)
        reset_link = f"{base_url}/api/auth/email/reset-password?token={reset_token}"
        background_tasks.add_task(
            EmailUtils.send_email,
            subject="Password Reset Request",
            recipient=data.email,
            body=f"To reset your password, please click the following link:\n{reset_link}\n\nIf you did not request this, please ignore this email."
        
        )

        return APIResponse(
            message="Password reset link sent to your email",
            data={"reset_link": reset_link},
            status=StatusCodes.HTTP_200_OK
        )

    @staticmethod
    async def reset_password(data: ResetPasswordRequest, token:str, session: Session) -> APIResponse:
        if data.new_password != data.confirm_password:
            return APIResponse(message="Passwords do not match", status=StatusCodes.HTTP_400_BAD_REQUEST)
            
        payload:EmailUserTokenPayload = JWTUtils.verify_password_reset_token(token=token,expected_token_type=EmailUserTokenPayload)
        if payload is None:
            return APIResponse(message="Invalid or expired token", status=StatusCodes.HTTP_400_BAD_REQUEST)
        if payload.email is None:
            return APIResponse(message="Invalid token data", status=StatusCodes.HTTP_400_BAD_REQUEST)
        update_password_repository_response =  await EmailUserRepository.update_password(
            payload.email, data.new_password, session
        )
        return APIResponse(
            data=None,
            message=update_password_repository_response.message,
            status=update_password_repository_response.status
        )

    @staticmethod
    async def change_password(request:Request,data: ChangePasswordRequest, session: Session) -> APIResponse:
        # check_old_password
        from src.auth.service import GlobalUserService

        auth_user_api_response:APIResponse = await GlobalUserService.authenticate(request)
        if auth_user_api_response.status != StatusCodes.HTTP_200_OK:
            return APIResponse(message="Authentication failed", status=auth_user_api_response.status)
        old_password = data.old_password
        if not old_password:
            return APIResponse(message="Old password is required", status=StatusCodes.HTTP_400_BAD_REQUEST)
        
        auth_user: UserTokenPayload = auth_user_api_response.data
        if auth_user is None:
            return APIResponse(message="Authentication failed", status=StatusCodes.HTTP_401_UNAUTHORIZED)
     
        if data.new_password != data.confirm_password:
            return APIResponse(message="Passwords do not match", status=StatusCodes.HTTP_400_BAD_REQUEST)
        
        # verify old password
        email_user_repository_response = await EmailUserRepository.get_email_user_by_global_user_id(auth_user.global_user_id, session)
        if email_user_repository_response.status != StatusCodes.HTTP_200_OK or email_user_repository_response.data is None:
            return APIResponse(message=email_user_repository_response.message, status=StatusCodes.HTTP_404_NOT_FOUND)
        email_user:EmailUserDomain = email_user_repository_response.data
        if not EmailUserUtils().verify_password(old_password, email_user.password):
            return APIResponse(message="Old password is incorrect", status=StatusCodes.HTTP_401_UNAUTHORIZED)
        
        # update password
        if not data.new_password:
            return APIResponse(message="New password is required", status=StatusCodes.HTTP_400_BAD_REQUEST)

        change_password_repository_response = await EmailUserRepository.update_password(
            email_user.email, data.new_password, session
        )

        return APIResponse(
            message=change_password_repository_response.message,
            status=change_password_repository_response.status,
            
        )


    @staticmethod
    async def logout(request:Request, session: Session) -> APIResponse:

        return APIResponse(
            message="Logged out successfully",
            status=StatusCodes.HTTP_200_OK
        )