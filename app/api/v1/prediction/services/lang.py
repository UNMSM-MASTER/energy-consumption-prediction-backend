import pandas as pd
import os
from datetime import timedelta
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

    def get_forecast_lags(self, company_name: str, model, target_dt: pd.Timestamp):
        """
        Calcula los lags necesarios para la predicción futura
        """
        # Validar compañía en columnas
        if company_name not in self.df_base.columns:
            raise ValueError(f"{company_name} no está en el DataFrame base.")

        # Extraer datos de la empresa y limpiar NaN
        series = self.df_base[company_name].dropna()

        last_dt = pd.to_datetime(series.index.max())

        current_dt = last_dt + timedelta(hours=1)

        if target_dt <= last_dt:
            raise ValueError("La fecha debe ser futura respecto al último dato real.")

        history = series.copy()

        steps = 0
        while current_dt <= target_dt:
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

            prediction = model.predict([features])[0]
            history.loc[current_dt] = prediction
            current_dt += timedelta(hours=1)
            steps += 1

        return (
            [
                history.loc[target_dt - timedelta(hours=i)]
                for i in [1, 2, 3]
            ],
            {
                "steps": steps,
                "last_real": {
                    "lag_1": series.loc[last_dt],
                    "lag_2": series.loc[last_dt - timedelta(hours=1)],
                    "lag_3": series.loc[last_dt - timedelta(hours=2)],
                }
            }
        )

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
