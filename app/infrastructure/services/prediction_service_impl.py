from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import pandas as pd
from app.domain.services.prediction_service import PredictionService
from app.domain.repositories.cache_repository import CacheRepository
from app.ml_models.ml_model import MlModel

class MLPredictionService(PredictionService):
    def __init__(self, cache_repository: CacheRepository):
        self.cache_repository = cache_repository
        self.models_cache = {}
        self.ml_model_loader = MlModel()

    async def load_model(self, company: str) -> Any:
        # Verificar si el modelo ya está en cache
        if company in self.models_cache:
            return self.models_cache[company]

        # Cargar modelo desde Firebase Storage usando MlModel
        try:
            model = self.ml_model_loader.load_model(company)
            
            # Guardar en cache
            self.models_cache[company] = model
            return model
        except Exception as e:
            raise ValueError(f"Error loading model for company {company}: {str(e)}")

    async def get_forecast_lags(self, company: str, model: Any, target_date: datetime) -> Tuple[list, Dict[str, Any]]:
        # Verificar cache para lags
        cache_key = f"lags:{company}:{target_date.strftime('%Y-%m-%d-%H')}"
        cached_lags = await self.cache_repository.get(cache_key)
        
        if cached_lags:
            return cached_lags['lags'], cached_lags['meta']

        # Usar LagService para calcular lags reales con cache optimizado
        from app.api.v1.prediction.services.lang import LagService
        lag_service = LagService()
        
        # Convertir datetime a pandas Timestamp para compatibilidad
        target_dt = pd.Timestamp(target_date)
        
        try:
            lags, meta = await lag_service.get_forecast_lags(company, model, target_dt)
            
            # Guardar en cache
            await self.cache_repository.set(cache_key, {
                'lags': lags,
                'meta': meta
            }, expire=3600)

            return lags, meta
        except Exception as e:
            raise ValueError(f"Error calculating lags for {company}: {str(e)}")

    async def prepare_features(self, target_date: datetime, lags: list) -> list:
        features = [
            target_date.hour,
            target_date.weekday(),
            target_date.month,
            target_date.year,
            1 if target_date.weekday() >= 5 else 0,  # is_weekend
            1 if target_date.hour in [7, 8, 18, 19] else 0,  # is_peak
            lags[0],  # lag_1
            lags[1],  # lag_2
            lags[2],  # lag_3
        ]
        return features

    async def make_prediction(self, model: Any, features: list) -> float:
        # Definir nombres de features para evitar warning de sklearn
        feature_names = ['hour', 'dayofweek', 'month', 'year', 'is_weekend', 'is_peak', 'lag_1', 'lag_2', 'lag_3']
        
        # Convertir a DataFrame con nombres de columnas para evitar warning
        features_df = pd.DataFrame([features], columns=feature_names)
        prediction = model.predict(features_df)[0]
        return float(prediction)

    async def get_cached_prediction(self, cache_key: str) -> Optional[Dict[str, Any]]:
        return await self.cache_repository.get(cache_key)

    async def cache_prediction(self, cache_key: str, prediction_data: Dict[str, Any], expire: int = 3600) -> bool:
        return await self.cache_repository.set(cache_key, prediction_data, expire) 