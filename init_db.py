from sqlmodel import SQLModel
from src.db import engine
from src.v1.email.model import EmailUser
import asyncio

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)
#     print("Database and tables created successfully.")




async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Database and tables created successfully.")


if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
