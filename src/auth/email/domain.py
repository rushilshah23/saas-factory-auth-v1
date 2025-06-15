from dataclasses import dataclass
from typing import Dict
from datetime import datetime
from .models import EmailUser


@dataclass
class EmailUserDomain:
    id: str 
    email: str 
    password: str 
    email_verified: bool 
    global_user_id: str 
    password_updated_at: datetime 

    @staticmethod
    def from_dict(dic: Dict):
        result = EmailUserDomain(
            id=dic.get("id"),
            email=dic.get("email"),
            password=dic.get("password"),
            email_verified=dic.get("email_verified"), 
            global_user_id=dic.get("global_user_id"),
            password_updated_at=dic.get("password_updated_at")
        )
        return result       

    def to_dict(self):
        result = {
            "id": self.id,
            "email": self.email,
            "password":self.password,
            "email_verified": self.email_verified,
            "global_user_id": self.global_user_id,
            "password_updated_at": self.password_updated_at.isoformat() if self.password_updated_at else None
        }
        return result

    @staticmethod
    def from_model(model_obj:EmailUser):
        result = EmailUserDomain(
            id=model_obj.id,
            email=model_obj.email,
            email_verified=model_obj.email_verified,
            global_user_id=model_obj.global_user_id,
            password=model_obj.password,
            password_updated_at=model_obj.password_updated_at
        )
        return result