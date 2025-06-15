
from email.message import EmailMessage
from src.configs.secrets import SecretUtils
import aiosmtplib


class EmailUtils:
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
