"""
Complemento de Paternidad API
API para calcular y gestionar el Complemento de Paternidad según la normativa española.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from .routes import router
from .logging_config import setup_logging
from .schemas import ErrorResponse

def create_app() -> FastAPI:
    """Crear y configurar la aplicación FastAPI."""
    
    # Configurar logging
    setup_logging()
    
    app = FastAPI(
        title="Complemento de Paternidad API",
        description="API para calcular y gestionar el Complemento de Paternidad según la normativa española",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Registrar manejadores de excepciones
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Manejador de errores de validación."""
        logging.error(f"Error de validación: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="ValidationError",
                message=str(exc)
            ).dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejador general de errores."""
        logging.error(f"Error interno: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="InternalServerError",
                message="Error interno del servidor"
            ).dict()
        )
    
    # Registrar rutas
    app.include_router(router)
    
    return app

app = create_app()