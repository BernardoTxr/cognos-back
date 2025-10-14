from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_async_session
from auth.users import current_active_user, User
from social.models import UserFriend
from uuid import UUID

social_router = APIRouter(prefix="/social")


@social_router.post("/friends/request")
async def send_friend_request(
    requested_username: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    # Find the user by username
    result = await db.execute(select(User).where(User.username == requested_username))
    requested_user = result.scalar_one_or_none()

    if not requested_user:
        raise HTTPException(status_code=404, detail="User not found")

    menor_id = min(user.id, requested_user.id)
    maior_id = max(user.id, requested_user.id)

    if user.id == requested_user.id:
        raise HTTPException(
            status_code=400,
            detail="Você nao pode adicionar você mesmo... Tente fazer outros amigos!",
        )

    # verifica se existe um pedido de amizade já existente. se
    # enum = req do user -> "Pedido já enviado!"
    # enum = req do requested_user -> "Você já recebeu um invite deste usuário. Aceite ele!"
    # enum = friends -> "Você e {username} são amigos!"
    existing_request = await db.execute(
        select(UserFriend).where(
            UserFriend.uid1 == menor_id, UserFriend.uid2 == maior_id
        )
    )
    friend_request = existing_request.scalar_one_or_none()

    if friend_request:
        if (
            (friend_request.status == "req_uid1") and friend_request.uid1 == user.id
        ) or (
            (friend_request.status == "req_uid2") and (friend_request.uid2 == user.id)
        ):
            return {"message": "Pedido já enviado!"}
        elif (
            (friend_request.status == "req_uid2") and friend_request.uid1 == user.id
        ) or (
            (friend_request.status == "req_uid1") and (friend_request.uid2 == user.id)
        ):
            return {"message": "Você já recebeu um invite deste usuário. Aceite ele!"}
        elif friend_request.status == "friends":
            return {"message": f"Você e {requested_username} já são amigos!"}
    else:
        friend_request = UserFriend(
            uid1=menor_id,
            uid2=maior_id,
            status="req_uid1" if user.id == menor_id else "req_uid2",
        )

    db.add(friend_request)
    await db.commit()
    return {"message": "Friend request sent"}


# rota para listar os friend requests
@social_router.get("/friends/requests")
async def list_friend_requests(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    friend_requests = await db.execute(
        select(UserFriend).where(
            ((UserFriend.uid1 == user.id) & (UserFriend.status == "req_uid2"))
            | ((UserFriend.uid2 == user.id) & (UserFriend.status == "req_uid1"))
        )
    )
    friend_requests = friend_requests.scalars().all()
    return {"friend_requests": friend_requests}


# rota para listar os friend requests com detalhes do usuário
@social_router.get("/friends/requests/details")
async def list_friend_requests_details(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    friend_requests: List[UserFriend] = Depends(list_friend_requests),
):
    requester_ids = [
        fr.uid2 if fr.uid1 == user.id else fr.uid1
        for fr in friend_requests["friend_requests"]
    ]
    if not requester_ids:
        return {"friend_requests_details": []}

    result = await db.execute(select(User).where(User.id.in_(requester_ids)))
    # retorna apenas id, username, email
    requesters_details = result.scalars().all()
    requesters_details = [
        {"id": requester.id, "username": requester.username, "email": requester.email}
        for requester in requesters_details
    ]
    return {"friend_requests_details": requesters_details}


# rota para aceitar um friend request
@social_router.post("/friends/accept/{friend_id}")
async def accept_friend_request(
    friend_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    # procurar a relação
    result = await db.execute(
        select(UserFriend).where(
            (UserFriend.uid1 == min(user.id, friend_id))
            & (UserFriend.uid2 == max(user.id, friend_id))
        )
    )
    friend_request = result.scalar_one_or_none()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # só pode aceitar se ele for o destinatário do pedido
    if (friend_request.status == "req_uid1" and friend_request.uid2 == user.id) or (
        friend_request.status == "req_uid2" and friend_request.uid1 == user.id
    ):
        friend_request.status = "friends"
        await db.commit()
        return {"message": "Amizade confirmada!"}
    else:
        raise HTTPException(status_code=403, detail="Você não pode aceitar este pedido")


@social_router.delete("/friends/request/{friend_id}")
async def delete_friend_request(
    friend_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    # sempre ordena ids para bater com o padrão da tabela
    menor_id = min(user.id, friend_id)
    maior_id = max(user.id, friend_id)

    result = await db.execute(
        select(UserFriend).where(
            (UserFriend.uid1 == menor_id) & (UserFriend.uid2 == maior_id)
        )
    )
    friend_request = result.scalar_one_or_none()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if friend_request.status == "friends":
        raise HTTPException(status_code=400, detail="Vocês já são amigos")

    # só pode rejeitar se ele for o destinatário do pedido
    if (friend_request.status == "req_uid1" and friend_request.uid2 == user.id) or (
        friend_request.status == "req_uid2" and friend_request.uid1 == user.id
    ):
        raise HTTPException(status_code=403, detail="Você não pode remover este pedido")

    # remove da tabela
    await db.delete(friend_request)
    await db.commit()

    return {"message": "Pedido de amizade removido com sucesso"}


@social_router.get("/friends")
async def list_friends(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(UserFriend).where(
            ((UserFriend.uid1 == user.id) | (UserFriend.uid2 == user.id))
            & (UserFriend.status == "friends")
        )
    )
    friends = result.scalars().all()
    return {"friends": friends}


@social_router.get("/friends/details")
async def list_friends_details(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    friends: List[UserFriend] = Depends(list_friends),
):
    friend_ids = [
        friend.uid2 if friend.uid1 == user.id else friend.uid1
        for friend in friends["friends"]
    ]
    if not friend_ids:
        return {"friends_details": []}

    result = await db.execute(select(User).where(User.id.in_(friend_ids)))
    # retorna apenas id, username, email
    friends_details = result.scalars().all()
    friends_details = [
        {"id": friend.id, "username": friend.username, "email": friend.email}
        for friend in friends_details
    ]
    return {"friends_details": friends_details}


@social_router.delete("/friends/{friend_id}")
async def remove_friend(
    friend_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    menor_id = min(user.id, friend_id)
    maior_id = max(user.id, friend_id)

    result = await db.execute(
        select(UserFriend).where(
            (UserFriend.uid1 == menor_id) & (UserFriend.uid2 == maior_id)
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise HTTPException(status_code=404, detail="Amizade não encontrada")

    if friendship.status != "friends":
        raise HTTPException(status_code=400, detail="Vocês não são amigos")

    await db.delete(friendship)
    await db.commit()

    return {"message": "Amizade removida com sucesso"}
