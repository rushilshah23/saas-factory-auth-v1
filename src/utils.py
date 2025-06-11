from uuid import uuid4
import smtplib
from email.message import EmailMessage
from src.configs.secrets import SecretUtils
from jose import jwt
from datetime import datetime, timedelta
class Utils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid4())
    
    @staticmethod
    def get_current_timestamp() -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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
    async def generate_access_token(payload: dict) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_SECRET_KEY)
        algorithm = "HS256"
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
        payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_in)
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        return token
    
    @staticmethod
    async def verify_access_token(token: str) -> dict:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.JWTError as e:
            print(f"❌ Token verification failed: {e}")
            return {}