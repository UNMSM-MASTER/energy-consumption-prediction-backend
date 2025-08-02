from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.repositories.user_repository import UserRepository
from app.domain.entities.user import User, UserCreate, UserUpdate
from app.infrastructure.database.models import User as UserModel
import uuid


class PostgreSQLUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, user: UserCreate) -> User:
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.password,  # Ya viene hasheada desde el caso de uso
            disabled=False
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User.from_orm(db_user)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return User.from_orm(db_user) if db_user else None

    async def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        return User.from_orm(db_user) if db_user else None

    async def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return User.from_orm(db_user) if db_user else None

    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return User.from_orm(db_user)

    async def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [User.from_orm(user) for user in db_users] 