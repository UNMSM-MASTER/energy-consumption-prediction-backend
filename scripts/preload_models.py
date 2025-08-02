#!/usr/bin/env python3
"""
Script para precargar modelos ML comunes y mejorar el rendimiento
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.repositories.cache_repository_impl import RedisCacheRepository
from app.infrastructure.services.forecast_cache_service import ForecastCacheService
from app.ml_models.ml_model import MlModel
from app.utils.logger import logger

async def preload_common_models():
    """Precarga modelos ML comunes para mejorar rendimiento"""
    logger.info("Iniciando precarga de modelos ML...")
    
    # Lista de empresas comunes
    common_companies = ['PJM', 'AEP', 'DOMINION', 'DUKE', 'SOUTHERN']
    
    try:
        # Inicializar servicios
        cache_repo = RedisCacheRepository()
        forecast_service = ForecastCacheService()
        ml_loader = MlModel()
        
        # Verificar conexión a Redis
        await cache_repo.ping()
        logger.info("Conexión a Redis establecida")
        
        # Precargar modelos
        loaded_models = {}
        for company in common_companies:
            try:
                logger.info(f"Precargando modelo para {company}...")
                model = ml_loader.load_model(company)
                loaded_models[company] = model
                logger.info(f"Modelo {company} cargado exitosamente")
            except Exception as e:
                logger.warning(f"No se pudo cargar modelo para {company}: {str(e)}")
        
        # Precargar predicciones comunes para las próximas 24 horas
        logger.info("Precargando predicciones comunes...")
        current_time = datetime.now()
        target_time = current_time + timedelta(hours=24)
        
        for company, model in loaded_models.items():
            try:
                # Precargar predicciones para las próximas horas
                await forecast_service.preload_common_forecasts([company], hours_ahead=24)
                logger.info(f"Predicciones precargadas para {company}")
            except Exception as e:
                logger.warning(f"Error precargando predicciones para {company}: {str(e)}")
        
        logger.info("Precarga de modelos completada")
        return True
        
    except Exception as e:
        logger.error(f"Error durante la precarga: {str(e)}")
        return False

async def cleanup_old_cache():
    """Limpia cache antiguo para liberar espacio"""
    try:
        forecast_service = ForecastCacheService()
        stats = await forecast_service.cleanup_expired_cache()
        logger.info(f"Limpieza de cache completada: {stats}")
    except Exception as e:
        logger.warning(f"Error durante limpieza de cache: {str(e)}")

if __name__ == "__main__":
    async def main():
        # Limpiar cache antiguo
        await cleanup_old_cache()
        
        # Precargar modelos
        success = await preload_common_models()
        
        if success:
            logger.info("Precarga completada exitosamente")
            sys.exit(0)
        else:
            logger.error("Precarga falló")
            sys.exit(1)
    
    asyncio.run(main()) 