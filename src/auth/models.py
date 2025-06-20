from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.auth.helpers import UserAuthType
from src.utils.misc import MiscUtils
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


class GlobalUser(SQLModel, table=True):
    __tablename__ = "global_users"
    id: str = Field(primary_key=True)
    user_auth_type: UserAuthType = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    last_login: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, default=None)
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, default=MiscUtils.get_current_timestamp())
    )