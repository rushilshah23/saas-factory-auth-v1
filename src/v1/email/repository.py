from src.db import SessionDependency
from .helpers import RegisterEmailRequest
from .model import EmailUser
from src.utils import Utils
from .utils import Utils as EmailUtils
from src.helpers.response import APIResponse
from sqlmodel.ext.asyncio.session import AsyncSession
class Repository:
    
    @staticmethod
    async def register(data:RegisterEmailRequest, session:AsyncSession) -> APIResponse:
        try:
            
            new_user = EmailUser(
                id = Utils.generate_uuid(),
                email = data.email,
                password = EmailUtils.hash_password(data.password), 
            )
            session.add(new_user)
            await session.commit()
            return APIResponse(
                status=201,
                message="User registered successfully",
                data={"email": new_user.email}
            )
        except Exception as e:
            return APIResponse(
                status=500,
                message=f"An error occurred: {str(e)}"
            )
