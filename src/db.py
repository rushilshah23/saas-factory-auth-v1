# # ===================== Synchronous =============================
# from sqlmodel import create_engine, Session
# from src.configs.secrets import SecretUtils
# from typing import Annotated
# from fastapi import Depends

# db_uri = SecretUtils.get_secret_value(SecretUtils.SECRETS.DB_URI)

# if db_uri is None:
#     raise ValueError("Database URI is not set in the environment variables.")


# engine = create_engine(db_uri, echo=True)


# def get_session():
#     with Session(engine) as session:
#         yield session


# SessionDependency = Annotated[Session, Depends(get_session)]

# ===================== Asynchronous ============================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Annotated
from fastapi import Depends
from src.configs.secrets import SecretUtils

# ✅ Get async DB URI like: 'postgresql+asyncpg://user:pass@host/db'
db_uri = SecretUtils.get_secret_value(SecretUtils.SECRETS.DB_URI)

if db_uri is None:
    raise ValueError("Database URI is not set in the environment variables.")

# ✅ Create async engine
engine = create_async_engine(db_uri, echo=True)

# ✅ Async sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# ✅ Dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# ✅ Dependency type
SessionDependency = Annotated[AsyncSession, Depends(get_session)]
