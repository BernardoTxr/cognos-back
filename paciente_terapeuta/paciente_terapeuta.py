from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, join
from uuid import UUID
from sqlalchemy.orm import aliased
from database import get_async_session
from auth.users import current_active_user, User
from dados.models import PacienteTerapeuta, Terapeuta, Paciente

social_router = APIRouter(prefix="/paciente_terapeuta", tags=["paciente-terapeuta"])


# 1️⃣ Listar todos os terapeutas conectados ao paciente logado
@social_router.get("/me/terapeutas")
async def listar_terapeutas_para_paciente(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    # 🔒 Só pacientes podem acessar
    if not current_user.is_patient:
        raise HTTPException(status_code=403, detail="Apenas pacientes podem acessar isso.")

    # 🔍 Join entre PacienteTerapeuta, Terapeuta e User
    query = (
        select(
            Terapeuta.user_id,
            Terapeuta.nome_completo,
            Terapeuta.documento,
            User.email,
            User.username,
        )
        .join(PacienteTerapeuta, Terapeuta.user_id == PacienteTerapeuta.terapeuta_id)
        .join(User, User.id == Terapeuta.user_id)
        .where(
            and_(
                PacienteTerapeuta.paciente_id == current_user.id,
                PacienteTerapeuta.status == "conectados",
            )
        )
    )

    result = await db.execute(query)
    terapeutas = result.mappings().all()  # Retorna como dicionários

    return terapeutas


# 2️⃣ Listar todos os pacientes conectados ao terapeuta logado
@social_router.get("/me/pacientes")
async def listar_pacientes_para_terapeuta(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    # 🔒 Só terapeutas podem acessar
    if current_user.is_patient:
        raise HTTPException(status_code=403, detail="Apenas terapeutas podem acessar isso.")

    # 🔍 Join entre PacienteTerapeuta, Paciente e User
    query = (
        select(
            Paciente.user_id,
            Paciente.nome_completo,
            Paciente.data_de_nascimento,
            Paciente.cpf,
            Paciente.sexo,
            Paciente.nivel_tea,
            User.email,
            User.username,
        )
        .join(PacienteTerapeuta, Paciente.user_id == PacienteTerapeuta.paciente_id)
        .join(User, User.id == Paciente.user_id)
        .where(
            (PacienteTerapeuta.terapeuta_id == current_user.id)
            & (PacienteTerapeuta.status == "conectados")
        )
    )

    result = await db.execute(query)
    pacientes = result.mappings().all()  # retorna como lista de dicionários

    return pacientes


# 3️⃣ Criar solicitação de conexão
@social_router.post("/conectar/{alvo_id}")
async def solicitar_conexao(
    alvo_id: UUID,  # o id do terapeuta (se paciente estiver logado) ou do paciente (se terapeuta estiver logado)
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    if current_user.is_patient not in [True, False]:
        raise HTTPException(status_code=403, detail="Usuário inválido.")

    # Verifica se já existe relação
    query_existente = select(PacienteTerapeuta).where(
        or_(
            and_(
                PacienteTerapeuta.paciente_id == current_user.id,
                PacienteTerapeuta.terapeuta_id == alvo_id,
            ),
            and_(
                PacienteTerapeuta.paciente_id == alvo_id,
                PacienteTerapeuta.terapeuta_id == current_user.id,
            ),
        )
    )
    existente = (await db.execute(query_existente)).scalars().first()
    if existente:
        raise HTTPException(status_code=400, detail="Conexão já existe.")

    # Define status conforme quem está enviando
    status_conec = "req_paciente" if current_user.is_patient else "req_terapeuta"

    nova_conexao = PacienteTerapeuta(
        paciente_id=current_user.id if current_user.is_patient else alvo_id,
        terapeuta_id=alvo_id if current_user.is_patient else current_user.id,
        status=status_conec,
    )
    db.add(nova_conexao)
    await db.commit()
    await db.refresh(nova_conexao)

    return {"message": "Solicitação enviada com sucesso.", "conexao": nova_conexao}


# 4️⃣ Solicitações para terapeuta (status = req_paciente)
@social_router.get("/solicitacoes/terapeuta")
async def listar_solicitacoes_para_terapeuta(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    if current_user.is_patient:
        raise HTTPException(status_code=403, detail="Apenas terapeutas podem acessar isso.")

    # Aliases para clareza
    paciente_alias = aliased(Paciente)
    user_alias = aliased(User)

    # Construção dos joins explícitos:
    # PacienteTerapeuta → Paciente → User
    j = (
        join(PacienteTerapeuta, paciente_alias, PacienteTerapeuta.paciente_id == paciente_alias.user_id)
        .join(user_alias, paciente_alias.user_id == user_alias.id)
    )

    # Query com filtros
    query = (
        select(
            PacienteTerapeuta.id.label("conexao_id"),
            PacienteTerapeuta.status,
            paciente_alias.user_id.label("paciente_id"),
            paciente_alias.nivel_tea,
            paciente_alias.sexo,
            paciente_alias.data_de_nascimento,
            user_alias.username.label("nome_usuario"),
            user_alias.email,
            user_alias.created_at.label("criado_em"),
        )
        .select_from(j)
        .where(
            and_(
                PacienteTerapeuta.terapeuta_id == current_user.id,
                PacienteTerapeuta.status == "req_paciente",
            )
        )
    )

    result = await db.execute(query)
    rows = result.mappings().all()

    return rows


# 5️⃣ Solicitações para paciente (status = req_terapeuta)
from sqlalchemy import select, and_, join
from sqlalchemy.orm import aliased

@social_router.get("/solicitacoes/paciente")
async def listar_solicitacoes_para_paciente(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    # 🔒 Apenas pacientes podem acessar
    if not current_user.is_patient:
        raise HTTPException(status_code=403, detail="Apenas pacientes podem acessar isso.")

    # Aliases para clareza
    terapeuta_alias = aliased(Terapeuta)
    user_alias = aliased(User)

    # 🔗 Joins explícitos: PacienteTerapeuta → Terapeuta → User
    j = (
        join(PacienteTerapeuta, terapeuta_alias, PacienteTerapeuta.terapeuta_id == terapeuta_alias.user_id)
        .join(user_alias, terapeuta_alias.user_id == user_alias.id)
    )

    # 🔍 Query com os filtros e campos relevantes
    query = (
        select(
            PacienteTerapeuta.id.label("conexao_id"),
            PacienteTerapeuta.status,
            terapeuta_alias.user_id.label("terapeuta_id"),
            user_alias.username.label("nome_usuario"),
            user_alias.email,
            user_alias.created_at.label("criado_em"),
        )
        .select_from(j)
        .where(
            and_(
                PacienteTerapeuta.paciente_id == current_user.id,
                PacienteTerapeuta.status == "req_terapeuta",
            )
        )
    )

    result = await db.execute(query)
    rows = result.mappings().all()

    return rows


# 6️⃣ Aceitar conexão (muda status → conectados)
@social_router.put("/aceitar/{conexao_id}")
async def aceitar_conexao(
    conexao_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    query = select(PacienteTerapeuta).where(PacienteTerapeuta.id == conexao_id)
    result = await db.execute(query)
    conexao = result.scalars().first()

    if not conexao:
        raise HTTPException(status_code=404, detail="Conexão não encontrada.")

    # Verifica se o usuário pode aceitar
    if (
        (current_user.is_patient and conexao.status != "req_terapeuta")
        or (not current_user.is_patient and conexao.status != "req_paciente")
    ):
        raise HTTPException(status_code=403, detail="Você não pode aceitar esta conexão.")

    conexao.status = "conectados"
    await db.commit()
    await db.refresh(conexao)

    return {"message": "Conexão aceita com sucesso.", "conexao": conexao}

# 7️⃣ Rejeitar conexão (agora deleta a linha da tabela)
@social_router.delete("/rejeitar/{conexao_id}")
async def rejeitar_conexao(
    conexao_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    query = select(PacienteTerapeuta).where(PacienteTerapeuta.id == conexao_id)
    result = await db.execute(query)
    conexao = result.scalars().first()

    if not conexao:
        raise HTTPException(status_code=404, detail="Conexão não encontrada.")

    # Verifica se o usuário tem permissão para rejeitar
    if (
        (current_user.is_patient and conexao.status != "req_terapeuta")
        or (not current_user.is_patient and conexao.status != "req_paciente")
    ):
        raise HTTPException(status_code=403, detail="Você não pode rejeitar esta conexão.")

    # ❌ Remove o registro da tabela
    await db.delete(conexao)
    await db.commit()

    return {"message": "Conexão rejeitada e removida com sucesso."}
