from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.utils.logger import logger, get_request_id

class EnergyPredictionException(Exception):
    """Excepción base para la aplicación de predicción de energía"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.request_id = get_request_id()
        
        # Log del error
        logger.error(
            f"Application error: {message}",
            extra_fields={
                "error_code": self.error_code,
                "request_id": self.request_id,
                "details": self.details
            }
        )
        
        super().__init__(self.message)

class DatabaseException(EnergyPredictionException):
    """Excepción para errores de base de datos"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_ERROR", details)

class CacheException(EnergyPredictionException):
    """Excepción para errores de cache"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "CACHE_ERROR", details)

class ModelLoadException(EnergyPredictionException):
    """Excepción para errores de carga de modelos ML"""
    
    def __init__(self, message: str, model_name: str = None, details: Dict[str, Any] = None):
        if model_name:
            details = details or {}
            details["model_name"] = model_name
        super().__init__(message, "MODEL_LOAD_ERROR", details)

class PredictionException(EnergyPredictionException):
    """Excepción para errores de predicción"""
    
    def __init__(self, message: str, company: str = None, details: Dict[str, Any] = None):
        if company:
            details = details or {}
            details["company"] = company
        super().__init__(message, "PREDICTION_ERROR", details)

class AuthenticationException(EnergyPredictionException):
    """Excepción para errores de autenticación"""
    
    def __init__(self, message: str, user: str = None, details: Dict[str, Any] = None):
        if user:
            details = details or {}
            details["user"] = user
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class ValidationException(EnergyPredictionException):
    """Excepción para errores de validación"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
        if field or value:
            details = details or {}
            if field:
                details["field"] = field
            if value:
                details["value"] = str(value)
        super().__init__(message, "VALIDATION_ERROR", details)

class FirebaseException(EnergyPredictionException):
    """Excepción para errores de Firebase"""
    
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        if operation:
            details = details or {}
            details["operation"] = operation
        super().__init__(message, "FIREBASE_ERROR", details)

def handle_exception(exc: Exception, context: str = None) -> HTTPException:
    """Manejar excepciones y convertirlas a HTTPException apropiadas"""
    
    request_id = get_request_id()
    
    # Log del error con contexto
    logger.error(
        f"Unhandled exception in {context or 'unknown context'}: {str(exc)}",
        extra_fields={
            "exception_type": type(exc).__name__,
            "request_id": request_id,
            "context": context
        },
        exc_info=True
    )
    
    # Mapear excepciones personalizadas a códigos HTTP
    if isinstance(exc, ValidationException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": exc.message,
                "error_code": exc.error_code,
                "request_id": request_id,
                "details": exc.details
            }
        )
    
    elif isinstance(exc, AuthenticationException):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": exc.message,
                "error_code": exc.error_code,
                "request_id": request_id,
                "details": exc.details
            }
        )
    
    elif isinstance(exc, (DatabaseException, CacheException, ModelLoadException, FirebaseException)):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": exc.message,
                "error_code": exc.error_code,
                "request_id": request_id,
                "details": exc.details
            }
        )
    
    elif isinstance(exc, PredictionException):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": exc.message,
                "error_code": exc.error_code,
                "request_id": request_id,
                "details": exc.details
            }
        )
    
    # Excepción genérica
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "request_id": request_id,
                "message": str(exc) if str(exc) else "Unknown error occurred"
            }
        )

def log_request_info(method: str, path: str, user: str = None, extra_fields: Dict[str, Any] = None):
    """Log de información de request"""
    fields = {
        "method": method,
        "path": path,
        "request_id": get_request_id()
    }
    
    if user:
        fields["user"] = user
    
    if extra_fields:
        fields.update(extra_fields)
    
    logger.info(f"Request: {method} {path}", extra_fields=fields)

def log_response_info(status_code: int, response_time: float, extra_fields: Dict[str, Any] = None):
    """Log de información de response"""
    fields = {
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "request_id": get_request_id()
    }
    
    if extra_fields:
        fields.update(extra_fields)
    
    logger.info(f"Response: {status_code} ({response_time:.3f}s)", extra_fields=fields) 