from app.config.firestore import db
from app.db_models.main import User, PredictionResult, PredictionInput
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from firebase_admin import firestore
import pandas as pd

from app.utils.main import get_current_active_user
from app.ml_models.ml_model import MlModel
from app.api.v1.prediction.services.lang import LagService
from datetime import datetime

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
    responses={404: {"description": "Not found"}}
)

model_loader = MlModel()
lag_service = LagService()


@router.post("/predict", response_model=PredictionResult)
async def make_prediction(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    try:
        dt = pd.to_datetime(input_data.datetime)
        # if dt < datetime.now():
        #     raise ValueError("La fecha debe ser futura")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fecha inválida: {str(e)}")

    try:
        # Cargar modelo
        model = model_loader.load_model(input_data.company.upper())

        # Obtener lags predictivos
        lags, meta = lag_service.get_forecast_lags(
            input_data.company.upper(),
            model,
            dt
        )

        # Preparar features finales
        features = lag_service._prepare_features(dt, lags)

        # Hacer predicción final
        prediction = model.predict([features])[0]

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al predecir: {str(e)}")

    # Preparar respuesta
    prediction_data = {
        "input_data": input_data.dict(),
        "parsed_features": {
            "hour": dt.hour,
            "dayofweek": dt.dayofweek,
            "month": dt.month,
            "year": dt.year,
            "is_weekend": 1 if dt.dayofweek >= 5 else 0,
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
        "created_at": datetime.utcnow().isoformat(),
        "created_by": current_user.username
    }

    # Guardar en Firestore
    doc_ref = db.collection("predictions").document()
    doc_ref.set(prediction_data)

    return {
        "prediction_id": doc_ref.id,
        **prediction_data
    }

@router.get("/predictions", response_model=List[PredictionResult])
async def get_predictions(
    current_user: User = Depends(get_current_active_user),
    limit: int = 10
):
    # Get predictions for the current user
    predictions_ref = db.collection("predictions")
    query = predictions_ref.where("created_by", "==", current_user.username) \
                          .order_by("created_at", direction=firestore.Query.DESCENDING) \
                          .limit(limit)

    predictions = []
    for doc in query.stream():
        pred_data = doc.to_dict()
        predictions.append({
            "prediction_id": doc.id,
            **pred_data
        })

    return predictions

@router.get("/predictions/{prediction_id}", response_model=PredictionResult)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_active_user)
):
    doc_ref = db.collection("predictions").document(prediction_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Prediction not found")

    pred_data = doc.to_dict()

    # Check if the prediction belongs to the current user
    if pred_data["created_by"] != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to access this prediction")

    return {
        "prediction_id": doc.id,
        **pred_data
            }
