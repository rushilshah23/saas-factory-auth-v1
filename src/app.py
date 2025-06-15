from fastapi import FastAPI
from src.configs.secrets import SecretUtils
from init_db import create_db_and_tables
from contextlib import asynccontextmanager

SecretUtils.collect_secrets()
print(SecretUtils.COLLECTED_SECRETS)


@asynccontextmanager
async def lifespan(app:FastAPI):
    yield

def create_api():
    api = FastAPI(title="Authentication Microservice", lifespan=lifespan)



    from src.auth import router
    api.include_router(router, prefix="/api")
    
    
    return api

