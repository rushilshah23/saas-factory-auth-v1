from uuid import uuid4
import smtplib
from email.message import EmailMessage
from src.configs.secrets import SecretUtils

class Utils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid4())
    


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