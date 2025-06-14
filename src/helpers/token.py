from pydantic import BaseModel
from enum import Enum



class CookieNames(Enum):
    ACCESS_TOKEN= "access_token"
    REFRESH_TOKEN= "refresh_token" 
    
class TokenPayload(BaseModel):
    email: str
    email_user_id: str
    global_user_id:str
    is_active: bool | None
    is_verified: bool
    exp:int | None = None

    def to_dict(self):
        return self.model_dump()