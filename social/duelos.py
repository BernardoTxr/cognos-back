from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from home.models import Macroarea, Mesoarea, Microarea, Lesson, Question, Simulados, UserAtividade
from database import get_async_session
from auth.users import current_active_user, User
from social.models import (
    UserFriend,
    Duelo,
    DueloQuestion,
)
from uuid import UUID
from sqlalchemy import func

duelos_router = APIRouter(prefix="/duelo")


@duelos_router.post("/create")
async def create_duelo(
    uid2: UUID,
    id_mesoarea: int,
    rounds: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    # por enquanto, todo duelo tem round=1
    rounds = 1
    if rounds != 1:
        raise HTTPException(
            status_code=400, detail="Currently only 1 round is supported"
        )
    if user.id == uid2:
        raise HTTPException(status_code=400, detail="You cannot challenge yourself")
    # verifica se uid2 existe
    result = await db.execute(select(User).where(User.id == uid2))
    challenged_user = result.scalar_one_or_none()
    if not challenged_user:
        raise HTTPException(status_code=404, detail="Challenged user not found")
    # verifica se id_mesoarea existe
    result = await db.execute(select(Mesoarea).where(Mesoarea.id == id_mesoarea))
    mesoarea = result.scalar_one_or_none()
    if not mesoarea:
        raise HTTPException(status_code=404, detail="Mesoarea not found")
    # cria duelo
    new_duelo = Duelo(
        uid1=user.id,
        uid2=uid2,
        id_mesoarea=id_mesoarea,
        rounds=rounds,
        status="waiting_u2",
        resultado="waiting_results",
    )
    db.add(new_duelo)
    await db.commit()  # commit para garantir que o ID é gerado
    # associa questões aleatórias da mesoarea em questão ao duelo em duelo_question
    # primeiro, obtém o id do duelo recém criado
    await db.refresh(new_duelo)  # para garantir que new_duelo.id está atualizado
    duelo_id = new_duelo.id
    # obtém todas as microareas da mesoarea em questao
    result = await db.execute(
        select(Microarea.id).where(Microarea.id_mesoarea == id_mesoarea)
    )
    microarea_ids = [row[0] for row in result.fetchall()]
    if not microarea_ids:
        raise HTTPException(
            status_code=404, detail="No microareas found for this mesoarea"
        )
    # obtém 5 questões aleatórias dessas microareas
    result = await db.execute(
        select(Question.id)
        .where(Question.id_microarea.in_(microarea_ids))
        .order_by(func.random())
        .limit(5)
    )
    # adiciona essas 5 questões na tabela duelo_question
    question_ids = [row[0] for row in result.fetchall()]
    if len(question_ids) < 5:
        raise HTTPException(
            status_code=404, detail="Not enough questions in this mesoarea"
        )
    for qid in question_ids:
        duelo_question = DueloQuestion(
            id_question=qid,
            id_duelo=duelo_id,
            foiAcerto_u1=False,
            foiAcerto_u2=False,
        )
        db.add(duelo_question)
    await db.commit()
    return {"message": "Duelo created", "duelo_id": duelo_id}


@duelos_router.get("/my_duelos", response_model=List[dict])
async def get_my_duelos(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(Duelo).where((Duelo.uid1 == user.id) | (Duelo.uid2 == user.id))
    )
    duelos = result.scalars().all()
    duelos_list = []
    for duelo in duelos:
        # encontre o username associado a uid1 e uid2
        result = await db.execute(select(User).where(User.id == duelo.uid1))
        user1 = result.scalar_one_or_none()
        result = await db.execute(select(User).where(User.id == duelo.uid2))
        user2 = result.scalar_one_or_none()
        # encontre o friendly name da mesoarea
        result = await db.execute(
            select(Mesoarea).where(Mesoarea.id == duelo.id_mesoarea)
        )
        mesoarea = result.scalar_one_or_none()
        duelos_list.append(
            {
                "id": duelo.id,
                "uid1": duelo.uid1,
                "uid2": duelo.uid2,
                "user1_username": user1.username,
                "user2_username": user2.username,
                "mesoarea_friendly_name": mesoarea.friendly_name,
                "id_mesoarea": duelo.id_mesoarea,
                "rounds": duelo.rounds,
                "status": duelo.status,
                "resultado": duelo.resultado,
            }
        )
    return duelos_list
