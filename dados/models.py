# Em seu arquivo models.py

import uuid
from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Date,
    Enum as SAEnum,
    Boolean # Adicionado para o campo is_patient
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

# --- Base Declarativa (você já deve ter isso) ---
# Todos os seus modelos devem herdar da mesma Base
Base = declarative_base()

# --- Modelo User (Verifique se ele herda da sua Base) ---
class User(SQLAlchemyBaseUserTableUUID, Base):
    # Seus campos da tabela 'users'
    __tablename__ = "users"
    username = Column(String, nullable=False, unique=True)
    is_patient = Column(Boolean, default=None, nullable=True) # Campo para diferenciar os perfis
    # Outros campos do fastapi-users (email, hashed_password, etc.) já estão incluídos

# --- Enums para os Tipos de Dados ---
class sexo(str, PyEnum):
    MASCULINO = "masc"
    FEMININO = "fem"

class nivel_tea(str, PyEnum):
    NIVEL_1 = "nivel_1"
    NIVEL_2 = "nivel_2"
    NIVEL_3 = "nivel_3"

# ===================================================================
# AQUI ESTÁ A CLASSE QUE FALTAVA
# ===================================================================
class Paciente(Base):
    """
    Este é o Modelo ORM do SQLAlchemy que mapeia para a tabela 'paciente'.
    """
    __tablename__ = "paciente"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    nome_completo = Column(String, nullable=False)
    data_de_nascimento = Column(Date, nullable=False)
    cpf = Column(String(11), nullable=False, unique=True)
    sexo = Column(SAEnum(sexo), nullable=False, name='sexo')
    nivel_tea = Column(SAEnum(nivel_tea), nullable=False, name='nivel_tea')


# --- Modelo Terapeuta (para consistência) ---
class Terapeuta(Base):
    """Modelo ORM do SQLAlchemy para a tabela 'terapeuta'."""
    __tablename__ = "terapeuta"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    nome_completo = Column(String, nullable=False)
    documento = Column(String, nullable=True)

    