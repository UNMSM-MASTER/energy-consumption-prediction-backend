from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Annotated
from datetime import datetime
import asyncio

from app.domain.entities.user import User
from app.domain.entities.prediction import PredictionResult, PredictionInput
from app.application.use_cases.prediction_use_cases import PredictionUseCases
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.prediction_repository_impl import PostgreSQLPredictionRepository
from app.infrastructure.repositories.cache_repository_impl import RedisCacheRepository
from app.infrastructure.services.prediction_service_impl import MLPredictionService
from app.api.v1.auth.jwt_auth import get_current_user

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
    responses={404: {"description": "Not found"}}
)


def get_prediction_use_cases(db=Depends(get_db)) -> PredictionUseCases:
    prediction_repository = PostgreSQLPredictionRepository(db)
    cache_repository = RedisCacheRepository()
    prediction_service = MLPredictionService(cache_repository)
    return PredictionUseCases(prediction_repository, cache_repository, prediction_service)


@router.post("/predict", response_model=PredictionResult)
async def make_prediction(
    input_data: PredictionInput,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    prediction_use_cases: PredictionUseCases = Depends(get_prediction_use_cases)
):
    try:
        # Parsear fecha
        dt = datetime.fromisoformat(input_data.datetime.replace(' ', 'T'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fecha inválida: {str(e)}")

    try:
        # Configurar timeout específico para predicciones (4 minutos)
        result = await asyncio.wait_for(
            prediction_use_cases.make_prediction(input_data, current_user.username),
            timeout=240.0  # 4 minutos
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408, 
            detail="La predicción está tomando más tiempo del esperado. Por favor, intente nuevamente."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/predictions", response_model=List[PredictionResult])
async def get_predictions(
    current_user: User = Depends(get_current_user),
    prediction_use_cases: PredictionUseCases = Depends(get_prediction_use_cases),
    limit: int = 10
):
    return await prediction_use_cases.get_user_predictions(current_user.username, limit)


@router.get("/predictions/{prediction_id}", response_model=PredictionResult)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    prediction_use_cases: PredictionUseCases = Depends(get_prediction_use_cases)
):
    try:
        prediction = await prediction_use_cases.get_prediction_by_id(prediction_id, current_user.username)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
