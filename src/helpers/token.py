from pydantic import BaseModel
from enum import Enum



class CookieNames(Enum):
    ACCESS_TOKEN= "access_token"
    REFRESH_TOKEN= "refresh_token" 
    
class TokenPayload(BaseModel):
    email: str
    user_id: str
    is_active: bool
    is_verified: bool
    exp:int

    def to_dict(self):
        return self.model_dump()