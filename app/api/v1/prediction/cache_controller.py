from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.infrastructure.services.forecast_cache_service import ForecastCacheService
from app.api.v1.prediction.services.lang import LagService
from app.ml_models.ml_model import MlModel

router = APIRouter(prefix="/cache", tags=["Cache Management"])

@router.get("/stats/{company}")
async def get_cache_stats(company: str):
    """
    Obtiene estadísticas del cache para una empresa específica
    """
    try:
        forecast_cache_service = ForecastCacheService()
        stats = await forecast_cache_service.get_cache_stats(company)
        return {
            "company": company,
            "cache_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@router.delete("/invalidate/{company}")
async def invalidate_cache(company: str):
    """
    Invalida el cache de predicciones para una empresa
    """
    try:
        forecast_cache_service = ForecastCacheService()
        success = await forecast_cache_service.invalidate_forecast_cache(company)
        
        if success:
            return {
                "message": f"Cache invalidated successfully for {company}",
                "company": company,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating cache: {str(e)}")

@router.get("/performance")
async def get_cache_performance():
    """
    Obtiene métricas de rendimiento del cache
    """
    try:
        forecast_cache_service = ForecastCacheService()
        metrics = await forecast_cache_service.get_performance_metrics()
        
        return {
            "cache_status": "active",
            "optimization_enabled": True,
            "cache_strategy": "forecast_series_caching_with_compression",
            "performance_metrics": metrics,
            "benefits": [
                "Reducción de tiempo de cálculo de lags",
                "Reutilización de predicciones intermedias",
                "Cache inteligente por empresa y fecha",
                "Compresión de datos para ahorrar espacio",
                "Métricas de rendimiento en tiempo real"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

@router.post("/preload/{company}")
async def preload_company_forecasts(company: str, hours_ahead: int = 24):
    """
    Precarga predicciones para una empresa específica
    """
    try:
        # Cargar modelo
        ml_model_loader = MlModel()
        model = ml_model_loader.load_model(company)
        
        # Precargar predicciones
        lag_service = LagService()
        results = await lag_service.preload_forecasts_for_company(company, model, hours_ahead)
        
        return {
            "message": f"Preloaded {results['total_predictions']} predictions for {company}",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preloading forecasts: {str(e)}")

@router.post("/preload/multiple")
async def preload_multiple_companies(companies: List[str], hours_ahead: int = 24):
    """
    Precarga predicciones para múltiples empresas
    """
    try:
        forecast_cache_service = ForecastCacheService()
        results = await forecast_cache_service.preload_common_forecasts(companies, hours_ahead)
        
        return {
            "message": f"Preload results for {len(companies)} companies",
            "results": results,
            "hours_ahead": hours_ahead
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preloading multiple companies: {str(e)}")

@router.get("/cleanup")
async def cleanup_cache():
    """
    Limpia cache expirado y retorna estadísticas
    """
    try:
        forecast_cache_service = ForecastCacheService()
        stats = await forecast_cache_service.cleanup_expired_cache()
        
        return {
            "message": "Cache cleanup completed",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up cache: {str(e)}")

@router.get("/health")
async def cache_health_check():
    """
    Verifica el estado de salud del cache
    """
    try:
        forecast_cache_service = ForecastCacheService()
        
        # Verificar conexión a Redis
        await forecast_cache_service.redis_client.ping()
        
        # Obtener métricas básicas
        metrics = await forecast_cache_service.get_performance_metrics()
        
        return {
            "status": "healthy",
            "redis_connection": "active",
            "cache_efficiency": metrics.get('cache_efficiency', 'Unknown'),
            "hit_rate": f"{metrics.get('hit_rate_percentage', 0)}%"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "redis_connection": "failed"
        } 