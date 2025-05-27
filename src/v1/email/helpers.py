from pydantic import BaseModel

class RegisterEmailRequest(BaseModel):
    email:str
    password:str
    confirm_password:str

class LoginEmailRequest(BaseModel):
    email:str
    password:str

