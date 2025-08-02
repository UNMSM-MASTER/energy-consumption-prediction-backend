from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import User, UserCreate, Token


class AuthService(ABC):
    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create_access_token(self, data: dict, expires_delta: int) -> str:
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[str]:
        pass

    @abstractmethod
    async def get_password_hash(self, password: str) -> str:
        pass

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass 