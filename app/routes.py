"""
Endpoints REST para la API del Complemento de Paternidad.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import json

from .schemas import (
    EligibilityRequest, EligibilityResponse,
    CalculationRequest, CalculationResponse,
    RetroactiveRequest, RetroactiveResponse,
    CompareRequest, CompareResponse,
    HealthResponse, ErrorResponse
)
from .services import ComplementoPaternidadService
from .logging_config import get_logger

logger = get_logger('routes')
router = APIRouter()
service = ComplementoPaternidadService()

# Los manejadores de excepciones se registrarán en la aplicación principal

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de verificación de salud del servicio.
    
    Returns:
        Estado del servicio, timestamp y versión
    """
    logger.info("Health check solicitado")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + 'Z',
        version="1.0.0"
    )

@router.get("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(
    pension_type: str,
    start_date: str,
    num_children: int
):
    """
    Verificar si el solicitante cumple los criterios básicos de elegibilidad.
    
    Args:
        pension_type: Tipo de pensión (jubilacion|jubilacion_anticipada|incapacidad|viudedad)
        start_date: Fecha de inicio de la pensión (YYYY-MM-DD)
        num_children: Número de hijos (entero >= 1)
        
    Returns:
        Resultado de elegibilidad con período aplicable
    """
    try:
        request_data = EligibilityRequest(
            pension_type=pension_type,
            start_date=start_date,
            num_children=num_children
        )
    except Exception as e:
        logger.error(f"Error validando parámetros de elegibilidad: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parámetros inválidos: {str(e)}")
    
    logger.info(f"Verificando elegibilidad: {request_data.dict()}")
    
    result = service.check_eligibility(
        request_data.pension_type,
        request_data.start_date,
        request_data.num_children
    )
    
    logger.info(f"Resultado elegibilidad: {result.dict()}")
    return result

@router.post("/calculate", response_model=CalculationResponse)
async def calculate_complement(request: CalculationRequest):
    """
    Calcular el complemento de paternidad.
    
    Args:
        request: Datos de la pensión y solicitante
        
    Returns:
        Cálculo detallado del complemento incluyendo período y cantidad
    """
    logger.info(f"Calculando complemento: {request.dict()}")
    
    try:
        result = service.calculate_complement(
            request.pension_type,
            request.start_date,
            request.num_children,
            request.pension_amount
        )
        
        logger.info(f"Complemento calculado: {result.amount}€")
        return result
        
    except ValueError as e:
        logger.error(f"Error en cálculo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error interno en cálculo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno en el cálculo")

@router.get("/retroactive", response_model=RetroactiveResponse)
async def calculate_retroactive(
    start_date: str,
    end_date: str,
    pension_amount: float,
    num_children: int
):
    """
    Calcular el total de atrasos acumulados entre dos fechas.
    
    Args:
        start_date: Fecha de inicio del período (YYYY-MM-DD)
        end_date: Fecha de fin del período (YYYY-MM-DD)
        pension_amount: Cuantía de la pensión en euros
        num_children: Número de hijos
        
    Returns:
        Total de atrasos acumulados con desglose por períodos
    """
    try:
        request_data = RetroactiveRequest(
            start_date=start_date,
            end_date=end_date,
            pension_amount=pension_amount,
            num_children=num_children
        )
    except Exception as e:
        logger.error(f"Error validando parámetros retroactivos: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parámetros inválidos: {str(e)}")
    
    logger.info(f"Calculando atrasos: {request_data.dict()}")
    
    try:
        result = service.calculate_retroactive(
            request_data.start_date,
            request_data.end_date,
            request_data.pension_amount,
            request_data.num_children
        )
        
        response = RetroactiveResponse(**result)
        logger.info(f"Atrasos calculados: {response.total_amount}€ en {response.months_calculated} meses")
        return response
        
    except Exception as e:
        logger.error(f"Error calculando atrasos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno calculando atrasos")

@router.post("/compare", response_model=CompareResponse)
async def compare_progenitors(request: CompareRequest):
    """
    Comparar dos progenitores para determinar quién tiene derecho al complemento.
    
    Args:
        request: Datos de ambos progenitores
        
    Returns:
        Resultado de la comparación indicando quién tiene derecho y por qué
    """
    logger.info(f"Comparando progenitores: {request.progenitor_1.name} vs {request.progenitor_2.name}")
    
    try:
        progenitor_1_data = request.progenitor_1.dict()
        progenitor_2_data = request.progenitor_2.dict()
        
        result = service.compare_progenitors(progenitor_1_data, progenitor_2_data)
        
        response = CompareResponse(**result)
        logger.info(f"Resultado comparación: {response.eligible_progenitor} tiene derecho")
        return response
        
    except Exception as e:
        logger.error(f"Error comparando progenitores: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno en la comparación")

@router.get("/spec")
async def get_openapi_spec():
    """
    Obtener la especificación OpenAPI/Swagger de la API.
    
    Returns:
        Especificación OpenAPI en formato JSON
    """
    from ..__init__ import app
    
    logger.info("Especificación OpenAPI solicitada")
    
    openapi_schema = app.openapi()
    
    # Añadir información adicional a la especificación
    openapi_schema["info"]["description"] = """
    API para calcular y gestionar el Complemento de Paternidad según la normativa española.
    
    ## Períodos de aplicación:
    - **Período 1** (01/01/2016 - 03/02/2021): Solo jubilaciones ordinarias (excluye anticipadas), cálculo porcentual
    - **Período 2** (desde 04/02/2021): Jubilación, incapacidad y viudedad, importe fijo por hijo
    
    ## Reglas de cálculo:
    ### Período 1:
    - 2 hijos → 5% adicional
- 3 hijos → 10% adicional
- ≥4 hijos → 15% adicional
    
    ### Período 2:
    - 35,90€ por hijo (máximo 4 hijos)
    - Solo puede cobrarse uno de los dos posibles complementos (el de menor cuantía)
    """
    
    openapi_schema["info"]["contact"] = {
        "name": "Complemento de Paternidad API",
        "email": "soporte@complementopaternidad.es"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    return openapi_schema