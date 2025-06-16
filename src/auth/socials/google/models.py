from sqlmodel import Field, Session, SQLModel, create_engine, select



class GoogleUser(SQLModel, table=True):
    __tablename__ = "google_users"
    id: str = Field(primary_key=True)
    social_user_id:str = Field(foreign_key="social_users.id")
    provider_user_id:str = Field(unique=True, nullable=False)
    email:str = Field(unique=True, nullable=False)