from uuid import uuid4
from src.configs.secrets import SecretUtils
from jose import jwt
from datetime import datetime, timedelta, timezone
from src.helpers.token import UserTokenPayload, EmailUserTokenPayload, GoogleUserTokenPayload
from typing import Type

class JWTUtils:
    @staticmethod
    def generate_access_token(payload: UserTokenPayload) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_SECONDS))

    
        payload.exp = int((datetime.now(timezone.utc) + timedelta(seconds=expires_in)).timestamp())

        token = jwt.encode(payload.to_dict(), secret_key, algorithm=algorithm)
        return token

    @staticmethod
    async def verify_access_token(token: str, expected_token_type:Type[UserTokenPayload]) -> UserTokenPayload | None:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        print(f"Verifying token: {token}")
        print(f"Secret key: {secret_key}")
        print(f"Algorithm: {algorithm}")
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            print(f"PAyload - {type(payload)}")
            return expected_token_type(**payload)
        except Exception as e:
            print(e)
            return None
            
        
    @staticmethod
    def generate_refresh_token(payload: UserTokenPayload) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_TOKEN_EXPIRE_SECONDS))
        
        payload.exp = int((datetime.now(timezone.utc) + timedelta(seconds=expires_in)).timestamp())
        
        token = jwt.encode(payload.to_dict(), secret_key, algorithm=algorithm)
        return token

    @staticmethod
    def verify_refresh_token(token: str, expected_token_type:Type[UserTokenPayload]) -> UserTokenPayload | None:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_REFRESH_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return UserTokenPayload(**payload)
        except Exception as e:
            print(e)
            return None
        
    @staticmethod
    def generate_password_reset_token(payload:UserTokenPayload) -> str:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        expires_in = int(SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_TOKEN_EXPIRE_SECONDS))
        payload.exp = int((datetime.now(timezone.utc) + timedelta(seconds=expires_in)).timestamp())
 

        
        token = jwt.encode(payload.to_dict(), secret_key, algorithm=algorithm)
        return token
    
    @staticmethod
    def verify_password_reset_token(token: str, expected_token_type:Type[UserTokenPayload]) -> UserTokenPayload | None:
        secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ACCESS_SECRET_KEY)
        algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.JWT_ALGORITHM)
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return expected_token_type(**payload)
        except Exception as e:
            print(e)
            return None