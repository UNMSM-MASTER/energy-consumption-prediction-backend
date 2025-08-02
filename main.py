from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth.auth_controller import router as auth_api
from app.api.v1.prediction.prediction_controller import router as prediction_api
from app.api.v1.prediction.cache_controller import router as cache_api
from app.infrastructure.database.database import engine
from app.infrastructure.database.models import Base

# Initialize Firebase at startup
import app.config.firestore

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Osinergmin Energy Prediction APIs - Arquitectura Hexagonal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api)
app.include_router(prediction_api)
app.include_router(cache_api)

@app.get("/")
def read_root():
    return {
        "message": "Osinergmin Energy Prediction APIs",
        "architecture": "Hexagonal (Clean Architecture)",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
