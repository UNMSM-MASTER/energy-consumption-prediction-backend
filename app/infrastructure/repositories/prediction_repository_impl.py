from typing import Optional, List
from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.domain.repositories.prediction_repository import PredictionRepository
from app.domain.entities.prediction import Prediction, PredictionCreate
from app.infrastructure.database.models.prediction_model import PredictionModel
from app.config.redis_config import get_redis

class PredictionRepositoryImpl(PredictionRepository):
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis()
    
    def _get_cache_key(self, target_date: datetime, user_id: int) -> str:
        return f"prediction:{user_id}:{target_date.strftime('%Y-%m-%d')}"
    
    async def create(self, prediction: PredictionCreate) -> Prediction:
        # Check cache first
        cache_key = self._get_cache_key(prediction.target_date, prediction.user_id)
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            cached_prediction = json.loads(cached_data)
            return Prediction(**cached_prediction)
        
        # Generate prediction using ML model (placeholder)
        consumption_prediction = 150.5  # This should come from your ML model
        confidence_interval = {"lower": 140.0, "upper": 160.0}
        
        db_prediction = PredictionModel(
            user_id=prediction.user_id,
            target_date=prediction.target_date,
            consumption_prediction=consumption_prediction,
            confidence_interval=confidence_interval,
            model_version=prediction.model_version,
            features_used=prediction.features_used,
            company=prediction.company
        )
        
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        
        # Cache the prediction
        prediction_entity = Prediction(
            id=db_prediction.id,
            user_id=db_prediction.user_id,
            prediction_date=db_prediction.prediction_date,
            target_date=db_prediction.target_date,
            consumption_prediction=db_prediction.consumption_prediction,
            confidence_interval=db_prediction.confidence_interval,
            model_version=db_prediction.model_version,
            features_used=db_prediction.features_used,
            company=db_prediction.company,
            created_at=db_prediction.created_at
        )
        
        # Cache for 24 hours
        self.redis.setex(
            cache_key,
            86400,  # 24 hours in seconds
            json.dumps(prediction_entity.dict(), default=str)
        )
        
        return prediction_entity
    
    async def get_by_id(self, prediction_id: int) -> Optional[Prediction]:
        db_prediction = self.db.query(PredictionModel).filter(PredictionModel.id == prediction_id).first()
        if db_prediction is None:
            return None
        return Prediction(
            id=db_prediction.id,
            user_id=db_prediction.user_id,
            prediction_date=db_prediction.prediction_date,
            target_date=db_prediction.target_date,
            consumption_prediction=db_prediction.consumption_prediction,
            confidence_interval=db_prediction.confidence_interval,
            model_version=db_prediction.model_version,
            features_used=db_prediction.features_used,
            company=db_prediction.company,
            created_at=db_prediction.created_at
        )
    
    async def get_by_user_id(self, user_id: int) -> List[Prediction]:
        db_predictions = self.db.query(PredictionModel).filter(PredictionModel.user_id == user_id).all()
        return [
            Prediction(
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
            for pred in db_predictions
        ]
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Prediction]:
        db_predictions = self.db.query(PredictionModel).filter(
            PredictionModel.target_date >= start_date,
            PredictionModel.target_date <= end_date
        ).all()
        return [
            Prediction(
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
            for pred in db_predictions
        ]
    
    async def get_all(self) -> List[Prediction]:
        db_predictions = self.db.query(PredictionModel).all()
        return [
            Prediction(
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
            for pred in db_predictions
        ]
    
    async def update(self, prediction: Prediction) -> Prediction:
        db_prediction = self.db.query(PredictionModel).filter(PredictionModel.id == prediction.id).first()
        if db_prediction:
            db_prediction.consumption_prediction = prediction.consumption_prediction
            db_prediction.confidence_interval = prediction.confidence_interval
            db_prediction.model_version = prediction.model_version
            db_prediction.features_used = prediction.features_used
            self.db.commit()
            self.db.refresh(db_prediction)
        return prediction
    
    async def delete(self, prediction_id: int) -> bool:
        db_prediction = self.db.query(PredictionModel).filter(PredictionModel.id == prediction_id).first()
        if db_prediction:
            # Clear cache
            cache_key = self._get_cache_key(db_prediction.target_date, db_prediction.user_id)
            self.redis.delete(cache_key)
            
            self.db.delete(db_prediction)
            self.db.commit()
            return True
        return False 