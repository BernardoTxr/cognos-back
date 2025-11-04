# define models 
from sqlalchemy import Boolean, Column, Integer, String, UUID, TIMESTAMP
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class partida_JogodaMem(Base):
    __tablename__ = "partida_jogodamem"
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(UUID, index=True)
    clicks = Column(Integer)
    duration = Column(Integer)  # em milisegundos
    played_at = Column(TIMESTAMP, server_default="now()")  # timestamp como string para simplificação

class partida_JogodaBola(Base):
    __tablename__ = "partida_jogodabola"
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(UUID, index=True)
    acertos = Column(Integer)
    duration = Column(Integer)  # em milisegundos
    played_at = Column(TIMESTAMP, server_default="now()")  # timestamp como string para simplificação

class partida_JogoReac(Base):
    __tablename__ = "partida_jogoreac"
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(UUID, index=True)
    reacao = Column(Integer)  # em milisegundos
    played_at = Column(TIMESTAMP, server_default="now()")  # timestamp como string para simplificação

# schema para inserir partidas
from pydantic import BaseModel
class PartidaJogodaMemCreate(BaseModel):
    clicks: int
    duration: int

class PartidaJogodaBolaCreate(BaseModel):
    acertos: int
    duration: int

class PartidaJogoReacCreate(BaseModel):
    reacao: int
