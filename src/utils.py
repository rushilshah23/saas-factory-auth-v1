from uuid import uuid4
import smtplib
from email.message import EmailMessage
from src.configs.secrets import SecretUtils
from jose import jwt
from datetime import datetime, timedelta, timezone
class Utils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid4())
    
    @staticmethod
    def get_current_timestamp() -> str:
        # return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return int(datetime.now(timezone.utc).timestamp())


    @staticmethod
    async def send_email(subject: str, recipient: str, body: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_FROM_NAME) + " <" + SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_USER) + ">"
        msg["To"] = recipient
        msg.set_content(body)

        try:
            with smtplib.SMTP(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_HOST), int(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_PORT))) as smtp:
                smtp.starttls()
                smtp.login(SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_USER), SecretUtils.get_secret_value(SecretUtils.SECRETS.EMAIL_PASSWORD))
                smtp.send_message(msg)
                print(f"✅ Email sent to {recipient}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")


    @staticmethod
    def generate_access_token(payload: dict) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))

        payload_copy = payload.copy()
        payload_copy["exp"] = int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp())

        token = jwt.encode(payload_copy, secret_key, algorithm=algorithm)
        return token

    @staticmethod
    async def verify_access_token(token: str) -> dict:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        print(f"Verifying token: {token}")
        print(f"Secret key: {secret_key}")
        print(f"Algorithm: {algorithm}")
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Access token has expired.")
            return {}
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid access token: {e}")
            return {}
        
    @staticmethod
    def generate_refresh_token(payload: dict) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES))
        
        payload_copy = payload.copy()
        payload_copy["exp"] = int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp())
        
        token = jwt.encode(payload_copy, secret_key, algorithm=algorithm)
        print(f"Generated token exp: {payload_copy['exp']}")
        print(f"Current UTC: {datetime.utcnow().timestamp()}")
        return token

    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Refresh token has expired.")
            return {}
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid refresh token: {e}")
            return {}
        
    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        
        payload = {
            "email": email,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp())
        }
        
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        return token
    
    @staticmethod
    def verify_password_reset_token(token: str) -> dict:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Password reset token has expired.")
            return {}
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid password reset token: {e}")
            return {}