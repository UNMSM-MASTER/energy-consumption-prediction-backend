import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import traceback
import uuid

# Context variable para request ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class StructuredFormatter(logging.Formatter):
    """Formateador estructurado para logs en producción"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Crear estructura de log
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar request_id si está disponible
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Agregar excepción si existe
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Agregar campos extra si existen
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class ProductionLogger:
    """Logger configurado para producción"""
    
    def __init__(self, name: str = "energy_prediction"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicación de logs
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar handlers para stdout (docker logs)"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Usar formateador estructurado
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def _log_with_context(self, level: str, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log con contexto adicional"""
        record = self.logger.makeRecord(
            self.logger.name, 
            getattr(logging, level.upper()), 
            "", 0, 
            message, 
            (), 
            None
        )
        
        if extra_fields:
            record.extra_fields = extra_fields
        
        if exc_info:
            record.exc_info = sys.exc_info()
        
        self.logger.handle(record)
    
    def info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log de información"""
        self._log_with_context("INFO", message, extra_fields)
    
    def error(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """Log de errores"""
        self._log_with_context("ERROR", message, extra_fields, exc_info)
    
    def warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log de advertencias"""
        self._log_with_context("WARNING", message, extra_fields)
    
    def debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log de debug"""
        self._log_with_context("DEBUG", message, extra_fields)
    
    def critical(self, message: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """Log crítico"""
        self._log_with_context("CRITICAL", message, extra_fields, exc_info)

# Instancia global del logger
logger = ProductionLogger()

def get_request_id() -> str:
    """Obtener o generar request ID"""
    request_id = request_id_var.get()
    if not request_id:
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
    return request_id

def set_request_id(request_id: str):
    """Establecer request ID"""
    request_id_var.set(request_id) 