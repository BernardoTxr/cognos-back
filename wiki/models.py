# wiki/models.py

import uuid
from datetime import datetime

from sqlalchemy import (TIMESTAMP, Boolean, Column, ForeignKey, Integer, String,
                        Text, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

# Supondo que você tenha um arquivo 'database.py' com a Base declarativa
# from app.database import Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TopicoWiki(Base):
    """
    Modelo ORM para a tabela 'topico_wiki'.
    
    Representa uma categoria ou tópico para os conceitos da Wiki.
    """
    __tablename__ = "topico_wiki"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topico: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Relacionamento com ConceitosWiki
    conceitos = relationship("ConceitosWiki", back_populates="topico_rel")


class ConceitosWiki(Base):
    """
    Modelo ORM para a tabela 'conceitos_wiki'.
    
    Representa uma definição de um conceito escrito por um terapeuta.
    """
    __tablename__ = "conceitos_wiki"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conceito: Mapped[str] = mapped_column(String, nullable=False)
    definicao: Mapped[str] = mapped_column(Text, nullable=False) # Usando Text para definições mais longas
    
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("terapeuta.user_id"), 
        nullable=False,
        name="autor" # Mantendo o nome da coluna do DBML
    )

    # A coluna 'topico' no DBML refere-se a 'topico_wiki.id', então o nome correto
    # da coluna de chave estrangeira seria 'topico_id'
    topico_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("topico_wiki.id"),
        nullable=False,
        name="topico" # Mantendo o nome da coluna do DBML
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamentos
    topico_rel = relationship("TopicoWiki", back_populates="conceitos")
    # autor_rel = relationship("Terapeuta")