from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.v1.helpers import UserAuthType


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(primary_key=True)
    user_auth_type: UserAuthType = Field(nullable=False)
    is_active: bool = Field(default=True)
    last_login: str = Field(default=None, nullable=True)