from pydantic import BaseModel
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Numeric,
    TIMESTAMP,
    JSON,
    Integer,
    Boolean,
    Enum,
)
from typing import Any, Optional
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base


class UserFriend(Base):
    __tablename__ = "user_friend"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid1 = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uid2 = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum("req_uid1", "req_uid2", "friends", name="FriendStatus"),
        nullable=False,
    )


class DueloStatusEnum(str, Enum):
    waiting_u1 = "waiting_u1"
    waiting_u2 = "waiting_u2"
    show_results = "show_results"  # apenas para u1
    ended = "ended"


class DueloResultsEnum(str, Enum):
    win_u1 = "win_u1"
    win_u2 = "win_u2"
    waiting_results = "waiting_results"


class Duelo(Base):
    __tablename__ = "duelo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid1 = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )  # desafiador
    uid2 = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )  # desafiado
    id_mesoarea = Column(Integer, ForeignKey("mesoarea.id"), nullable=False)
    rounds = Column(Integer, nullable=False)

    # 👇 mesmo estilo do UserFriend
    status = Column(
        Enum("waiting_u1", "waiting_u2", "show_results", "ended", name="DueloStatus"),
        nullable=False,
    )
    resultado = Column(
        Enum("win_u1", "win_u2", "waiting_results", name="DueloResults"),
        nullable=False,
    )


class DueloQuestion(Base):
    __tablename__ = "duelo_question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_question = Column(Integer, ForeignKey("question.id"), nullable=False)
    id_duelo = Column(Integer, ForeignKey("duelo.id"), nullable=False)
    foiAcerto_u1 = Column(Boolean, default=False)
    foiAcerto_u2 = Column(Boolean, default=False)
