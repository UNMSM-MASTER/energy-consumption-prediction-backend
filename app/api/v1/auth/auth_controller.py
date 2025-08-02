from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from app.domain.entities.user import Token, User, UserCreate
from app.application.use_cases.auth_use_cases import AuthUseCases
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.user_repository_impl import PostgreSQLUserRepository
from app.infrastructure.services.auth_service_impl import JWTAuthService
from app.config.settings import get_settings
from app.api.v1.auth.jwt_auth import get_current_user

settings = get_settings()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}}
)


def get_auth_use_cases(db=Depends(get_db)) -> AuthUseCases:
    user_repository = PostgreSQLUserRepository(db)
    auth_service = JWTAuthService(user_repository)
    return AuthUseCases(user_repository, auth_service)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    user = await auth_use_cases.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = await auth_use_cases.create_access_token(
        user=user, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
async def register_user(
    user: UserCreate,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    try:
        return await auth_use_cases.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
