from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.application.use_cases.auth_use_cases import AuthUseCases
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.user_repository_impl import PostgreSQLUserRepository
from app.infrastructure.services.auth_service_impl import JWTAuthService
from app.domain.entities.user import User

security = HTTPBearer()

def get_auth_use_cases(db=Depends(get_db)) -> AuthUseCases:
    user_repository = PostgreSQLUserRepository(db)
    auth_service = JWTAuthService(user_repository)
    return AuthUseCases(user_repository, auth_service)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
) -> User:
    token = credentials.credentials
    username = await auth_use_cases.auth_service.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await auth_use_cases.user_repository.get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user 