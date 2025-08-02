import pandas as pd
import os
from datetime import timedelta
import json
from typing import Dict, Any, Tuple, Optional
from app.config.settings import get_settings
from app.infrastructure.services.forecast_cache_service import ForecastCacheService

settings = get_settings()

class LagService:
    def __init__(self):
        csv_path = os.path.join(os.path.dirname(__file__), "data/pjm_hourly_est.csv")
        df = pd.read_csv(csv_path)
        df.columns = [col.upper().strip() for col in df.columns]
        df["DATETIME"] = pd.to_datetime(df["DATETIME"])
        df.set_index("DATETIME", inplace=True)

        valid_columns = [col for col in df.columns if df[col].notna().sum() > 100000]
        df = df[valid_columns]

        self.df_base = df
        # Inicializar servicio de cache optimizado
        self.forecast_cache_service = ForecastCacheService()

    async def get_forecast_lags(self, company_name: str, model, target_dt: pd.Timestamp):
        """
        Calcula los lags necesarios para la predicción futura con cache optimizado
        """
        # Validar compañía en columnas
        if company_name not in self.df_base.columns:
            raise ValueError(f"{company_name} no está en el DataFrame base.")

        # Extraer datos de la empresa y limpiar NaN
        series = self.df_base[company_name].dropna()
        last_dt = pd.to_datetime(series.index.max())

        # Si la fecha objetivo está en el pasado, usar datos históricos
        if target_dt <= last_dt:
            try:
                lag_1 = series.loc[target_dt - timedelta(hours=1)]
                lag_2 = series.loc[target_dt - timedelta(hours=2)]
                lag_3 = series.loc[target_dt - timedelta(hours=3)]
            except KeyError:
                raise ValueError("No hay datos históricos disponibles para la fecha especificada.")

            return (
                [lag_1, lag_2, lag_3],
                {
                    "steps": 0,
                    "last_real": {
                        "lag_1": lag_1,
                        "lag_2": lag_2,
                        "lag_3": lag_3,
                    }
                }
            )

        # Para fechas futuras, verificar cache de lags específicos primero
        cached_lags = await self.forecast_cache_service.get_cached_lags(company_name, target_dt.to_pydatetime())
        if cached_lags:
            return cached_lags['lags'], cached_lags['meta']

        # Si no hay cache, calcular y cachear
        lags, meta = await self._get_future_lags_with_cache(company_name, model, target_dt, series, last_dt)
        
        # Cachear los lags específicos para futuras consultas
        await self.forecast_cache_service.cache_lags(company_name, target_dt.to_pydatetime(), lags, meta)
        
        return lags, meta

    async def _get_future_lags_with_cache(self, company_name: str, model, target_dt: pd.Timestamp, 
                                         series: pd.Series, last_dt: pd.Timestamp) -> Tuple[list, Dict[str, Any]]:
        """
        Calcula lags futuros usando cache optimizado para evitar recálculos
        """
        # Usar el servicio de cache optimizado
        history = await self.forecast_cache_service.get_or_extend_forecast(
            company_name, model, last_dt, target_dt, series
        )

        # Obtener lags requeridos
        try:
            lag_1 = history.loc[target_dt - timedelta(hours=1)]
            lag_2 = history.loc[target_dt - timedelta(hours=2)]
            lag_3 = history.loc[target_dt - timedelta(hours=3)]
        except KeyError:
            # Si no tenemos suficientes predicciones, extender más
            history = await self.forecast_cache_service.get_or_extend_forecast(
                company_name, model, last_dt, target_dt + timedelta(hours=3), series
            )
            
            lag_1 = history.loc[target_dt - timedelta(hours=1)]
            lag_2 = history.loc[target_dt - timedelta(hours=2)]
            lag_3 = history.loc[target_dt - timedelta(hours=3)]

        steps = len(history) - len(series)
        
        return (
            [lag_1, lag_2, lag_3],
            {
                "steps": steps,
                "last_real": {
                    "lag_1": series.loc[last_dt],
                    "lag_2": series.loc[last_dt - timedelta(hours=1)],
                    "lag_3": series.loc[last_dt - timedelta(hours=2)],
                }
            }
        )

    async def get_multiple_forecast_lags(self, company_name: str, model, target_dates: list) -> Dict[str, Tuple[list, Dict[str, Any]]]:
        """
        Calcula lags para múltiples fechas objetivo de manera optimizada
        """
        results = {}
        
        for target_dt in target_dates:
            if isinstance(target_dt, str):
                target_dt = pd.Timestamp(target_dt)
            
            lags, meta = await self.get_forecast_lags(company_name, model, target_dt)
            results[target_dt.isoformat()] = (lags, meta)
        
        return results

    async def preload_forecasts_for_company(self, company_name: str, model, hours_ahead: int = 24) -> Dict[str, Any]:
        """
        Precarga predicciones para una empresa para las próximas horas
        """
        from datetime import datetime
        
        current_time = datetime.now()
        target_times = [current_time + timedelta(hours=i) for i in range(1, hours_ahead + 1)]
        
        results = {}
        for target_time in target_times:
            try:
                lags, meta = await self.get_forecast_lags(company_name, model, pd.Timestamp(target_time))
                results[target_time.isoformat()] = {
                    'lags': lags,
                    'steps': meta['steps']
                }
            except Exception as e:
                results[target_time.isoformat()] = {'error': str(e)}
        
        return {
            'company': company_name,
            'hours_ahead': hours_ahead,
            'predictions': results,
            'total_predictions': len(results)
        }

    def _prepare_features(self, dt, lags):
        return [
            dt.hour,
            dt.dayofweek,
            dt.month,
            dt.year,
            1 if dt.dayofweek >= 5 else 0,
            1 if dt.hour in [7, 8, 18, 19] else 0,
            lags[0],
            lags[1],
            lags[2],
        ]
