#!/usr/bin/env python3
"""
Script de monitoreo para verificar el estado de la aplicación
"""
import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.repositories.cache_repository_impl import RedisCacheRepository
from app.infrastructure.services.forecast_cache_service import ForecastCacheService
from app.utils.logger import logger

async def check_application_health():
    """Verifica el estado de salud de la aplicación"""
    try:
        # Verificar endpoint de salud básico
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Health check básico: OK")
        else:
            logger.error(f"❌ Health check básico falló: {response.status_code}")
            return False
        
        # Verificar endpoint de salud detallado
        response = requests.get("http://localhost:8000/health/detailed", timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ Health check detallado: {health_data['status']}")
            
            # Mostrar estado de componentes
            for component, status in health_data.get('components', {}).items():
                logger.info(f"  - {component}: {status}")
        else:
            logger.error(f"❌ Health check detallado falló: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando salud de la aplicación: {str(e)}")
        return False

async def check_cache_performance():
    """Verifica el rendimiento del cache"""
    try:
        cache_repo = RedisCacheRepository()
        forecast_service = ForecastCacheService()
        
        # Verificar conexión a Redis
        await cache_repo.ping()
        logger.info("✅ Redis: Conectado")
        
        # Obtener métricas de rendimiento
        metrics = await forecast_service.get_performance_metrics()
        logger.info(f"📊 Métricas de cache:")
        logger.info(f"  - Hit rate: {metrics.get('hit_rate_percentage', 0)}%")
        logger.info(f"  - Cache hits: {metrics.get('cache_hits', 0)}")
        logger.info(f"  - Cache misses: {metrics.get('cache_misses', 0)}")
        logger.info(f"  - Eficiencia: {metrics.get('cache_efficiency', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando cache: {str(e)}")
        return False

async def test_prediction_endpoint():
    """Prueba el endpoint de predicción con un request simple"""
    try:
        # Datos de prueba
        test_data = {
            "company": "PJM",
            "datetime": "2024-01-15 12:00:00"
        }
        
        logger.info("🧪 Probando endpoint de predicción...")
        
        # Nota: Este test requiere autenticación, por lo que solo verificamos que el endpoint responde
        response = requests.post(
            "http://localhost:8000/prediction/predict",
            json=test_data,
            timeout=60  # Timeout extendido para predicciones
        )
        
        if response.status_code in [200, 401, 403]:  # 401/403 son esperados sin auth
            logger.info(f"✅ Endpoint de predicción responde: {response.status_code}")
            return True
        else:
            logger.error(f"❌ Endpoint de predicción falló: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout en endpoint de predicción")
        return False
    except Exception as e:
        logger.error(f"❌ Error probando endpoint de predicción: {str(e)}")
        return False

async def main():
    """Función principal de monitoreo"""
    logger.info("🔍 Iniciando monitoreo de la aplicación...")
    
    results = {
        "health_check": False,
        "cache_performance": False,
        "prediction_endpoint": False
    }
    
    # Verificar salud de la aplicación
    results["health_check"] = await check_application_health()
    
    # Verificar rendimiento del cache
    results["cache_performance"] = await check_cache_performance()
    
    # Probar endpoint de predicción
    results["prediction_endpoint"] = await test_prediction_endpoint()
    
    # Resumen
    logger.info("📋 Resumen del monitoreo:")
    for test, result in results.items():
        status = "✅ OK" if result else "❌ FALLÓ"
        logger.info(f"  - {test}: {status}")
    
    # Determinar estado general
    all_passed = all(results.values())
    if all_passed:
        logger.info("🎉 Todas las verificaciones pasaron")
        sys.exit(0)
    else:
        logger.error("⚠️ Algunas verificaciones fallaron")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 