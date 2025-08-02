import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.utils.logger import logger, set_request_id, get_request_id
from app.utils.exceptions import handle_exception, log_request_info, log_response_info

async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware para logging automático de requests y responses"""
    
    # Generar request ID único
    request_id = str(uuid.uuid4())
    set_request_id(request_id)
    
    # Agregar request_id al request para uso posterior
    request.state.request_id = request_id
    
    # Obtener información del usuario si está autenticado
    user = None
    try:
        if hasattr(request.state, 'user'):
            user = request.state.user.username if hasattr(request.state.user, 'username') else str(request.state.user)
    except:
        pass
    
    # Log del request
    start_time = time.time()
    log_request_info(
        method=request.method,
        path=str(request.url.path),
        user=user,
        extra_fields={
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    try:
        # Procesar el request
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        response_time = time.time() - start_time
        
        # Log del response exitoso
        log_response_info(
            status_code=response.status_code,
            response_time=response_time,
            extra_fields={
                "content_length": response.headers.get("content-length"),
                "content_type": response.headers.get("content-type")
            }
        )
        
        # Agregar request_id al header de respuesta
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as exc:
        # Calcular tiempo hasta el error
        response_time = time.time() - start_time
        
        # Log del error
        logger.error(
            f"Request failed after {response_time:.3f}s",
            extra_fields={
                "method": request.method,
                "path": str(request.url.path),
                "user": user,
                "response_time": response_time,
                "exception_type": type(exc).__name__
            },
            exc_info=True
        )
        
        # Manejar la excepción y convertir a HTTPException
        http_exception = handle_exception(exc, f"{request.method} {request.url.path}")
        
        # Crear respuesta de error con request_id
        error_response = JSONResponse(
            status_code=http_exception.status_code,
            content=http_exception.detail
        )
        error_response.headers["X-Request-ID"] = request_id
        
        return error_response 