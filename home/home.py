from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import case, exists
from home.models import Macroarea, Mesoarea, Microarea, Lesson, Question, UserAtividade, UserQuestion, UserQuestionRequest, UserAtividadeRequest, QuestionResquest, Simulados
from database import get_async_session
from auth.users import current_active_user, User
from datetime import datetime

# ---------- MACROAREA ----------
macro_router = APIRouter(prefix="/macroareas")


@macro_router.get("/")
async def get_all_macros(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Macroarea))
    return result.scalars().all()


@macro_router.get("/by-name/{name}")
async def get_macro_by_name(name: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Macroarea).filter(Macroarea.nome.ilike(f"%{name}%"))
    )
    macros = result.scalars().all()
    if not macros:
        raise HTTPException(status_code=404, detail="Macroarea não encontrada")
    return macros


# ---------- MESOAREA ----------
meso_router = APIRouter(prefix="/mesoareas")


@meso_router.get("/")
async def get_all_mesos(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Mesoarea))
    return result.scalars().all()


@meso_router.get("/by-name/{name}")
async def get_meso_by_name(name: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Mesoarea).filter(Mesoarea.nome.ilike(f"%{name}%")))
    mesos = result.scalars().all()
    if not mesos:
        raise HTTPException(status_code=404, detail="Mesoarea não encontrada")
    return mesos


@meso_router.get("/by-macroarea/{macro_name}")
async def get_mesos_by_macroarea(
    macro_name: str, db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Macroarea).filter(Macroarea.nome.ilike(f"%{macro_name}%"))
    )
    macroareas = result.scalars().all()
    if not macroareas:
        raise HTTPException(status_code=404, detail="Macroarea não encontrada")
    macro_ids = [m.id for m in macroareas]
    result = await db.execute(
        select(Mesoarea).filter(Mesoarea.id_macroarea.in_(macro_ids))
    )
    mesoareas = result.scalars().all()
    if not mesoareas:
        raise HTTPException(
            status_code=404, detail="Nenhuma Mesoarea encontrada para essa Macroarea"
        )
    return mesoareas


# ---------- MICROAREA ----------
micro_router = APIRouter(prefix="/microareas")


@micro_router.get("/")
async def get_all_micros(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Microarea))
    return result.scalars().all()


@micro_router.get("/by-name/{name}")
async def get_micro_by_name(name: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Microarea).filter(Microarea.nome.ilike(f"%{name}%"))
    )
    micros = result.scalars().all()
    if not micros:
        raise HTTPException(status_code=404, detail="Microarea não encontrada")
    return micros


@micro_router.get("/by-mesoarea/{meso_name}")
async def get_microareas_by_mesoarea(
    meso_name: str, db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Mesoarea).filter(Mesoarea.nome.ilike(f"%{meso_name}%"))
    )
    mesoareas = result.scalars().all()
    if not mesoareas:
        raise HTTPException(status_code=404, detail="Mesoarea não encontrada")
    meso_ids = [m.id for m in mesoareas]
    result = await db.execute(
        select(Microarea).filter(Microarea.id_mesoarea.in_(meso_ids))
    )
    microareas = result.scalars().all()
    if not microareas:
        raise HTTPException(
            status_code=404, detail="Nenhuma Microarea encontrada para essa Mesoarea"
        )
    return microareas


# ---------- QUESTION ----------
question_router = APIRouter(prefix="/questions")


@question_router.get("/")
async def get_all_questions(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Question))
    return result.scalars().all()


@question_router.get("/by-microarea/{microarea_id}")
async def get_questions_by_microarea_id(
    microarea_id: int, db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Question).filter(Question.id_microarea == microarea_id)
    )
    return result.scalars().all()

@question_router.post("/by-microarea-and-quantity/")
async def get_questions_by_microarea_id(
    question_request_data: QuestionResquest,
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Question)
        .filter(Question.id_microarea == question_request_data.microarea_id, Question.difficulty == question_request_data.nivel_associado)
        .order_by(func.random())
        .limit(question_request_data.quantity)
    )
    return result.scalars().all()

@question_router.get("/done-by-microarea/{microarea_id}")
async def get_done_question_by_microarea_id(
    microarea_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(UserQuestion).join(Question, UserQuestion.id_question == Question.id).filter(Question.id_microarea == microarea_id, UserQuestion.id_user == user.id)
    )
    return result.scalars().all()

@question_router.post("/done-question/")
async def post_done_question(
    userQuestionData: List[UserQuestionRequest],
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    created = []

    for item in userQuestionData:
        user_question = UserQuestion(
            id_user=user.id,
            id_question=item.id_question,
            foiAcerto=item.foiAcerto,
            attempted_at=datetime.now(),
        )
        db.add(user_question)
        created.append(user_question)

    await db.commit()
    for q in created:
        await db.refresh(q)

    return {
        "message": f"{len(created)} questões adicionadas",
        "questions": [{"id": q.id, "id_question": q.id_question} for q in created],
    }


# ---------- LESSON ----------
lesson_router = APIRouter(prefix="/lessons")


@lesson_router.get("/")
async def get_all_lessons(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Lesson))
    return result.scalars().all()


from sqlalchemy import select, case, exists, func, union_all, literal, literal_column
from sqlalchemy.orm import aliased

@lesson_router.get("/by-mesoarea/{mesoarea_id}")
async def get_trilha_com_simulados(
    mesoarea_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    # Subquery para determinar qual é a próxima atividade (lesson ou simulado)
    atividades_union = union_all(
        # Lessons
        select(
            Lesson.id.label("id"),
            Lesson.nivel_associado.label("nivel"),
            Lesson.ordem_no_nivel.label("ordem"),
            literal("lesson", type_=UserAtividade.__table__.c.type.type).label("type"),
        ).join(Microarea, Microarea.id == Lesson.id_microarea)
        .where(Microarea.id_mesoarea == mesoarea_id),
        # Simulados
        select(
            Simulados.id.label("id"),
            Simulados.nivel_associado.label("nivel"),
            literal(9999).label("ordem"),
            literal("simulado", type_=UserAtividade.__table__.c.type.type).label("type"),
        ).where(Simulados.id_mesoarea == mesoarea_id),
    ).subquery("atividades")

    current_atividade = (
        select(atividades_union.c.id)
        .where(
            ~exists(
                select(1).where(
                    UserAtividade.id_atividade == atividades_union.c.id,
                    UserAtividade.id_user == user.id,
                    UserAtividade.foiAprovado == True,
                    UserAtividade.type == atividades_union.c.type,
                )
            )
        )
        .order_by(atividades_union.c.nivel.asc(), atividades_union.c.ordem.asc())
        .limit(1)
        .scalar_subquery()
    )

    # Lessons
    lessons_stmt = (
        select(
            Lesson.id.label("id"),
            Lesson.id_microarea.label("id_microarea"),
            Microarea.friendly_name.label("nome_microarea"),
            Lesson.nivel_associado.label("nivel_associado"),
            Lesson.ordem_no_nivel.label("ordem_no_nivel"),
            literal("lesson").label("type"),
            case(
                (
                    exists(
                        select(1).where(
                            UserAtividade.id_atividade == Lesson.id,
                            UserAtividade.id_user == user.id,
                            UserAtividade.foiAprovado == True,
                            UserAtividade.type == "lesson",
                        )
                    ),
                    True,
                ),
                else_=False,
            ).label("foiFeito"),
            case((Lesson.id == current_atividade, True), else_=False).label("currentLesson"),
        )
        .join(Microarea, Microarea.id == Lesson.id_microarea)
        .where(Microarea.id_mesoarea == mesoarea_id)
    )

    # Simulados
    simulados_stmt = (
        select(
            Simulados.id.label("id"),
            literal(None).label("id_microarea"),
            literal(None).label("nome_microarea"),
            Simulados.nivel_associado.label("nivel_associado"),
            literal(9999).label("ordem_no_nivel"),
            literal("simulado").label("type"),
            case(
                (
                    exists(
                        select(1).where(
                            UserAtividade.id_atividade == Simulados.id,
                            UserAtividade.id_user == user.id,
                            UserAtividade.foiAprovado == True,
                            UserAtividade.type == "simulado",
                        )
                    ),
                    True,
                ),
                else_=False,
            ).label("foiFeito"),
            case((Simulados.id == current_atividade, True), else_=False).label("currentLesson"),
        )
        .where(Simulados.id_mesoarea == mesoarea_id)
    )

    # Unir Lessons + Simulados
    stmt = union_all(lessons_stmt, simulados_stmt).subquery("atividade")

    # Seleção final
    final_stmt = select(stmt).order_by(
        stmt.c.nivel_associado.asc(),
        stmt.c.ordem_no_nivel.asc()
    )

    result = await db.execute(final_stmt)
    return result.mappings().all()


@lesson_router.post("/done-lesson/")
async def post_done_lesson(
    UserAtividadeData: UserAtividadeRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    user_atividade = UserAtividade(
        id_user=user.id,
        id_atividade=UserAtividadeData.id_atividade,
        foiAprovado=UserAtividadeData.foiAprovado,
        type=UserAtividadeData.type,
        done_at=datetime.now(),
    )
    db.add(user_atividade)

    await db.commit()
    await db.refresh(user_atividade)

    return {
        "message": "Lição adicionada",
    }
