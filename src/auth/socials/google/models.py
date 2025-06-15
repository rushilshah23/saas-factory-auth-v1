from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.auth.helpers import UserAuthType
from src.utils import Utils as AppUtils
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


class GoogleUser(SQLModel, table=True):
    __tablename__ = "google_users"
    id: str = Field(primary_key=True)
    social_user_id:str = Field(foreign_key="social_users.id")
    provider_user_id:str = Field(unique=True, nullable=False)