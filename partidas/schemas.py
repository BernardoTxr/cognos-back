# partidas/schemas.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Schema base com os campos comuns
class PartidaBase(BaseModel):
    jogo_id: int
    results: str
    duration: int

# Schema para criação de uma nova partida (o que a API recebe no POST)
class PartidaCreate(PartidaBase):
    pass

# Schema para leitura/retorno de uma partida (o que a API envia como resposta)
class PartidaRead(PartidaBase):
    id: int
    paciente_id: uuid.UUID
    played_at: datetime

    # Configuração para permitir que o Pydantic leia dados de um objeto ORM
    model_config = ConfigDict(from_attributes=True)