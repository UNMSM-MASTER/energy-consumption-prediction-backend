from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class PredictionInput(BaseModel):
    company: str
    datetime: str  # Formato: "YYYY-MM-DD HH:MM"


class PredictionResult(BaseModel):
    id: Optional[int] = None
    prediction_id: Optional[str] = None
    input_data: PredictionInput
    parsed_features: Dict[str, Any]
    prediction_meta: Dict[str, Any]
    prediction: float
    created_at: Optional[datetime] = None
    created_by: str

    class Config:
        from_attributes = True


class PredictionCreate(BaseModel):
    input_data: PredictionInput
    parsed_features: Dict[str, Any]
    prediction_meta: Dict[str, Any]
    prediction: float
    created_by: str 