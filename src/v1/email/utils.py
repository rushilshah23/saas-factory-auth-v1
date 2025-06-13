from passlib.context import CryptContext
# from jose import jwt
from datetime import datetime, timedelta
from src.configs.secrets import SecretUtils

class Utils():

    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
    _secret_key = SecretUtils.get_secret_value(SecretUtils.SECRETS.SECRET_KEY)
    _algorithm = SecretUtils.get_secret_value(SecretUtils.SECRETS.ALGORITHM)

    @classmethod
    def hash_password(cls,password: str) -> str:
        return cls._pwd_context.hash(password)

    @classmethod
    def verify_password(cls,plain: str, hashed: str) -> bool:
        return cls._pwd_context.verify(plain, hashed)
    
    @classmethod
    def set_cookie(cls, response, key: str, value: str, expires: int) -> None:
        response.set_cookie(
            key=key,
            value=value,
            httponly=True,
            secure=True,
            samesite="Strict",
            expires=expires
        )


