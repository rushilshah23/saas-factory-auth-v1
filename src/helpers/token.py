from pydantic import BaseModel
from enum import Enum
from src.auth.helpers import UserAuthType
from typing import Literal, Dict, Type, TypeVar

class TokenEnum(Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    VERIFY_EMAIL_TOKEN = "verify_email_token"
    RESET_PASSWORD_TOKEN = "reset_password_token"

class UserTokenPayload(BaseModel):
    token_type: TokenEnum
    user_type: UserAuthType
    is_active: bool
    global_user_id: str
    exp: int | None = None

    def to_dict(self):
        return {
            "token_type": self.token_type.value,
            "user_type": self.user_type.value,
            "is_active": self.is_active,
            "global_user_id": self.global_user_id,
            "exp": self.exp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "UserTokenPayload":
        return cls(
            token_type=TokenEnum(data["token_type"]),
            user_type=UserAuthType(data["user_type"]),
            is_active=data["is_active"],
            global_user_id=data["global_user_id"],
            exp=data.get("exp")
        )

class EmailUserTokenPayload(UserTokenPayload):
    email: str
    email_user_id: str
    email_verified: bool

    def to_dict(self):
        result = super().to_dict()
        result.update({
            "email": self.email,
            "email_user_id": self.email_user_id,
            "email_verified": self.email_verified,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "EmailUserTokenPayload":
        return cls(
            token_type=TokenEnum(data["token_type"]),
            is_active=data["is_active"],
            global_user_id=data["global_user_id"],
            exp=data.get("exp"),
            email=data["email"],
            email_user_id=data["email_user_id"],
            email_verified=data["email_verified"],
            user_type=UserAuthType(UserAuthType.EMAIL.value)
        )

class GoogleUserTokenPayload(UserTokenPayload):
    email: str
    provider_user_id:str

    def to_dict(self):
        result = super().to_dict()
        result.update({
            "email": self.email,
            "provider_user_id":self.provider_user_id
          
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "GoogleUserTokenPayload":
        return cls(
            token_type=TokenEnum(data["token_type"]),
            is_active=data["is_active"],
            global_user_id=data["global_user_id"],
            exp=data.get("exp"),
            email=data["email"],
            provider_user_id=data["provider_user_id"],
            user_type=UserAuthType(UserAuthType.GOOGLE.value)

        )
