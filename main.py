from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.auth.auth_controller import router as auth_api
from app.api.v1.prediction.prediction_controller import router as prediction_api
from app.api.v1.prediction.cache_controller import router as cache_api
from app.infrastructure.database.database import engine
from app.infrastructure.database.models import Base
from app.middleware.logging_middleware import logging_middleware
from app.utils.logger import logger
from app.utils.exceptions import handle_exception

# Initialize Firebase at startup
import app.config.firestore

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Osinergmin Energy Prediction APIs - Arquitectura Hexagonal")

# Agregar middleware de logging
app.middleware("http")(logging_middleware)

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
    logger.info("Health check endpoint accessed")
    return {
        "message": "Osinergmin Energy Prediction APIs",
        "architecture": "Hexagonal (Clean Architecture)",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones"""
    http_exception = handle_exception(exc, f"{request.method} {request.url.path}")
    
    # Agregar request_id si está disponible
    request_id = getattr(request.state, 'request_id', None)
    if request_id and isinstance(http_exception.detail, dict):
        http_exception.detail["request_id"] = request_id
    
    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail
    )

# Log de inicio de la aplicación
logger.info("Application started successfully", extra_fields={
    "version": "2.0.0",
    "architecture": "Hexagonal"
})
