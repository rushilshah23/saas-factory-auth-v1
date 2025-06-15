from pydantic import BaseModel
from typing import Dict, Optional, Generic, TypeVar
from src.helpers.status_codes import StatusCodes
T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    status: StatusCodes
    message: str
    data: Optional[T] = None

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "message": self.message,
             "data": self.data.to_dict() if self.data is not None and hasattr(self.data, "to_dict") else self.data
        }




class RepositoryResponse(BaseModel, Generic[T]):
    status: StatusCodes
    message: str
    data: Optional[T] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data.to_dict() if self.data is not None else {}
        }