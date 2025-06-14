from uuid import uuid4
import smtplib
from email.message import EmailMessage
from src.configs.secrets import SecretUtils
from jose import jwt
from datetime import datetime, timedelta, timezone
from src.helpers.token import TokenPayload
import aiosmtplib
import time

class Utils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid4())
    
    @staticmethod
    def get_current_timestamp_numeric() -> int:
        # return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return int(datetime.now(timezone.utc).timestamp())

    @staticmethod
    def get_current_timestamp() -> datetime:
        """Return UTC aware datetime for DB storage."""
        return datetime.now(timezone.utc)


    # @staticmethod
    # async def send_email(subject: str, recipient: str, body: str) -> None:
    #     msg = EmailMessage()
    #     msg["Subject"] = subject
    #     msg["From"] = SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_FROM_NAME) + " <" + SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_USER) + ">"
    #     msg["To"] = recipient
    #     msg.set_content(body)

    #     try:
    #         with smtplib.SMTP(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_HOST), int(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_PORT))) as smtp:
    #             smtp.starttls()
    #             smtp.login(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_USER), SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_PASSWORD))
    #             smtp.send_message(msg)
    #             print(f"✅ Email sent to {recipient}")
    #     except Exception as e:
    #         print(f"❌ Failed to send email: {e}")


    @staticmethod
    async def send_email(subject: str, recipient: str, body: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_FROM_NAME) + " <" + SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_USER) + ">"
        msg["To"] = recipient
        msg.set_content(body)

        try:
            await aiosmtplib.send(
                msg,
                hostname=SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_HOST),
                port=int(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_PORT)),
                start_tls=True,
                username=SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_USER),
                password=SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_PASSWORD)
            )
            print(f"✅ Email sent to {recipient}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    @staticmethod
    def generate_access_token(payload: TokenPayload) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))

    
        payload.exp = int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp())

        token = jwt.encode(payload.to_dict(), secret_key, algorithm=algorithm)
        return token

    @staticmethod
    async def verify_access_token(token: str) -> TokenPayload:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        print(f"Verifying token: {token}")
        print(f"Secret key: {secret_key}")
        print(f"Algorithm: {algorithm}")
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            print("❌ Access token has expired.")
            return {}
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid access token: {e}")
            return {}
        
    @staticmethod
    def generate_refresh_token(payload: TokenPayload) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES))
        
        payload.exp = int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp())
        
        token = jwt.encode(payload.to_dict(), secret_key, algorithm=algorithm)
        return token

    @staticmethod
    def verify_refresh_token(token: str) -> TokenPayload:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            print("❌ Refresh token has expired.")
            return {}
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid refresh token: {e}")
            return {}
        
    @staticmethod
    def generate_password_reset_token(payload:TokenPayload) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        payload.exp = int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp())
 

        
        token = jwt.encode(payload.to_dict(), secret_key, algorithm=algorithm)
        return token
    
    @staticmethod
    def verify_password_reset_token(token: str) -> TokenPayload:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            print("❌ Password reset token has expired.")
            return {}
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid password reset token: {e}")
            return {}