from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.auth.helpers import UserAuthType
from src.utils.misc import MiscUtils
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime

class SocialUser(SQLModel, table=True):
    __tablename__ = "social_users"
    id: str = Field(primary_key=True)
    provider_user_id:str = Field(unique=True, nullable=False)
    global_user_id:str = Field(foreign_key="global_users.id")
    provider: UserAuthType = Field(nullable=False)



