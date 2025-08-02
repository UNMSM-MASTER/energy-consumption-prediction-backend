import io
import os
from firebase_admin import storage
from google.cloud.exceptions import NotFound
import joblib
from app.utils.logger import logger
from app.utils.exceptions import ModelLoadException, FirebaseException

class MlModel:
    def __init__(self, bucket_name: str = "doctoria-pe.firebasestorage.app"):
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
            
            logger.info(
                "Firebase Storage connected successfully",
                extra_fields={
                    "bucket_name": self.bucket.name,
                    "operation": "initialize"
                }
            )
        except Exception as e:
            logger.error(
                "Failed to initialize Firebase Storage",
                extra_fields={
                    "bucket_name": bucket_name,
                    "operation": "initialize",
                    "error": str(e)
                },
                exc_info=True
            )
            raise FirebaseException(
                f"Error inicializando Firebase Storage: {str(e)}",
                operation="initialize",
                details={"bucket_name": bucket_name}
            )

    def load_model(self, model_name: str):
        """Carga un modelo desde Firebase Storage con manejo robusto de errores"""
        try:
            # Normalizar nombre del modelo
            normalized_name = model_name.upper().strip()
            blob_path = f"models_prediction/{normalized_name}_random_forest_model.pkl"

            logger.info(
                "Loading model from Firebase Storage",
                extra_fields={
                    "model_name": normalized_name,
                    "blob_path": blob_path,
                    "operation": "load_model"
                }
            )

            # Obtener el blob
            blob = self.bucket.blob(blob_path)

            # Verificar existencia
            if not blob.exists():
                logger.error(
                    "Model not found in Firebase Storage",
                    extra_fields={
                        "model_name": normalized_name,
                        "blob_path": blob_path,
                        "operation": "load_model"
                    }
                )
                raise ModelLoadException(
                    f"Modelo {normalized_name} no encontrado en Storage",
                    model_name=normalized_name,
                    details={"blob_path": blob_path}
                )

            # Descargar como bytes
            model_bytes = blob.download_as_bytes()
            logger.info(
                "Model downloaded successfully",
                extra_fields={
                    "model_name": normalized_name,
                    "size_bytes": len(model_bytes),
                    "operation": "download"
                }
            )

            try:
                with io.BytesIO(model_bytes) as f:
                    model = joblib.load(f)
                
                logger.info(
                    "Model loaded successfully",
                    extra_fields={
                        "model_name": normalized_name,
                        "model_type": type(model).__name__,
                        "operation": "deserialize"
                    }
                )
                return model
            except Exception as e:
                logger.error(
                    "Failed to deserialize model",
                    extra_fields={
                        "model_name": normalized_name,
                        "size_bytes": len(model_bytes),
                        "operation": "deserialize",
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise ModelLoadException(
                    f"Error inesperado al cargar el modelo: {str(e)}",
                    model_name=normalized_name,
                    details={"operation": "deserialize", "size_bytes": len(model_bytes)}
                )

        except NotFound as e:
            logger.error(
                "Model not found in Firebase Storage",
                extra_fields={
                    "model_name": normalized_name,
                    "blob_path": blob_path,
                    "operation": "load_model"
                }
            )
            raise ModelLoadException(
                f"Modelo {normalized_name} no encontrado en Storage",
                model_name=normalized_name,
                details={"blob_path": blob_path, "firebase_error": str(e)}
            )
        except ModelLoadException:
            # Re-raise ModelLoadException sin modificar
            raise
        except Exception as e:
            logger.error(
                "Unexpected error loading model",
                extra_fields={
                    "model_name": normalized_name,
                    "blob_path": blob_path,
                    "operation": "load_model",
                    "error": str(e)
                },
                exc_info=True
            )
            raise ModelLoadException(
                f"Error cargando modelo {normalized_name}: {str(e)}",
                model_name=normalized_name,
                details={"blob_path": blob_path, "error": str(e)}
            )