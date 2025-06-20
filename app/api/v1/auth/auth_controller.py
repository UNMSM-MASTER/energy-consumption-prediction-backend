from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db_models.main import Token, User, UserCreate
from datetime import timedelta

from app.utils.main import authenticate_user, create_access_token, get_user, get_password_hash, get_current_active_user
from app.config.secrets import config
from app.config.firestore import db

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}}
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

    access_token = create_access_token(
        data={"sub": user.username if isinstance(user, bool) == False else ''}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    # Check if username already exists
    existing_user = get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    users_ref = db.collection("users")
    query = users_ref.where("email", "==", user.email).limit(1).get()
    if query:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }

    # Add to Firestore
    doc_ref = db.collection("users").document()
    doc_ref.set(user_data)

    return User(**user_data)

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
