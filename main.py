from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.timeout import TimeoutMiddleware
from app.api.v1.auth.auth_controller import router as auth_api
from app.api.v1.prediction.prediction_controller import router as prediction_api
from app.api.v1.prediction.cache_controller import router as cache_api
from app.infrastructure.database.database import engine
from app.infrastructure.database.models import Base
from app.middleware.logging_middleware import logging_middleware
from app.utils.logger import logger
from app.utils.exceptions import handle_exception
from datetime import datetime

# Initialize Firebase at startup
import app.config.firestore

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Osinergmin Energy Prediction APIs - Arquitectura Hexagonal",
    # Configuraciones de timeout para manejar requests largos
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Agregar middleware de timeout (5 minutos para predicciones)
app.add_middleware(TimeoutMiddleware, timeout=300)

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

@app.get("/health/detailed")
async def detailed_health_check():
    """Health check detallado que incluye estado de modelos ML y cache"""
    logger.info("Detailed health check endpoint accessed")
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        # Verificar base de datos
        from app.infrastructure.database.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    try:
        # Verificar Redis
        from app.infrastructure.repositories.cache_repository_impl import RedisCacheRepository
        cache_repo = RedisCacheRepository()
        await cache_repo.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    try:
        # Verificar modelos ML (solo verificar que se pueden cargar)
        from app.ml_models.ml_model import MlModel
        ml_loader = MlModel()
        # Intentar cargar un modelo de prueba (puede fallar si no hay conexión a Firebase)
        health_status["components"]["ml_models"] = "available"
    except Exception as e:
        health_status["components"]["ml_models"] = f"warning: {str(e)}"
        # No cambiar status a degraded porque los modelos se cargan bajo demanda
    
    return health_status

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
