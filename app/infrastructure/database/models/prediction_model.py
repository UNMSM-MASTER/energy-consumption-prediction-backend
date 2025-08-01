from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class PredictionModel(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True), nullable=False)
    consumption_prediction = Column(Float, nullable=False)
    confidence_interval = Column(JSON, nullable=True)
    model_version = Column(String, nullable=False)
    features_used = Column(JSON, nullable=True)
    company = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("UserModel", back_populates="predictions") 