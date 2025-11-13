from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from partidas.models import partida_JogodaMem, partida_JogodaBola, partida_JogoReac
from auth.users import current_active_user, User
from database import get_async_session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/jogodamem")
async def get_jogo_mem(
    paciente_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(partida_JogodaMem)
        .where(partida_JogodaMem.paciente_id == paciente_id)
        .order_by(partida_JogodaMem.played_at)
    )
    partidas = result.scalars().all()
    return [
        {
            "clicks": p.clicks,
            "duration": p.duration,
            "played_at": p.played_at,
        }
        for p in partidas
    ]


@router.get("/jogodabola")
async def get_jogo_bola(
    paciente_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(partida_JogodaBola)
        .where(partida_JogodaBola.paciente_id == paciente_id)
        .order_by(partida_JogodaBola.played_at)
    )
    partidas = result.scalars().all()
    return [
        {
            "acertos": p.acertos,
            "duration": p.duration,
            "played_at": p.played_at,
        }
        for p in partidas
    ]


@router.get("/jogoreac")
async def get_jogo_reac(
    paciente_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(partida_JogoReac)
        .where(partida_JogoReac.paciente_id == paciente_id)
        .order_by(partida_JogoReac.played_at)
    )
    partidas = result.scalars().all()
    return [
        {
            "reacao": p.reacao,
            "played_at": p.played_at,
        }
        for p in partidas
    ]
