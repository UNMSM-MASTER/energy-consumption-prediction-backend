from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PredictionInput(BaseModel):
    company: str
    datetime: str  # Formato: "YYYY-MM-DD HH:MM"

class PredictionResult(BaseModel):
    prediction_id: str
    input_data: PredictionInput
    parsed_features: dict
    prediction_meta: dict
    prediction: float
    created_at: str
    created_by: str
