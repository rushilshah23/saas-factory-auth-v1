from dataclasses import dataclass
from src.auth.helpers import UserAuthType
from datetime import datetime
from typing import Dict, Any
from .models import GlobalUser


@dataclass
class GlobalUserDomain:
    id: str
    user_auth_type: UserAuthType
    is_active: bool
    last_login: datetime
    created_at: datetime

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "GlobalUserDomain":
        print("DEBUG ")
        print(dic.get("created_at"))
        return GlobalUserDomain(
            id=dic.get("id"),
            user_auth_type=UserAuthType(dic.get("user_auth_type")),
            is_active=dic.get("is_active"),
            # last_login=datetime.fromisoformat(dic.get("last_login")) if dic.get("last_login") else None,
            # created_at=datetime.fromisoformat(dic.get("created_at")) if dic.get("created_at") else None,
            last_login=dic.get("last_login"),
            created_at=dic.get("created_at")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_auth_type": self.user_auth_type.value,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def from_model(model_obj:GlobalUser) -> 'GlobalUserDomain':
        result = GlobalUserDomain(
            id=model_obj.id,
            user_auth_type=model_obj.user_auth_type,
            is_active=model_obj.is_active,
            last_login=model_obj.last_login,
            created_at=model_obj.created_at
        )
        return result