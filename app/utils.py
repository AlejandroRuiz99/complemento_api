"""
Funciones de utilidad para el cálculo del Complemento de Paternidad.
"""

from datetime import date, datetime
from typing import Optional
from .schemas import PeriodType

def date_to_period(input_date: date) -> Optional[PeriodType]:
    """
    Determinar a qué período pertenece una fecha.
    
    Args:
        input_date: Fecha a evaluar
        
    Returns:
        PeriodType correspondiente o None si está fuera de rango
    """
    period_1_start = date(2016, 1, 1)
    period_1_end = date(2021, 2, 3)
    period_2_start = date(2021, 4, 1)
    
    if period_1_start <= input_date <= period_1_end:
        return PeriodType.PERIOD_1
    elif input_date >= period_2_start:
        return PeriodType.PERIOD_2
    else:
        return None

def calculate_months_between_dates(start_date: date, end_date: date) -> int:
    """
    Calcular el número de meses entre dos fechas.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        Número de meses entre las fechas
    """
    if end_date < start_date:
        return 0
    
    months = (end_date.year - start_date.year) * 12
    months += end_date.month - start_date.month
    
    return months

def format_currency(amount: float) -> str:
    """
    Formatear cantidad como moneda española.
    
    Args:
        amount: Cantidad a formatear
        
    Returns:
        String formateado como moneda
    """
    return f"{amount:.2f}€"

def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validar que el rango de fechas sea correcto.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        
    Returns:
        True si el rango es válido
    """
    return start_date < end_date

def get_current_year() -> int:
    """Obtener el año actual."""
    return datetime.now().year

def is_valid_pension_date(pension_date: date) -> bool:
    """
    Verificar si una fecha de pensión es válida para el complemento.
    
    Args:
        pension_date: Fecha de inicio de la pensión
        
    Returns:
        True si la fecha es válida
    """
    min_date = date(2016, 1, 1)
    max_date = date.today()
    
    return min_date <= pension_date <= max_date

def calculate_annual_amount(monthly_amount: float) -> float:
    """
    Calcular el importe anual incluyendo pagas extraordinarias.
    
    Args:
        monthly_amount: Importe mensual
        
    Returns:
        Importe anual (12 mensualidades + 2 pagas extra)
    """
    return monthly_amount * 14

def normalize_pension_type(pension_type: str) -> str:
    """
    Normalizar el tipo de pensión a formato estándar.
    
    Args:
        pension_type: Tipo de pensión
        
    Returns:
        Tipo de pensión normalizado
    """
    return pension_type.lower().strip()

def get_period_description(period: PeriodType) -> str:
    """
    Obtener descripción textual del período.
    
    Args:
        period: Período del complemento
        
    Returns:
        Descripción del período
    """
    if period == PeriodType.PERIOD_1:
        return "Período 1 (01/01/2016 - 03/02/2021): Solo jubilación, cálculo porcentual"
    elif period == PeriodType.PERIOD_2:
        return "Período 2 (desde 01/04/2021): Jubilación e incapacidad, importe fijo"
    else:
        return "Período no definido"

def round_currency(amount: float) -> float:
    """
    Redondear cantidad a 2 decimales (céntimos).
    
    Args:
        amount: Cantidad a redondear
        
    Returns:
        Cantidad redondeada a 2 decimales
    """
    return round(amount, 2)