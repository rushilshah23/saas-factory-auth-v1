from uuid import uuid4
from datetime import datetime, timezone


class MiscUtils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid4())
    
    @staticmethod
    def get_current_timestamp_numeric() -> int:
        # return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return int(datetime.now(timezone.utc).timestamp())

    @staticmethod
    def get_current_timestamp() -> datetime:
        """Return UTC aware datetime for DB storage."""
        return datetime.now(timezone.utc)
