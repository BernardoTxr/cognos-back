# partidas/models.py

import uuid
from datetime import datetime

from sqlalchemy import (TIMESTAMP, ForeignKey, Integer, String, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

# Supondo que você tenha um arquivo 'database.py' com a Base declarativa
# from app.database import Base
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Partida(Base):
    """
    Modelo ORM para a tabela 'partida'.
    
    Representa uma sessão de jogo de um paciente.
    """
    __tablename__ = "partida"

    # Colunas da tabela
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # A coluna 'jogo_id' no DBML é uuid, mas a tabela 'jogo' tem um id integer.
    # Ajustando para integer para corresponder à PK da tabela 'jogo'.
    jogo_id: Mapped[int] = mapped_column(Integer, ForeignKey("jogo.id"), nullable=False)
    
    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("paciente.user_id"), 
        nullable=False
    )
    
    results: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer) # Duração em segundos
    
    played_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relacionamentos (opcional, mas bom para ORM)
    # paciente = relationship("Paciente", back_populates="partidas")
    # jogo = relationship("Jogo", back_populates="partidas")