from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from dados.models import ConceitosWiki, TopicoWiki, StatusConceito
from .schemas import ConceitoWikiCreate, ConceitoWikiRead, TopicoWikiRead
from database import get_async_session

# Importa usuário real do fastapi-users
from auth.users import current_active_user
from dados.models import Terapeuta

router = APIRouter(
    prefix="/wiki",
    tags=["Wiki"],
)


@router.post("/", response_model=ConceitoWikiRead, status_code=status.HTTP_201_CREATED)
async def create_or_approve_wiki_concept(
    conceito_in: ConceitoWikiCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):
    """
    Cria um conceito wiki:
    - superuser → status = approved automaticamente
    - terapeuta comum → status = pending
    - pacientes → proibido
    """

    terapeuta = await db.get(Terapeuta, current_user.id)

    if not terapeuta and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Apenas terapeutas podem criar wikis."
        )

    query = select(TopicoWiki).where(TopicoWiki.topico == conceito_in.topico)
    result = await db.execute(query)
    topico_existente = result.scalars().first()

    if not topico_existente:
        novo_topico = TopicoWiki(topico=conceito_in.topico)
        db.add(novo_topico)
        await db.commit()
        await db.refresh(novo_topico)
        topico_id = novo_topico.id
    else:
        topico_id = topico_existente.id

    if current_user.is_superuser:
        status_final = StatusConceito.APPROVED
    else:
        status_final = StatusConceito.PENDING

    db_conceito = ConceitosWiki(
        topico=topico_id,
        conceito=conceito_in.conceito,
        definicao=conceito_in.definicao,
        autor_id=current_user.id,
        status=status_final,
    )

    db.add(db_conceito)
    await db.commit()
    await db.refresh(db_conceito)

    return db_conceito

@router.delete("/{conceito_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wiki_concept(
    conceito_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Apenas superusuários podem deletar wikis."
        )

    conceito = await db.get(ConceitosWiki, conceito_id)
    if not conceito:
        raise HTTPException(404, "Conceito não encontrado.")

    await db.delete(conceito)
    await db.commit()

    return None

@router.get("/", response_model=List[ConceitoWikiRead])
async def get_all_wiki_concepts(
    db: AsyncSession = Depends(get_async_session),
):
    query = (
        select(ConceitosWiki)
        .where(ConceitosWiki.status == StatusConceito.APPROVED)
        .options(selectinload(ConceitosWiki.topico_rel))
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/pending", response_model=List[ConceitoWikiRead])
async def get_pending(
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):

    if not current_user.is_superuser:
        raise HTTPException(403, "Apenas superusuários podem ver pendentes.")

    query = (
        select(ConceitosWiki)
        .where(ConceitosWiki.status == StatusConceito.PENDING)
        .options(selectinload(ConceitosWiki.topico_rel))
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/topics", response_model=List[TopicoWikiRead])
async def get_topics(
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):

    query = (
        select(TopicoWiki)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{conceito_id}/approve", response_model=ConceitoWikiRead)
async def approve_concept(
    conceito_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(403, "Apenas superusuários podem aprovar conceitos.")

    conceito = await db.get(ConceitosWiki, conceito_id)
    if not conceito:
        raise HTTPException(404, "Conceito não encontrado.")

    conceito.status = StatusConceito.APPROVED
    await db.commit()
    await db.refresh(conceito)

    return conceito


@router.post("/{conceito_id}/reject", response_model=ConceitoWikiRead)
async def reject_concept(
    conceito_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(403, "Apenas superusuários podem rejeitar conceitos.")

    conceito = await db.get(ConceitosWiki, conceito_id)
    if not conceito:
        raise HTTPException(404, "Conceito não encontrado.")

    conceito.status = StatusConceito.REJECTED
    await db.commit()
    await db.refresh(conceito)

    return conceito
