import logging
from fastapi import FastAPI, Request

# Configure logging (you can customize this)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cookie-logger")


async def log_request_cookies(request: Request, call_next):
    cookies = request.cookies
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    logger.info(
        f"[{request.method}] {request.url.path} | IP: {client_ip} | User-Agent: {user_agent} | Cookies: {cookies or 'None'}"
    )

    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
