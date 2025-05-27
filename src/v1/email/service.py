from .utils import Utils
from .helpers import RegisterEmailRequest, LoginEmailRequest
from src.helpers.response import APIResponse
from .repository import Repository
from sqlmodel import Session

class Service:
    @staticmethod
    async def register(data:RegisterEmailRequest, session:Session) -> APIResponse:
        if data.password != data.confirm_password:
            raise ValueError("Passwords do not match")
        repository_response = await Repository.register(data, session)
        return repository_response


