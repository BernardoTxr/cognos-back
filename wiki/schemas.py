# wiki/schemas.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

# Schema para representar um Tópico
class TopicoWikiBase(BaseModel):
    topico: str

class TopicoWikiCreate(TopicoWikiBase):
    pass

class TopicoWikiRead(TopicoWikiBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Schema base para um Conceito da Wiki
class ConceitoWikiBase(BaseModel):
    topico: int
    conceito: str
    definicao: str

# Schema para criação de um novo conceito (o que a API recebe no POST)
class ConceitoWikiCreate(BaseModel):
    topico: str
    conceito: str
    definicao: str


# Schema para leitura/retorno de um conceito (o que a API envia como resposta)
class ConceitoWikiRead(ConceitoWikiBase):
    id: int
    created_at: datetime
    updated_at: datetime
    topico_rel: TopicoWikiRead  # Relacionamento opcional para incluir detalhes do tópico
    model_config = ConfigDict(from_attributes=True)