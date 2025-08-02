from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.prediction import PredictionResult, PredictionCreate


class PredictionRepository(ABC):
    @abstractmethod
    async def create(self, prediction: PredictionCreate) -> PredictionResult:
        pass

    @abstractmethod
    async def get_by_id(self, prediction_id: int) -> Optional[PredictionResult]:
        pass

    @abstractmethod
    async def get_by_prediction_id(self, prediction_id: str) -> Optional[PredictionResult]:
        pass

    @abstractmethod
    async def get_by_user(self, username: str, limit: int = 10) -> List[PredictionResult]:
        pass

    @abstractmethod
    async def delete(self, prediction_id: int) -> bool:
        pass

    @abstractmethod
    async def list_predictions(self, skip: int = 0, limit: int = 100) -> List[PredictionResult]:
        pass 