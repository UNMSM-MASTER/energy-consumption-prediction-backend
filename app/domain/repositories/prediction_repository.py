from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from app.domain.entities.prediction import Prediction, PredictionCreate

class PredictionRepository(ABC):
    @abstractmethod
    async def create(self, prediction: PredictionCreate) -> Prediction:
        pass
    
    @abstractmethod
    async def get_by_id(self, prediction_id: int) -> Optional[Prediction]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[Prediction]:
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Prediction]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Prediction]:
        pass
    
    @abstractmethod
    async def update(self, prediction: Prediction) -> Prediction:
        pass
    
    @abstractmethod
    async def delete(self, prediction_id: int) -> bool:
        pass 