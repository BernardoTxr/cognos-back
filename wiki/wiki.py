# wiki/wiki.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .models import ConceitosWiki
from .schemas import ConceitoWikiCreate, ConceitoWikiRead
from database import get_async_session
from .models import TopicoWiki


# --- Bloco de Suposições ---
# O código abaixo simula dependências que existiriam em sua aplicação real.
# Remova ou substitua pelas suas implementações reais.

from typing import AsyncGenerator
import uuid

# Simulação do modelo de usuário
class User:
    id: uuid.UUID = uuid.uuid4()
    is_superuser: bool = False
    is_active: bool = True

# Simulação de um superusuário para os testes
def get_superuser() -> User:
    user = User()
    user.is_superuser = True
    return user

# Simulação da dependência de usuário logado
async def current_active_user() -> User:
    # Para testar, você pode alternar entre User() e get_superuser()
    return get_superuser()

# --- Fim do Bloco de Suposições ---


router = APIRouter(
    prefix="/wiki",
    tags=["Wiki"],
)

@router.post("/", response_model=ConceitoWikiRead, status_code=status.HTTP_201_CREATED)
async def create_wiki_concept(
    conceito_in: ConceitoWikiCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente. Apenas superusuários podem criar wikis.",
        )

    # ===============================
    # 1. VERIFICAR / CRIAR TÓPICO
    # ===============================
    nome_topico = conceito_in.topico  # nome enviado no front

    query = select(TopicoWiki).where(TopicoWiki.topico == nome_topico)
    result = await db.execute(query)
    topico_existente = result.scalars().first()

    if not topico_existente:
        # criar novo tópico
        novo_topico = TopicoWiki(topico=nome_topico)
        db.add(novo_topico)
        await db.commit()
        await db.refresh(novo_topico)
        topico_id = novo_topico.id
    else:
        topico_id = topico_existente.id

    # ===============================
    # 2. CRIAR CONCEITO
    # ===============================

    db_conceito = ConceitosWiki(
        topico=topico_id,  # <- ESTE é o campo correto (ID do tópico)
        conceito=conceito_in.conceito,
        definicao=conceito_in.definicao )

    db.add(db_conceito)
    await db.commit()
    await db.refresh(db_conceito)

    return db_conceito

@router.delete("/{conceito_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wiki_concept(
    conceito_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    """
    Deleta um conceito da Wiki pelo seu ID.

    - **Apenas superusuários** podem deletar conceitos.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente. Apenas superusuários podem deletar wikis.",
        )

    # Primeiro, busca o conceito no banco de dados
    conceito = await db.get(ConceitosWiki, conceito_id)
    if not conceito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conceito com ID {conceito_id} não encontrado.",
        )
    
    await db.delete(conceito)
    await db.commit()

    return None

@router.get("/", response_model=List[ConceitoWikiRead])
async def get_all_wiki_concepts(
    db: AsyncSession = Depends(get_async_session),
):
    """
    Retorna uma lista de todos os conceitos da Wiki.
    
    - Esta rota é pública e não requer autenticação especial.
    """
    # Usamos selectinload para otimizar a query e já carregar os tópicos relacionados
    # evitando o problema de N+1 queries.
    query = select(ConceitosWiki).options(selectinload(ConceitosWiki.topico_rel))
    result = await db.execute(query)
    conceitos = result.scalars().all()
    
    return conceitos