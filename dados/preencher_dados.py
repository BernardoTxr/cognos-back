# Em seu arquivo: preencher_dados.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
# 1. Importe os schemas Pydantic que você acabou de criar
from .schemas import PacientePost, PacienteRead, TerapeutaPost, TerapeutaRead

# Importe os MODELOS ORM (para o Banco de Dados)
from .models import User, Paciente, Terapeuta 

# Importe suas dependências
from database import get_async_session
from auth.users import current_active_user

dados_router = APIRouter(prefix="/preencher_dados", tags=["Preencher Dados"])

@dados_router.post("/paciente", response_model=PacienteRead)
async def post_dados_paciente(
    # 2. Alterado: A função agora espera um objeto 'PacientePost'.
    # O FastAPI valida o corpo da requisição contra este schema automaticamente.
    paciente_data: PacientePost, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    """
    Cria um perfil de paciente para o usuário logado.
    """
    query = select(Paciente).where(Paciente.user_id == current_user.id)
    existing_paciente = await db.execute(query)
    if existing_paciente.scalars().first():
        raise HTTPException(
            status_code=400, detail="Este usuário já possui um perfil de paciente."
        )

    # 3. Alterado: Usamos .dict() para converter o schema Pydantic em um dicionário
    # para instanciar o modelo SQLAlchemy de forma segura. O bloco try/except não é mais necessário.
    db_paciente = Paciente(
        user_id=current_user.id,
        **paciente_data.dict()
    )
    
    current_user.is_patient = True
    
    db.add(db_paciente)
    db.add(current_user)
    await db.commit()
    await db.refresh(db_paciente)
    
    # 4. O objeto 'db_paciente' será filtrado e formatado pelo 'response_model=PacienteRead'
    return db_paciente


@dados_router.post("/terapeuta", response_model=TerapeutaRead)
async def post_dados_terapeuta(
    # 2. Alterado: A função agora espera um objeto 'TerapeutaPost'.
    terapeuta_data: TerapeutaPost,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    """
    Cria um perfil de terapeuta para o usuário logado.
    """
    query = select(Terapeuta).where(Terapeuta.user_id == current_user.id)
    existing_terapeuta = await db.execute(query)
    if existing_terapeuta.scalars().first():
        raise HTTPException(
            status_code=400, detail="Este usuário já possui um perfil de terapeuta."
        )

    # 3. Alterado: Usamos .dict() para instanciar o modelo SQLAlchemy.
    db_terapeuta = Terapeuta(
        user_id=current_user.id,
        **terapeuta_data.dict()
    )
    
    current_user.is_patient = False
    
    db.add(db_terapeuta)
    db.add(current_user)
    await db.commit()
    await db.refresh(db_terapeuta)
    
    # 4. A resposta será formatada pelo schema 'TerapeutaRead'.
    return db_terapeuta