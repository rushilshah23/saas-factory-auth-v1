from dataclasses import dataclass
from typing import Dict


@dataclass
class EmailPublicUser:
    email:str
    email_user_id:str
    global_user_id:str


    @staticmethod
    def from_dict(dict:Dict):
        result = EmailPublicUser(
            email=dict.get("email"),
            email_user_id=dict.get("email_user_id"),
            global_user_id=dict.get("global_user_id")
        )
        return result       
    
    def to_dict(self):
        result = {
            "email":self.email,
            "email_user_id":self.email_user_id,
            "global_user_id":self.global_user_id
        }
        return result