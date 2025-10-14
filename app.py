from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from database import create_db_and_tables
from auth.models import UserCreate, UserRead, UserUpdate
from auth.users import auth_backend, current_active_user, fastapi_users
from fastapi.middleware.cors import CORSMiddleware
from database import User
from home.home import macro_router, meso_router, question_router, lesson_router
from social.social import social_router
from stats.stats import stats_router
from social.duelos import duelos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)



@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em desenvolvimento pode ser "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
