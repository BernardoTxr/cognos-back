# rotas para inserir partidas
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from partidas.models import (
    partida_JogodaMem,
    partida_JogodaBola,
    partida_JogoReac,
    PartidaJogodaMemCreate,
    PartidaJogodaBolaCreate,
    PartidaJogoReacCreate,
)
from auth.users import current_active_user
from database import User   
from datetime import datetime

router = APIRouter(prefix="/partidas", tags=["partidas"])

@router.post("/jogodamem/", response_model=dict)
async def create_jogodamem_partida(
    partida: PartidaJogodaMemCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    new_partida = partida_JogodaMem(
        paciente_id=user.id,
        clicks=partida.clicks,
        duration=partida.duration
        )
    session.add(new_partida)
    await session.commit()
    await session.refresh(new_partida)
    return {"id": new_partida.id, "message": "Partida de Jogo da Memória criada com sucesso."}

@router.post("/jogodabola/", response_model=dict)
async def create_jogodabola_partida(
    partida: PartidaJogodaBolaCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    new_partida = partida_JogodaBola(
        paciente_id=user.id,
        acertos=partida.acertos,
        duration=partida.duration
        )
    session.add(new_partida)
    await session.commit()
    await session.refresh(new_partida)
    return {"id": new_partida.id, "message": "Partida de Jogo da Bola criada com sucesso."}

@router.post("/jogodoreac/", response_model=dict)
async def create_jogodoreac_partida(
    partida: PartidaJogoReacCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    new_partida = partida_JogoReac(
        paciente_id=user.id,
        reacao=partida.reacao,
        )
    session.add(new_partida)
    await session.commit()
    await session.refresh(new_partida)
    return {"id": new_partida.id, "message": "Partida de Jogo de Reação criada com sucesso."}
