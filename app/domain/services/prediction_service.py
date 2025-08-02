from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from app.domain.entities.prediction import PredictionInput


class PredictionService(ABC):
    @abstractmethod
    async def load_model(self, company: str) -> Any:
        pass

    @abstractmethod
    async def get_forecast_lags(self, company: str, model: Any, target_date: datetime) -> Tuple[list, Dict[str, Any]]:
        pass

    @abstractmethod
    async def prepare_features(self, target_date: datetime, lags: list) -> list:
        pass

    @abstractmethod
    async def make_prediction(self, model: Any, features: list) -> float:
        pass

    @abstractmethod
    async def get_cached_prediction(self, cache_key: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def cache_prediction(self, cache_key: str, prediction_data: Dict[str, Any], expire: int = 3600) -> bool:
        pass 