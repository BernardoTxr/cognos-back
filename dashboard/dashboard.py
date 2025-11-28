from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from partidas.models import partida_JogodaMem, partida_JogoDoCognosMath, partida_JogodaBola, partida_JogoReac, partida_JogoDoWisconsin
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

@router.get("/jogodocognosmath")
async def get_jogo_cognos_math(
    paciente_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(partida_JogoDoCognosMath)
        .where(partida_JogoDoCognosMath.paciente_id == paciente_id)
        .order_by(partida_JogoDoCognosMath.played_at)
    )
    partidas = result.scalars().all()
    return [
        {
            "acertos": p.acertos,
            "tempo_medio_jogada": p.tempo_medio_jogada,
            "variancia_jogada": p.variancia_jogada,
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

@router.get("/jogodowisconsin")
async def get_jogo_wisconsin(
    paciente_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(partida_JogoDoWisconsin)
        .where(partida_JogoDoWisconsin.paciente_id == paciente_id)
        .order_by(partida_JogoDoWisconsin.played_at)
    )
    partidas = result.scalars().all()

    return [
        {
            "acertos": p.acertos,
            "erros_perseverativos": p.erros_perseverativos,
            "erros_nonperseverativos": p.erros_nonperseverativos,
            "falha_manter_conjunto": p.falha_manter_conjunto,
            "categorias_completas": p.categorias_completas,
            "played_at": p.played_at,
        }
        for p in partidas
    ]
