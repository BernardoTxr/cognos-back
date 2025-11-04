# Em seu arquivo schemas.py

import uuid
from datetime import date
from pydantic import BaseModel

# Importe os Enums do seu arquivo de modelos para manter a consistência.
from .models import sexo, nivel_tea

# ===================================================================
# Schemas para a rota POST (Entrada de Dados) - SEM USAR Field
# ===================================================================

class PacientePost(BaseModel):
    """
    Schema para validar os dados enviados para criar um novo Paciente.
    """
    # Campos requeridos são definidos apenas com seu tipo.
    nome_completo: str
    data_de_nascimento: date
    cpf: str  # A validação detalhada foi removida, mas o tipo 'str' é garantido.
    sexo: sexo
    nivel_tea: nivel_tea

class TerapeutaPost(BaseModel):
    """
    Schema para validar os dados enviados para criar um novo Terapeuta.
    """
    nome_completo: str
    
    # Para um campo opcional, declare o tipo e atribua 'None' como valor padrão.
    documento: str | None = None

# ===================================================================
# Schemas para a resposta da API (Saída de Dados)
# ===================================================================

class PacienteRead(PacientePost):
    """
    Schema para retornar os dados de um Paciente. Herda de PacientePost
    e adiciona o campo user_id.
    """
    user_id: uuid.UUID

    class Config:
        # Permite que o Pydantic leia dados de um objeto SQLAlchemy
        orm_mode = True

class TerapeutaRead(TerapeutaPost):
    """
    Schema para retornar os dados de um Terapeuta. Herda de TerapeutaPost
    e adiciona o campo user_id.
    """
    user_id: uuid.UUID
    
    class Config:
        orm_mode = True