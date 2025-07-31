"""
Esquemas Pydantic para validación de datos de entrada y salida.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import date
from enum import Enum

class PensionType(str, Enum):
    """Tipos de pensión válidos."""
    JUBILACION = "jubilacion"  # Jubilación ordinaria
    JUBILACION_ANTICIPADA = "jubilacion_anticipada"  # Jubilación anticipada
    INCAPACIDAD = "incapacidad" 
    VIUDEDAD = "viudedad"

class PeriodType(str, Enum):
    """Períodos del complemento de paternidad."""
    PERIOD_1 = "1"  # 01-01-2016 a 03-02-2021
    PERIOD_2 = "2"  # a partir de febrero 2021

class EligibilityRequest(BaseModel):
    """Esquema para verificar elegibilidad básica."""
    pension_type: PensionType = Field(..., description="Tipo de pensión (jubilacion|jubilacion_anticipada|incapacidad|viudedad)")
    start_date: date = Field(..., description="Fecha de inicio de la pensión (YYYY-MM-DD)")
    num_children: int = Field(..., ge=1, description="Número de hijos (mínimo 1)")
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Validar que la fecha esté en rango válido."""
        min_date = date(2016, 1, 1)
        if v < min_date:
            raise ValueError(f'La fecha debe ser posterior al {min_date}')
        return v

class EligibilityResponse(BaseModel):
    """Respuesta de elegibilidad."""
    eligible: bool = Field(..., description="Si cumple los criterios básicos")
    period: Optional[PeriodType] = Field(None, description="Período aplicable (1 o 2)")
    reason: Optional[str] = Field(None, description="Razón de no elegibilidad")

class CalculationRequest(BaseModel):
    """Esquema para calcular el complemento."""
    pension_type: PensionType = Field(..., description="Tipo de pensión")
    start_date: date = Field(..., description="Fecha de inicio de la pensión")
    num_children: int = Field(..., ge=1, le=4, description="Número de hijos (1-4)")
    pension_amount: float = Field(..., gt=0, description="Cuantía de la pensión en euros")
    
    @validator('start_date')
    def validate_start_date(cls, v):
        min_date = date(2016, 1, 1)
        if v < min_date:
            raise ValueError(f'La fecha debe ser posterior al {min_date}')
        return v

class CalculationResponse(BaseModel):
    """Respuesta del cálculo del complemento."""
    period: PeriodType = Field(..., description="Período aplicable")
    complement_percent: Optional[float] = Field(None, description="Porcentaje adicional (Período 1)")
    complement_fixed: Optional[float] = Field(None, description="Importe fijo por hijo (Período 2)")
    amount: float = Field(..., description="Cantidad total del complemento en euros")
    pension_with_complement: float = Field(..., description="Pensión total con complemento")

class RetroactiveRequest(BaseModel):
    """Esquema para cálculo de atrasos."""
    start_date: date = Field(..., description="Fecha de inicio del período")
    end_date: date = Field(..., description="Fecha de fin del período") 
    pension_amount: float = Field(..., gt=0, description="Cuantía de la pensión")
    num_children: int = Field(..., ge=1, le=4, description="Número de hijos")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class RetroactiveResponse(BaseModel):
    """Respuesta de cálculo de atrasos."""
    total_amount: float = Field(..., description="Total de atrasos acumulados")
    months_calculated: int = Field(..., description="Número de meses calculados")
    period_1_amount: Optional[float] = Field(None, description="Importe del Período 1")
    period_2_amount: Optional[float] = Field(None, description="Importe del Período 2")

class CompareProgenitor(BaseModel):
    """Datos de un progenitor para comparación."""
    name: str = Field(..., description="Nombre del progenitor")
    pension_amount: float = Field(..., gt=0, description="Cuantía de la pensión")
    num_children: int = Field(..., ge=1, le=4, description="Número de hijos")
    start_date: date = Field(..., description="Fecha de inicio de la pensión")
    pension_type: PensionType = Field(..., description="Tipo de pensión")

class CompareRequest(BaseModel):
    """Esquema para comparar dos progenitores."""
    progenitor_1: CompareProgenitor = Field(..., description="Datos del primer progenitor")
    progenitor_2: CompareProgenitor = Field(..., description="Datos del segundo progenitor")

class CompareResult(BaseModel):
    """Resultado de la comparación de un progenitor."""
    name: str = Field(..., description="Nombre del progenitor")
    eligible: bool = Field(..., description="Si tiene derecho al complemento")
    complement_amount: Optional[float] = Field(None, description="Cantidad del complemento")
    total_pension: Optional[float] = Field(None, description="Pensión total con complemento")

class CompareResponse(BaseModel):
    """Respuesta de comparación entre progenitores."""
    eligible_progenitor: str = Field(..., description="Nombre del progenitor con derecho")
    progenitor_1: CompareResult = Field(..., description="Resultado del primer progenitor")
    progenitor_2: CompareResult = Field(..., description="Resultado del segundo progenitor")
    explanation: str = Field(..., description="Explicación de por qué tiene derecho")

class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""
    status: str = Field(..., description="Estado del servicio")
    timestamp: str = Field(..., description="Marca de tiempo")
    version: str = Field(..., description="Versión de la API")

class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje descriptivo del error")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")