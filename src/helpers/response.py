from pydantic import BaseModel
from typing import Dict, Optional, Generic, TypeVar


class APIResponse(BaseModel):
    status: int
    message: str
    data: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data if self.data is not None else {}
        }



T = TypeVar("T")

class RepositoryResponse(BaseModel, Generic[T]):
    status: int
    message: str
    data: Optional[T] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data if self.data is not None else {}
        }