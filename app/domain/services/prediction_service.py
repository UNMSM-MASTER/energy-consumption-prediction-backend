from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from app.domain.entities.prediction import PredictionCreate, Prediction

class PredictionService(ABC):
    @abstractmethod
    async def generate_prediction(self, prediction_request: PredictionCreate) -> Prediction:
        """Generate energy consumption prediction for a given date"""
        pass
    
    @abstractmethod
    async def get_cached_prediction(self, target_date: datetime, user_id: int) -> Optional[Prediction]:
        """Get cached prediction from Redis if available"""
        pass
    
    @abstractmethod
    async def cache_prediction(self, prediction: Prediction) -> None:
        """Cache prediction in Redis for future use"""
        pass
    
    @abstractmethod
    async def validate_prediction_request(self, prediction_request: PredictionCreate) -> bool:
        """Validate prediction request parameters"""
        pass 