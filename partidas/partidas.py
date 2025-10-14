# partidas/partidas.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Importações de outros módulos do seu projeto (ajuste os caminhos conforme necessário)
# from app.database import get_async_session
# from app.users.models import User
# from app.users.auth import current_active_user
from .models import Partida
from .schemas import PartidaCreate, PartidaRead

# --- Bloco de Suposições ---
# O código abaixo simula dependências que existiriam em sua aplicação real.
# Remova ou substitua pelas suas implementações reais.

from typing import AsyncGenerator, List
import uuid

# Simulação do get_async_session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    # Em uma aplicação real, isso criaria e fecharia uma sessão com o banco.
    yield None # type: ignore

# Simulação do modelo de usuário
class User:
    id: uuid.UUID = uuid.uuid4()
    is_patient: bool = True
    is_active: bool = True

# Simulação da dependência de usuário logado
async def current_active_user() -> User:
    return User()

# --- Fim do Bloco de Suposições ---


router = APIRouter(
    prefix="/partidas",
    tags=["Partidas"],
)


@router.post("/", response_model=PartidaRead, status_code=status.HTTP_201_CREATED)
async def create_partida(
    partida_in: PartidaCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    """
    Cria uma nova partida para o paciente logado.

    - **Apenas usuários que são pacientes** podem criar partidas.
    - O ID do paciente é obtido automaticamente do usuário autenticado.
    """
    if not current_user.is_patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas pacientes podem registrar partidas.",
        )

    # Cria a instância do modelo SQLAlchemy
    db_partida = Partida(
        **partida_in.model_dump(),
        paciente_id=current_user.id
    )

    # Adiciona ao banco de dados
    db.add(db_partida)
    await db.commit()
    await db.refresh(db_partida)

    return db_partida


@router.get("/", response_model=List[PartidaRead])
async def get_partidas_by_user(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    """
    Retorna uma lista de todas as partidas jogadas pelo paciente logado.

    - **Apenas usuários que são pacientes** podem visualizar seu histórico.
    """
    if not current_user.is_patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas pacientes podem visualizar seu histórico de partidas.",
        )
    
    # Cria a query para selecionar as partidas do paciente
    query = select(Partida).where(Partida.paciente_id == current_user.id)
    
    # Executa a query
    result = await db.execute(query)
    partidas = result.scalars().all()
    
    return partidas