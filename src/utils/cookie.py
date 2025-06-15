class CookieUtils:
    @classmethod
    def set_cookie(cls, response, key: str, value: str, expires: int) -> None:
        response.set_cookie(
            key=key,
            value=value,
            httponly=True,
            secure=True,
            samesite="Strict",
            expires=expires
        )
