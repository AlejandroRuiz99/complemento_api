"""
Tests unitarios para las funciones de utilidad.
"""

import pytest
from datetime import date
from app.utils import (
    date_to_period, calculate_months_between_dates, format_currency,
    validate_date_range, is_valid_pension_date, calculate_annual_amount,
    normalize_pension_type, get_period_description, round_currency
)
from app.schemas import PeriodType

class TestUtils:
    """Tests para funciones de utilidad."""
    
    def test_date_to_period_period_1(self):
        """Test conversión de fecha a período 1."""
        test_date = date(2020, 6, 15)
        result = date_to_period(test_date)
        assert result == PeriodType.PERIOD_1
    
    def test_date_to_period_period_2(self):
        """Test conversión de fecha a período 2."""
        test_date = date(2021, 6, 15)
        result = date_to_period(test_date)
        assert result == PeriodType.PERIOD_2
    
    def test_date_to_period_boundary_period_1_start(self):
        """Test fecha límite inicio período 1."""
        test_date = date(2016, 1, 1)
        result = date_to_period(test_date)
        assert result == PeriodType.PERIOD_1
    
    def test_date_to_period_boundary_period_1_end(self):
        """Test fecha límite fin período 1."""
        test_date = date(2021, 2, 3)
        result = date_to_period(test_date)
        assert result == PeriodType.PERIOD_1
    
    def test_date_to_period_boundary_period_2_start(self):
        """Test fecha límite inicio período 2."""
        test_date = date(2021, 4, 1)
        result = date_to_period(test_date)
        assert result == PeriodType.PERIOD_2
    
    def test_date_to_period_gap_between_periods(self):
        """Test fecha en el gap entre períodos."""
        test_date = date(2021, 3, 15)  # Entre período 1 y 2
        result = date_to_period(test_date)
        assert result is None
    
    def test_date_to_period_before_period_1(self):
        """Test fecha anterior al período 1."""
        test_date = date(2015, 12, 31)
        result = date_to_period(test_date)
        assert result is None
    
    def test_calculate_months_between_dates_same_year(self):
        """Test cálculo de meses en el mismo año."""
        start = date(2021, 3, 15)
        end = date(2021, 6, 15)
        result = calculate_months_between_dates(start, end)
        assert result == 3
    
    def test_calculate_months_between_dates_different_years(self):
        """Test cálculo de meses en años diferentes."""
        start = date(2020, 10, 15)
        end = date(2021, 2, 15)
        result = calculate_months_between_dates(start, end)
        assert result == 4
    
    def test_calculate_months_between_dates_reverse_order(self):
        """Test cálculo de meses con fechas invertidas."""
        start = date(2021, 6, 15)
        end = date(2021, 3, 15)
        result = calculate_months_between_dates(start, end)
        assert result == 0
    
    def test_format_currency(self):
        """Test formateo de moneda."""
        result = format_currency(1234.56)
        assert result == "1234.56€"
    
    def test_format_currency_round(self):
        """Test formateo de moneda con redondeo."""
        result = format_currency(1234.567)
        assert result == "1234.57€"
    
    def test_validate_date_range_valid(self):
        """Test validación de rango de fechas válido."""
        start = date(2021, 1, 1)
        end = date(2021, 12, 31)
        result = validate_date_range(start, end)
        assert result == True
    
    def test_validate_date_range_invalid(self):
        """Test validación de rango de fechas inválido."""
        start = date(2021, 12, 31)
        end = date(2021, 1, 1)
        result = validate_date_range(start, end)
        assert result == False
    
    def test_is_valid_pension_date_valid(self):
        """Test validación de fecha de pensión válida."""
        test_date = date(2020, 6, 15)
        result = is_valid_pension_date(test_date)
        assert result == True
    
    def test_is_valid_pension_date_too_early(self):
        """Test validación de fecha de pensión muy temprana."""
        test_date = date(2015, 6, 15)
        result = is_valid_pension_date(test_date)
        assert result == False
    
    def test_calculate_annual_amount(self):
        """Test cálculo de importe anual."""
        monthly = 100.0
        result = calculate_annual_amount(monthly)
        assert result == 1400.0  # 12 + 2 pagas extra
    
    def test_normalize_pension_type(self):
        """Test normalización de tipo de pensión."""
        result = normalize_pension_type("  JUBILACION  ")
        assert result == "jubilacion"
    
    def test_get_period_description_period_1(self):
        """Test descripción del período 1."""
        result = get_period_description(PeriodType.PERIOD_1)
        assert "Período 1" in result
        assert "porcentual" in result
    
    def test_get_period_description_period_2(self):
        """Test descripción del período 2."""
        result = get_period_description(PeriodType.PERIOD_2)
        assert "Período 2" in result
        assert "importe fijo" in result
    
    def test_round_currency(self):
        """Test redondeo de moneda."""
        result = round_currency(123.456789)
        assert result == 123.46
    
    def test_round_currency_exact(self):
        """Test redondeo de moneda exacta."""
        result = round_currency(123.45)
        assert result == 123.45