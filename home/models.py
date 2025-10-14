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
    PrimaryKeyConstraint
)
from typing import Optional, List
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base


class Macroarea(Base):
    __tablename__ = "macroarea"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    friendly_name = Column(String)


class MacroareaResponse(BaseModel):
    nome: str
    friendly_name: str


class Mesoarea(Base):
    __tablename__ = "mesoarea"
    id = Column(Integer, primary_key=True)
    id_macroarea = Column(Integer, ForeignKey("macroarea.id"))
    nome = Column(String)
    friendly_name = Column(String)
    descricao = Column(String)


class MesoareaResponse(BaseModel):
    id_macroarea: int
    nome: str
    friendly_name: Optional[str] = None
    descricao: Optional[str] = None


class Microarea(Base):
    __tablename__ = "microarea"
    id = Column(Integer, primary_key=True)
    id_mesoarea = Column(Integer, ForeignKey("mesoarea.id"))
    nome = Column(String)
    friendly_name = Column(String)
    videos_json = Column(String)


class MicroareaResponse(BaseModel):
    id_mesoarea: int
    nome: str
    friendly_name: str
    videos_json: Optional[str] = None


class Lesson(Base):
    __tablename__ = "lesson"
    id = Column(Numeric, primary_key=True)
    id_mesoarea = Column(Integer, ForeignKey("mesoarea.id"), nullable=False)
    id_microarea = Column(Integer, ForeignKey("microarea.id"), nullable=False)
    nivel_associado = Column(Integer, nullable=True)
    ordem_no_nivel = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default="now()")


class LessonResponse(BaseModel):
    id_mesoarea: int
    id_microarea: int
    nivel_associado: Optional[int] = None
    ordem_no_nivel: Optional[int] = None
    type: Optional[str] = None

class Simulados(Base):
    __tablename__ = "simulado"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    id_mesoarea = Column(Integer, ForeignKey("mesoarea.id"), nullable=False)
    nivel_associado = Column(Integer, nullable=True)
    type = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default="now()")


class Question(Base):
    __tablename__ = "question"
    id = Column(Numeric, primary_key=True)
    id_microarea = Column(Integer, ForeignKey("microarea.id"), nullable=False)
    type = Column(String, nullable=False)
    source = Column(String, nullable=True)
    prova = Column(String, nullable=True)
    question_json = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default="now()")

    
class QuestionResquest(BaseModel):
    microarea_id: int
    quantity: int
    nivel_associado: int

class QuestionResponse(BaseModel):
    id_microarea: int
    type: str
    source: Optional[str] = None
    prova: Optional[str] = None
    question_json: Optional[str] = None
    difficulty: int


class UserAtividade(Base):
    __tablename__ = "user_atividade"
    id = Column(Integer, autoincrement=True, primary_key=True)
    id_user = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    id_atividade = Column(Integer, ForeignKey("lesson.id"), nullable=False)
    foiAprovado = Column(Boolean, nullable=False)
    done_at = Column(TIMESTAMP, server_default="now()")
    type = Column(Enum("lesson", "simulado", name="atividadetype"),
        nullable=False,)

class UserAtividadeRequest(BaseModel):
    id_atividade: int
    foiAprovado: bool
    type: str


class UserQuestion(Base):
    __tablename__ = "user_question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    id_question = Column(Integer, ForeignKey("question.id"), nullable=False)
    foiAcerto = Column(Boolean, nullable=False)
    attempted_at = Column(TIMESTAMP, server_default="now()")

class UserQuestionRequest(BaseModel):
    id_question: int
    foiAcerto: bool