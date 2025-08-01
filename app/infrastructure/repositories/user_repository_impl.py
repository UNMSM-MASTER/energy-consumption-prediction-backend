from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.repositories.user_repository import UserRepository
from app.domain.entities.user import User, UserCreate
from app.infrastructure.database.models.user_model import UserModel
from app.config.main import pwd_context

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, user: UserCreate) -> User:
        hashed_password = pwd_context.hash(user.password)
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user is None:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user is None:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_all(self) -> List[User]:
        db_users = self.db.query(UserModel).all()
        return [
            User(
                id=user.id,
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in db_users
        ]
    
    async def update(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            db_user.username = user.username
            db_user.email = user.email
            db_user.hashed_password = user.hashed_password
            db_user.is_active = user.is_active
            self.db.commit()
            self.db.refresh(db_user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False 