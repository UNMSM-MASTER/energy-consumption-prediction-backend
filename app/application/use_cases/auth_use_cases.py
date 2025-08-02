from typing import Optional
from app.domain.entities.user import User, UserCreate, Token
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.auth_service import AuthService


class AuthUseCases:
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def register_user(self, user_data: UserCreate) -> User:
        # Verificar si el usuario ya existe
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")

        # Verificar si el email ya existe
        existing_email = await self.user_repository.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")

        # Crear hash de la contraseña
        hashed_password = await self.auth_service.get_password_hash(user_data.password)
        
        # Crear usuario con contraseña hasheada
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password
        )
        
        return await self.user_repository.create(user_create)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        return await self.auth_service.authenticate_user(username, password)

    async def create_access_token(self, user: User, expires_delta: int) -> str:
        data = {"sub": user.username}
        return await self.auth_service.create_access_token(data, expires_delta)

    async def get_current_user(self, username: str) -> Optional[User]:
        return await self.user_repository.get_by_username(username) 