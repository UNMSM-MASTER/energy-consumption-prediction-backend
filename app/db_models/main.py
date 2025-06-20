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
    hour: int
    dayofweek: int
    month: int
    year: int
    is_weekend: int
    is_peak: int
    lag_1: float
    lag_2: float
    lag_3: float

class PredictionResult(BaseModel):
    prediction_id: str
    input_data: PredictionInput
    prediction: float
    created_at: str
    created_by: str
