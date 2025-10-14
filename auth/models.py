from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, Numeric, TIMESTAMP
from database import Base
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str

    class Config:
        from_attributes = True


class UserUpdate(schemas.BaseUserUpdate):
    username: str

    class Config:
        from_attributes = True
