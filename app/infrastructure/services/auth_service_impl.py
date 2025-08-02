from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.config.settings import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTAuthService(AuthService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not await self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_access_token(self, data: dict, expires_delta: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    async def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

    async def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password) 