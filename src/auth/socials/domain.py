from dataclasses import dataclass
from typing import Dict
from .models import SocialUser
from src.auth.helpers import UserAuthType

@dataclass
class SocialUserDomain:
    id: str
    provider_user_id: str
    global_user_id: str
    provider: UserAuthType

    @staticmethod
    def from_dict(dic: Dict) -> "SocialUserDomain":
        return SocialUserDomain(
            id=dic["id"],
            provider_user_id=dic["provider_user_id"],
            global_user_id=dic["global_user_id"],
            provider=UserAuthType(dic["provider"])
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "provider_user_id": self.provider_user_id,
            "global_user_id": self.global_user_id,
            "provider": self.provider.value 
        }

    @staticmethod
    def from_model(model_obj: SocialUser) -> "SocialUserDomain":
        return SocialUserDomain(
            id=model_obj.id,
            provider_user_id=model_obj.provider_user_id,
            global_user_id=model_obj.global_user_id,
            provider=model_obj.provider
        )
