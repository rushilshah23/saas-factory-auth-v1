from pydantic import BaseModel
from fastapi import Request
class RegisterEmailRequest(BaseModel):
    email:str
    password:str
    confirm_password:str

class LoginEmailRequest(BaseModel):
    email:str
    password:str






class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    new_password: str
    confirm_password: str


class ChangePasswordRequest(BaseModel):
    email_id:str
    old_password: str
    new_password: str
    confirm_password: str

