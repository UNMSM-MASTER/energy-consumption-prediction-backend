from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Prediction(BaseModel):
    id: Optional[int] = None
    user_id: int
    prediction_date: datetime
    target_date: datetime
    consumption_prediction: float
    confidence_interval: Optional[Dict[str, float]] = None
    model_version: str
    features_used: List[str]
    company: str
    created_at: Optional[datetime] = None

class PredictionCreate(BaseModel):
    user_id: int
    target_date: datetime
    company: str
    model_version: str = "v1.0"
    features_used: List[str] = []

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    prediction_date: datetime
    target_date: datetime
    consumption_prediction: float
    confidence_interval: Optional[Dict[str, float]] = None
    model_version: str
    features_used: List[str]
    company: str
    created_at: datetime 