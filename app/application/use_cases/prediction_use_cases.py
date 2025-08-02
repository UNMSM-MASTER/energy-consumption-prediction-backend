from typing import List, Optional
from datetime import datetime
import uuid
from app.domain.entities.prediction import PredictionInput, PredictionResult, PredictionCreate
from app.domain.repositories.prediction_repository import PredictionRepository
from app.domain.repositories.cache_repository import CacheRepository
from app.domain.services.prediction_service import PredictionService


class PredictionUseCases:
    def __init__(
        self, 
        prediction_repository: PredictionRepository,
        cache_repository: CacheRepository,
        prediction_service: PredictionService
    ):
        self.prediction_repository = prediction_repository
        self.cache_repository = cache_repository
        self.prediction_service = prediction_service

    async def make_prediction(self, input_data: PredictionInput, username: str) -> PredictionResult:
        # Generar clave de cache única para esta predicción
        cache_key = f"prediction:{input_data.company}:{input_data.datetime}:{username}"
        
        # Verificar si existe en cache
        cached_prediction = await self.prediction_service.get_cached_prediction(cache_key)
        if cached_prediction:
            return PredictionResult(**cached_prediction)

        try:
            # Cargar modelo
            model = await self.prediction_service.load_model(input_data.company.upper())

            # Parsear fecha
            dt = datetime.fromisoformat(input_data.datetime.replace(' ', 'T'))

            # Obtener lags predictivos
            lags, meta = await self.prediction_service.get_forecast_lags(
                input_data.company.upper(),
                model,
                dt
            )

            # Preparar features finales
            features = await self.prediction_service.prepare_features(dt, lags)

            # Hacer predicción final
            prediction = await self.prediction_service.make_prediction(model, features)

            # Preparar datos de respuesta
            prediction_data = {
                "input_data": input_data,
                "parsed_features": {
                    "hour": dt.hour,
                    "dayofweek": dt.weekday(),
                    "month": dt.month,
                    "year": dt.year,
                    "is_weekend": 1 if dt.weekday() >= 5 else 0,
                    "is_peak": 1 if dt.hour in [7, 8, 18, 19] else 0,
                    "lag_1": lags[0],
                    "lag_2": lags[1],
                    "lag_3": lags[2],
                },
                "prediction_meta": {
                    "steps": meta['steps'],
                    "last_real_lag_1": meta['last_real']['lag_1'],
                    "last_real_lag_2": meta['last_real']['lag_2'],
                    "last_real_lag_3": meta['last_real']['lag_3'],
                    "forecast_method": "recursive"
                },
                "prediction": float(prediction),
                "created_by": username
            }

            # Crear predicción en base de datos
            prediction_create = PredictionCreate(**prediction_data)
            result = await self.prediction_repository.create(prediction_create)

            # Guardar en cache para futuras consultas
            await self.prediction_service.cache_prediction(cache_key, result.dict(), expire=3600)

            return result

        except Exception as e:
            raise ValueError(f"Error al predecir: {str(e)}")

    async def get_user_predictions(self, username: str, limit: int = 10) -> List[PredictionResult]:
        return await self.prediction_repository.get_by_user(username, limit)

    async def get_prediction_by_id(self, prediction_id: str, username: str) -> Optional[PredictionResult]:
        prediction = await self.prediction_repository.get_by_prediction_id(prediction_id)
        
        if not prediction:
            return None
            
        # Verificar que la predicción pertenece al usuario
        if prediction.created_by != username:
            raise ValueError("Not authorized to access this prediction")
            
        return prediction

    async def preload_model_if_needed(self, company: str) -> None:
        """
        Precarga el modelo en background si no está cargado
        """
        try:
            await self.prediction_service.load_model(company.upper())
        except Exception:
            # Silenciar errores en background task
            pass 