from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from home.models import Macroarea, Mesoarea, Microarea, Lesson, Question, UserAtividade, Simulados
from database import get_async_session
from auth.users import current_active_user, User
from social.models import UserFriend
from uuid import UUID
from sqlalchemy import union_all, func, literal


stats_router = APIRouter(prefix="/stats")

from sqlalchemy.sql import and_

@stats_router.get("/nivel/all")
async def get_nivel_all(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    enum_type = UserAtividade.__table__.c.type.type

    # 1) Atividades: lessons + simulados
    lessons_q = (
        select(
            Lesson.id.label("id"),
            Lesson.nivel_associado.label("nivel"),
            literal("lesson", type_=enum_type).label("type"),
            Microarea.id_mesoarea.label("mesoarea_id"),
        )
        .join(Microarea, Microarea.id == Lesson.id_microarea)
    )

    simulados_q = (
        select(
            Simulados.id.label("id"),
            Simulados.nivel_associado.label("nivel"),
            literal("simulado", type_=enum_type).label("type"),
            Simulados.id_mesoarea.label("mesoarea_id"),
        )
    )

    atividades = union_all(lessons_q, simulados_q).subquery("atividades")

    # 2) Total de atividades por mesoarea e nível
    total_subq = (
        select(
            atividades.c.mesoarea_id,
            atividades.c.nivel,
            func.count().label("total"),
        )
        .group_by(atividades.c.mesoarea_id, atividades.c.nivel)
        .subquery("total")
    )

    # 3) Concluídas pelo usuário
    done_subq = (
        select(
            atividades.c.mesoarea_id,
            atividades.c.nivel,
            func.count().label("done"),
        )
        .select_from(
            atividades.join(
                UserAtividade,
                and_(
                    UserAtividade.id_atividade == atividades.c.id,
                    UserAtividade.type == atividades.c.type,
                ),
            )
        )
        .where(UserAtividade.id_user == current_user.id, UserAtividade.foiAprovado == True)
        .group_by(atividades.c.mesoarea_id, atividades.c.nivel)
        .subquery("done")
    )

    # 4) Junta totals e done
    joined = (
        select(
            total_subq.c.mesoarea_id,
            total_subq.c.nivel,
            total_subq.c.total,
            func.coalesce(done_subq.c.done, 0).label("done"),
        )
        .outerjoin(
            done_subq,
            and_(
                done_subq.c.mesoarea_id == total_subq.c.mesoarea_id,
                done_subq.c.nivel == total_subq.c.nivel,
            ),
        )
    ).subquery("progress")

    # 5) Busca também os metadados da Mesoarea
    res = await db.execute(
        select(
            joined.c.mesoarea_id,
            joined.c.nivel,
            joined.c.total,
            joined.c.done,
            Mesoarea.friendly_name,
            Mesoarea.id_macroarea,
        )
        .join(Mesoarea, Mesoarea.id == joined.c.mesoarea_id)
        .order_by(joined.c.mesoarea_id, joined.c.nivel)
    )

    rows = res.all()

    # 6) Processa por mesoarea
    niveis = {}
    for mesoarea_id, nivel, total, done, friendly_name, id_macroarea in rows:
        if mesoarea_id not in niveis:
            niveis[mesoarea_id] = {
                "levels": {},
                "friendly_name": friendly_name,
                "id_macroarea": id_macroarea,
            }
        niveis[mesoarea_id]["levels"][nivel] = (total, done)

    response = []
    for mesoarea_id, data in niveis.items():
        current_level = 1.0
        for nivel in sorted(data["levels"].keys()):
            total, done = data["levels"][nivel]
            if done < total:
                current_level = nivel + (done / total)
                break
            else:
                current_level = nivel + 1
        response.append(
            {
                "mesoarea_id": mesoarea_id,
                "mesoarea_friendly_name": data["friendly_name"],
                "nivel": round(current_level, 2),
                "id_macroarea": data["id_macroarea"],
            }
        )

    return response
