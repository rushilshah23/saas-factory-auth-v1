from pydantic import BaseModel
from typing import Dict, Optional, Generic, TypeVar
from src.helpers.status_codes import StatusCodes

class APIResponse(BaseModel):
    status: StatusCodes
    message: str
    data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data if self.data is not None else {}
        }



T = TypeVar("T")

class RepositoryResponse(BaseModel, Generic[T]):
    status: StatusCodes
    message: str
    data: Optional[T] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data if self.data is not None else {}
        }