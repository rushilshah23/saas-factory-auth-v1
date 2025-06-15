from __future__ import annotations
import os
from typing import Dict, Optional
from enum import Enum
import json

class SecretUtils:
    COLLECTED_SECRETS: Dict[str, str] = {}

    class SECRETS(Enum):
        SECRET_KEY="SECRET_KEY"
        ALGORITHM="ALGORITHM"
        DB_URI="DB_URI"

        EMAIL_HOST="EMAIL_HOST"
        EMAIL_PORT="EMAIL_PORT"
        EMAIL_USER="EMAIL_USER"
        EMAIL_PASSWORD="EMAIL_PASSWORD"
        EMAIL_FROM_NAME="EMAIL_FROM_NAME"
        SERVER_BASE_URL="SERVER_BASE_URL"
        CLIENT_BASE_URL="CLIENT_BASE_URL"
        JWT_ACCESS_SECRET_KEY="JWT_ACCESS_SECRET_KEY"
        JWT_REFRESH_SECRET_KEY="JWT_REFRESH_SECRET_KEY"
        JWT_ALGORITHM="JWT_ALGORITHM"
        JWT_ACCESS_TOKEN_EXPIRE_SECONDS="JWT_ACCESS_TOKEN_EXPIRE_SECONDS"
        JWT_REFRESH_TOKEN_EXPIRE_SECONDS="JWT_REFRESH_TOKEN_EXPIRE_SECONDS"
        JWT_REFRESH_TOKEN_RENEW_THRESHOLD_SECONDS="JWT_REFRESH_TOKEN_RENEW_THRESHOLD_SECONDS"
        GOOGLE_CLIENT_ID="GOOGLE_CLIENT_ID"
        GOOGLE_CLIENT_SECRET="GOOGLE_CLIENT_SECRET"
        GOOGLE_REDIRECT_URI="GOOGLE_REDIRECT_URI"

    @staticmethod
    def collect_secrets():
        for SECRET in SecretUtils.SECRETS:
            env_secret_value = os.environ.get(SECRET.value)
            if env_secret_value is not None:
                secret_value = env_secret_value
            SecretUtils.COLLECTED_SECRETS[SECRET.value] = secret_value


    @staticmethod
    def get_secret_value(secret: SecretUtils.SECRETS) -> Optional[str]:
        secret_value = SecretUtils.COLLECTED_SECRETS.get(secret.value)
        env_secret_value = os.environ.get(secret.value)
        if env_secret_value is not None and (isinstance(env_secret_value,str) and len(env_secret_value) > 0):
            secret_value = env_secret_value
        return secret_value

    @staticmethod
    def set_secret_value(secret: SecretUtils.SECRETS, value: str):
        SecretUtils.COLLECTED_SECRETS[secret.value] = value