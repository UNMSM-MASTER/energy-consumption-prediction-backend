import io
import logging
from firebase_admin import storage
from google.cloud.exceptions import NotFound
import joblib

class MlModel:
    def __init__(self, bucket_name: str = "osinergmin-backend.firebasestorage.app"):
        """
        Inicializa el cargador de modelos con manejo robusto de errores

        Args:
            bucket_name: Nombre del bucket de Firebase Storage
        """
        try:
            if bucket_name:
                self.bucket = storage.bucket(bucket_name)
            else:
                self.bucket = storage.bucket()
            logging.info(f"Conectado al bucket: {self.bucket.name}")
        except Exception as e:
            logging.error(f"Error inicializando Firebase Storage: {str(e)}")
            raise

    def load_model(self, model_name: str):
        """Carga un modelo desde Firebase Storage con manejo robusto de errores"""
        try:
            # Normalizar nombre del modelo
            normalized_name = model_name.upper().strip()
            blob_path = f"models_prediction/{normalized_name}_random_forest_model.pkl"

            logging.info(f"Intentando cargar modelo desde: {blob_path}")

            # Obtener el blob
            blob = self.bucket.blob(blob_path)

            # Verificar existencia
            if not blob.exists():
                raise NotFound(f"El archivo {blob_path} no existe en el bucket")

            # Descargar como bytes
            model_bytes = blob.download_as_bytes()
            logging.info(f"Modelo descargado. Tamaño: {len(model_bytes)} bytes")

            try:
                with io.BytesIO(model_bytes) as f:
                    model = joblib.load(f)
                logging.info(f"Modelo {normalized_name} cargado exitosamente")
                return model
            # except pickle.UnpicklingError as e:
            #     raise ValueError(f"Error deserializando el modelo: {str(e)}")
            except Exception as e:
                raise ValueError(f"Error inesperado al cargar el modelo: {str(e)}")

        except NotFound as e:
            logging.error(f"Modelo no encontrado: {str(e)}")
            raise ValueError(f"Modelo {normalized_name} no encontrado en Storage") from e
        except Exception as e:
            logging.error(f"Error cargando modelo {normalized_name}: {str(e)}", exc_info=True)
            raise ValueError(f"Error cargando modelo {normalized_name}: {str(e)}") from e