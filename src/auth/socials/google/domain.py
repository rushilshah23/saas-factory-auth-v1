from dataclasses import dataclass
from typing import Dict
from .models import GoogleUser

@dataclass
class GoogleUserDomain:
    id: str
    social_user_id: str
    provider_user_id: str
    email: str

    @staticmethod
    def from_dict(dic: Dict) -> "GoogleUserDomain":
        return GoogleUserDomain(
            id=dic["id"],
            social_user_id=dic["social_user_id"],
            provider_user_id=dic["provider_user_id"],
            email=dic["email"]
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "social_user_id": self.social_user_id,
            "provider_user_id": self.provider_user_id,
            "email": self.email
        }

    @staticmethod
    def from_model(model_obj: GoogleUser) -> "GoogleUserDomain":
        return GoogleUserDomain(
            id=model_obj.id,
            social_user_id=model_obj.social_user_id,
            provider_user_id=model_obj.provider_user_id,
            email=model_obj.email
        )
