from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.config.database import get_db
from app.domain.entities.prediction import PredictionCreate, PredictionResponse
from app.application.services.prediction_application_service import PredictionApplicationService
from app.infrastructure.repositories.prediction_repository_impl import PredictionRepositoryImpl

router = APIRouter(prefix="/predictions", tags=["predictions"])

def get_prediction_service(db: Session = Depends(get_db)) -> PredictionApplicationService:
    prediction_repository = PredictionRepositoryImpl(db)
    return PredictionApplicationService(prediction_repository)

@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    prediction_request: PredictionCreate,
    prediction_service: PredictionApplicationService = Depends(get_prediction_service)
):
    """Create a new energy consumption prediction"""
    try:
        prediction = await prediction_service.generate_prediction(prediction_request)
        return PredictionResponse(
            id=prediction.id,
            user_id=prediction.user_id,
            prediction_date=prediction.prediction_date,
            target_date=prediction.target_date,
            consumption_prediction=prediction.consumption_prediction,
            confidence_interval=prediction.confidence_interval,
            model_version=prediction.model_version,
            features_used=prediction.features_used,
            company=prediction.company,
            created_at=prediction.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}", response_model=List[PredictionResponse])
async def get_user_predictions(
    user_id: int,
    prediction_service: PredictionApplicationService = Depends(get_prediction_service)
):
    """Get all predictions for a specific user"""
    try:
        predictions = await prediction_service.get_user_predictions(user_id)
        return [
            PredictionResponse(
                id=pred.id,
                user_id=pred.user_id,
                prediction_date=pred.prediction_date,
                target_date=pred.target_date,
                consumption_prediction=pred.consumption_prediction,
                confidence_interval=pred.confidence_interval,
                model_version=pred.model_version,
                features_used=pred.features_used,
                company=pred.company,
                created_at=pred.created_at
            )
            for pred in predictions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/date-range/", response_model=List[PredictionResponse])
async def get_predictions_by_date_range(
    start_date: datetime,
    end_date: datetime,
    prediction_service: PredictionApplicationService = Depends(get_prediction_service)
):
    """Get predictions within a date range"""
    try:
        predictions = await prediction_service.get_predictions_by_date_range(start_date, end_date)
        return [
            PredictionResponse(
                id=pred.id,
                user_id=pred.user_id,
                prediction_date=pred.prediction_date,
                target_date=pred.target_date,
                consumption_prediction=pred.consumption_prediction,
                confidence_interval=pred.confidence_interval,
                model_version=pred.model_version,
                features_used=pred.features_used,
                company=pred.company,
                created_at=pred.created_at
            )
            for pred in predictions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/user/{user_id}/cache")
async def clear_user_cache(
    user_id: int,
    prediction_service: PredictionApplicationService = Depends(get_prediction_service)
):
    """Clear all cached predictions for a user"""
    try:
        await prediction_service.clear_user_cache(user_id)
        return {"message": f"Cache cleared for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
