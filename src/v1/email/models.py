from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select






class EmailUser(SQLModel, table=True):
    __tablename__ = "email_users"
    id: str = Field(primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    email_verified: bool = Field(default=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)

