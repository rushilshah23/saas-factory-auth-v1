from pydantic import BaseModel
from typing import Dict, Optional

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
