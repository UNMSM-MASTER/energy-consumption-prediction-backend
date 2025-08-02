from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.repositories.prediction_repository import PredictionRepository
from app.domain.entities.prediction import PredictionResult, PredictionCreate
from app.infrastructure.database.models import Prediction as PredictionModel
import uuid


class PostgreSQLPredictionRepository(PredictionRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, prediction: PredictionCreate) -> PredictionResult:
        prediction_id = str(uuid.uuid4())
        db_prediction = PredictionModel(
            prediction_id=prediction_id,
            input_data=prediction.input_data.dict(),
            parsed_features=prediction.parsed_features,
            prediction_meta=prediction.prediction_meta,
            prediction=prediction.prediction,
            created_by=prediction.created_by
        )
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        
        return PredictionResult(
            id=db_prediction.id,
            prediction_id=db_prediction.prediction_id,
            input_data=prediction.input_data,
            parsed_features=db_prediction.parsed_features,
            prediction_meta=db_prediction.prediction_meta,
            prediction=db_prediction.prediction,
            created_at=db_prediction.created_at,
            created_by=db_prediction.created_by
        )

    async def get_by_id(self, prediction_id: int) -> Optional[PredictionResult]:
        db_prediction = self.db.query(PredictionModel).filter(PredictionModel.id == prediction_id).first()
        if not db_prediction:
            return None
            
        return PredictionResult(
            id=db_prediction.id,
            prediction_id=db_prediction.prediction_id,
            input_data=db_prediction.input_data,
            parsed_features=db_prediction.parsed_features,
            prediction_meta=db_prediction.prediction_meta,
            prediction=db_prediction.prediction,
            created_at=db_prediction.created_at,
            created_by=db_prediction.created_by
        )

    async def get_by_prediction_id(self, prediction_id: str) -> Optional[PredictionResult]:
        db_prediction = self.db.query(PredictionModel).filter(PredictionModel.prediction_id == prediction_id).first()
        if not db_prediction:
            return None
            
        return PredictionResult(
            id=db_prediction.id,
            prediction_id=db_prediction.prediction_id,
            input_data=db_prediction.input_data,
            parsed_features=db_prediction.parsed_features,
            prediction_meta=db_prediction.prediction_meta,
            prediction=db_prediction.prediction,
            created_at=db_prediction.created_at,
            created_by=db_prediction.created_by
        )

    async def get_by_user(self, username: str, limit: int = 10) -> List[PredictionResult]:
        db_predictions = self.db.query(PredictionModel)\
            .filter(PredictionModel.created_by == username)\
            .order_by(PredictionModel.created_at.desc())\
            .limit(limit)\
            .all()
            
        return [
            PredictionResult(
                id=pred.id,
                prediction_id=pred.prediction_id,
                input_data=pred.input_data,
                parsed_features=pred.parsed_features,
                prediction_meta=pred.prediction_meta,
                prediction=pred.prediction,
                created_at=pred.created_at,
                created_by=pred.created_by
            )
            for pred in db_predictions
        ]

    async def delete(self, prediction_id: int) -> bool:
        db_prediction = self.db.query(PredictionModel).filter(PredictionModel.id == prediction_id).first()
        if not db_prediction:
            return False

        self.db.delete(db_prediction)
        self.db.commit()
        return True

    async def list_predictions(self, skip: int = 0, limit: int = 100) -> List[PredictionResult]:
        db_predictions = self.db.query(PredictionModel)\
            .order_by(PredictionModel.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
            
        return [
            PredictionResult(
                id=pred.id,
                prediction_id=pred.prediction_id,
                input_data=pred.input_data,
                parsed_features=pred.parsed_features,
                prediction_meta=pred.prediction_meta,
                prediction=pred.prediction,
                created_at=pred.created_at,
                created_by=pred.created_by
            )
            for pred in db_predictions
        ] 