from typing import Optional, List
from datetime import datetime
import json
from app.domain.services.prediction_service import PredictionService
from app.domain.repositories.prediction_repository import PredictionRepository
from app.domain.entities.prediction import Prediction, PredictionCreate
from app.config.redis_config import get_redis

class PredictionApplicationService(PredictionService):
    def __init__(self, prediction_repository: PredictionRepository):
        self.prediction_repository = prediction_repository
        self.redis = get_redis()
    
    async def generate_prediction(self, prediction_request: PredictionCreate) -> Prediction:
        """Generate energy consumption prediction for a given date"""
        # Validate request
        if not await self.validate_prediction_request(prediction_request):
            raise ValueError("Invalid prediction request")
        
        # Check cache first
        cached_prediction = await self.get_cached_prediction(
            prediction_request.target_date, 
            prediction_request.user_id
        )
        
        if cached_prediction:
            return cached_prediction
        
        # Generate new prediction
        prediction = await self.prediction_repository.create(prediction_request)
        
        # Cache the prediction
        await self.cache_prediction(prediction)
        
        return prediction
    
    async def get_cached_prediction(self, target_date: datetime, user_id: int) -> Optional[Prediction]:
        """Get cached prediction from Redis if available"""
        cache_key = f"prediction:{user_id}:{target_date.strftime('%Y-%m-%d')}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            try:
                cached_dict = json.loads(cached_data)
                # Convert string dates back to datetime objects
                cached_dict['prediction_date'] = datetime.fromisoformat(cached_dict['prediction_date'])
                cached_dict['target_date'] = datetime.fromisoformat(cached_dict['target_date'])
                cached_dict['created_at'] = datetime.fromisoformat(cached_dict['created_at'])
                return Prediction(**cached_dict)
            except (json.JSONDecodeError, KeyError, ValueError):
                # If cache is corrupted, delete it
                self.redis.delete(cache_key)
        
        return None
    
    async def cache_prediction(self, prediction: Prediction) -> None:
        """Cache prediction in Redis for future use"""
        cache_key = f"prediction:{prediction.user_id}:{prediction.target_date.strftime('%Y-%m-%d')}"
        
        # Cache for 24 hours
        self.redis.setex(
            cache_key,
            86400,  # 24 hours in seconds
            json.dumps(prediction.dict(), default=str)
        )
    
    async def validate_prediction_request(self, prediction_request: PredictionCreate) -> bool:
        """Validate prediction request parameters"""
        # Check if target date is in the future
        if prediction_request.target_date <= datetime.now():
            return False
        
        # Check if target date is not too far in the future (e.g., 10 years)
        max_future_date = datetime.now().replace(year=datetime.now().year + 10)
        if prediction_request.target_date > max_future_date:
            return False
        
        # Check if user_id is valid
        if prediction_request.user_id <= 0:
            return False
        
        return True
    
    async def get_user_predictions(self, user_id: int) -> List[Prediction]:
        """Get all predictions for a specific user"""
        return await self.prediction_repository.get_by_user_id(user_id)
    
    async def get_predictions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Prediction]:
        """Get predictions within a date range"""
        return await self.prediction_repository.get_by_date_range(start_date, end_date)
    
    async def clear_user_cache(self, user_id: int) -> None:
        """Clear all cached predictions for a user"""
        pattern = f"prediction:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys) 