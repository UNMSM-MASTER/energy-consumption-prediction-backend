import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
import gzip
import pickle
from app.config.settings import get_settings

settings = get_settings()

class ForecastCacheService:
    """
    Servicio para manejar el cache de predicciones intermedias
    y optimizar el cálculo de lags futuros
    """
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)  # Cambiar a False para compresión
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0
        }
    
    async def get_cached_forecast(self, company: str, last_real_date: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtiene predicciones cacheadas para una empresa desde una fecha específica
        """
        cache_key = f"forecast_series:{company}:{last_real_date.strftime('%Y-%m-%d-%H')}"
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                # Descomprimir datos si están comprimidos
                try:
                    data = pickle.loads(gzip.decompress(cached_data))
                except:
                    # Fallback para datos no comprimidos
                    data = json.loads(cached_data.decode('utf-8'))
                
                # Convertir de vuelta a pandas Series
                predictions = pd.Series(data['predictions'])
                self.performance_metrics['cache_hits'] += 1
                return {
                    'predictions': predictions,
                    'last_updated': data['last_updated'],
                    'steps': len(predictions)
                }
            self.performance_metrics['cache_misses'] += 1
            return None
        except Exception:
            self.performance_metrics['cache_misses'] += 1
            return None
    
    async def get_cached_lags(self, company: str, target_date: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtiene lags específicos cacheados para una fecha objetivo
        """
        cache_key = f"lags:{company}:{target_date.strftime('%Y-%m-%d-%H')}"
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = pickle.loads(gzip.decompress(cached_data))
                self.performance_metrics['cache_hits'] += 1
                return data
            self.performance_metrics['cache_misses'] += 1
            return None
        except Exception:
            self.performance_metrics['cache_misses'] += 1
            return None
    
    async def cache_lags(self, company: str, target_date: datetime, lags: list, meta: Dict[str, Any], expire: int = 3600) -> bool:
        """
        Cachea lags específicos para una fecha objetivo
        """
        cache_key = f"lags:{company}:{target_date.strftime('%Y-%m-%d-%H')}"
        
        try:
            data = {
                'lags': lags,
                'meta': meta,
                'cached_at': datetime.now().isoformat(),
                'company': company,
                'target_date': target_date.isoformat()
            }
            
            # Comprimir datos para ahorrar espacio
            compressed_data = gzip.compress(pickle.dumps(data))
            await self.redis_client.set(cache_key, compressed_data, ex=expire)
            return True
        except Exception:
            return False
    
    async def cache_forecast_series(self, company: str, last_real_date: datetime, 
                                  predictions: pd.Series, expire: int = 3600) -> bool:
        """
        Cachea una serie de predicciones para una empresa con compresión
        """
        cache_key = f"forecast_series:{company}:{last_real_date.strftime('%Y-%m-%d-%H')}"
        
        try:
            # Preparar datos para cache
            forecast_data = {
                'predictions': predictions.to_dict(),
                'last_updated': datetime.now().isoformat(),
                'company': company,
                'last_real_date': last_real_date.isoformat(),
                'compressed': True
            }
            
            # Comprimir datos para ahorrar espacio
            compressed_data = gzip.compress(pickle.dumps(forecast_data))
            await self.redis_client.set(cache_key, compressed_data, ex=expire)
            return True
        except Exception:
            return False
    
    async def get_or_extend_forecast(self, company: str, model, last_real_date: datetime, 
                                   target_date: datetime, series: pd.Series) -> pd.Series:
        """
        Obtiene predicciones cacheadas o las extiende si es necesario
        """
        # Intentar obtener predicciones existentes
        cached_forecast = await self.get_cached_forecast(company, last_real_date)
        
        if cached_forecast:
            predictions = cached_forecast['predictions']
            max_cached_date = predictions.index.max()
            
            # Si tenemos suficientes predicciones, usarlas
            if target_date <= max_cached_date:
                return predictions
            
            # Si necesitamos más predicciones, extender desde el último punto
            return await self._extend_forecast(company, model, predictions, max_cached_date, target_date)
        else:
            # Calcular nuevas predicciones desde el inicio
            return await self._calculate_new_forecast(company, model, last_real_date, target_date, series)
    
    async def _extend_forecast(self, company: str, model, existing_predictions: pd.Series, 
                              from_date: datetime, target_date: datetime) -> pd.Series:
        """
        Extiende predicciones existentes desde una fecha específica
        """
        current_dt = from_date + timedelta(hours=1)
        history = existing_predictions.copy()
        
        feature_names = ['hour', 'dayofweek', 'month', 'year', 'is_weekend', 'is_peak', 'lag_1', 'lag_2', 'lag_3']
        
        while current_dt <= target_date:
            try:
                lag_1 = history.loc[current_dt - timedelta(hours=1)]
                lag_2 = history.loc[current_dt - timedelta(hours=2)]
                lag_3 = history.loc[current_dt - timedelta(hours=3)]
            except KeyError:
                raise ValueError("No hay datos suficientes para calcular los lags.")

            features = [
                current_dt.hour, current_dt.dayofweek,
                current_dt.month, current_dt.year,
                int(current_dt.dayofweek in [5, 6]),
                int(current_dt.hour in [7, 8, 18, 19]),
                lag_1, lag_2, lag_3
            ]

            features_df = pd.DataFrame([features], columns=feature_names)
            prediction = model.predict(features_df)[0]
            history.loc[current_dt] = prediction
            current_dt += timedelta(hours=1)
        
        # Actualizar cache con predicciones extendidas
        await self.cache_forecast_series(company, history.index.min() - timedelta(hours=1), history)
        
        return history
    
    async def _calculate_new_forecast(self, company: str, model, last_real_date: datetime, 
                                    target_date: datetime, series: pd.Series) -> pd.Series:
        """
        Calcula una nueva serie de predicciones desde el último dato real
        """
        current_dt = last_real_date + timedelta(hours=1)
        history = series.copy()
        
        feature_names = ['hour', 'dayofweek', 'month', 'year', 'is_weekend', 'is_peak', 'lag_1', 'lag_2', 'lag_3']
        
        while current_dt <= target_date:
            try:
                lag_1 = history.loc[current_dt - timedelta(hours=1)]
                lag_2 = history.loc[current_dt - timedelta(hours=2)]
                lag_3 = history.loc[current_dt - timedelta(hours=3)]
            except KeyError:
                raise ValueError("No hay datos suficientes para calcular los lags.")

            features = [
                current_dt.hour, current_dt.dayofweek,
                current_dt.month, current_dt.year,
                int(current_dt.dayofweek in [5, 6]),
                int(current_dt.hour in [7, 8, 18, 19]),
                lag_1, lag_2, lag_3
            ]

            features_df = pd.DataFrame([features], columns=feature_names)
            prediction = model.predict(features_df)[0]
            history.loc[current_dt] = prediction
            current_dt += timedelta(hours=1)
        
        # Cachear las nuevas predicciones
        await self.cache_forecast_series(company, last_real_date, history)
        
        return history
    
    async def invalidate_forecast_cache(self, company: str) -> bool:
        """
        Invalida el cache de predicciones para una empresa
        """
        try:
            pattern = f"forecast_series:{company}:*"
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception:
            return False
    
    async def get_cache_stats(self, company: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache para una empresa
        """
        try:
            pattern = f"forecast_series:{company}:*"
            keys = await self.redis_client.keys(pattern)
            
            stats = {
                'cached_forecasts': len(keys),
                'keys': keys,
                'total_size': 0,
                'performance': self.performance_metrics
            }
            
            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        stats['total_size'] += len(data)
                except Exception:
                    pass
            
            return stats
        except Exception:
            return {'error': 'Could not retrieve cache stats'}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del cache
        """
        total_requests = self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']
        hit_rate = (self.performance_metrics['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.performance_metrics['cache_hits'],
            'cache_misses': self.performance_metrics['cache_misses'],
            'total_requests': total_requests,
            'hit_rate_percentage': round(hit_rate, 2),
            'cache_efficiency': 'Excellent' if hit_rate > 80 else 'Good' if hit_rate > 60 else 'Needs Improvement'
        }
    
    async def preload_common_forecasts(self, companies: List[str], hours_ahead: int = 24) -> Dict[str, bool]:
        """
        Precarga predicciones comunes para empresas específicas
        """
        results = {}
        target_date = datetime.now() + timedelta(hours=hours_ahead)
        
        for company in companies:
            try:
                # Verificar si ya existe cache
                cached = await self.get_cached_forecast(company, datetime.now())
                if not cached:
                    # Aquí podrías implementar precarga automática
                    results[company] = False
                else:
                    results[company] = True
            except Exception:
                results[company] = False
        
        return results
    
    async def cleanup_expired_cache(self) -> Dict[str, int]:
        """
        Limpia cache expirado y retorna estadísticas
        """
        try:
            # Redis maneja automáticamente la expiración, pero podemos obtener estadísticas
            all_keys = await self.redis_client.keys("forecast_series:*")
            lag_keys = await self.redis_client.keys("lags:*")
            
            return {
                'forecast_keys': len(all_keys),
                'lag_keys': len(lag_keys),
                'total_keys': len(all_keys) + len(lag_keys),
                'cleanup_status': 'Automatic expiration handled by Redis'
            }
        except Exception:
            return {'error': 'Could not cleanup cache'} 