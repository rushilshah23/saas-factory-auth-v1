from uuid import uuid4


class Utils:
    @staticmethod
    def generate_uuid() -> str:
        return str(uuid4())