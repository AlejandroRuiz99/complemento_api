"""
Tests unitarios para los servicios de cálculo del complemento.
"""

import pytest
from datetime import date
from app.services import ComplementoPaternidadService
from app.schemas import PensionType, PeriodType

class TestComplementoPaternidadService:
    """Tests para ComplementoPaternidadService."""
    
    def setup_method(self):
        """Configurar test."""
        self.service = ComplementoPaternidadService()
    
    def test_check_eligibility_period_1_jubilacion_valid(self):
        """Test elegibilidad período 1 con jubilación válida."""
        result = self.service.check_eligibility(
            PensionType.JUBILACION,
            date(2020, 6, 15),
            2
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_1
        assert result.reason is None
    
    def test_check_eligibility_period_1_incapacidad_valid(self):
        """Test elegibilidad período 1 con incapacidad (válida)."""
        result = self.service.check_eligibility(
            PensionType.INCAPACIDAD,
            date(2020, 6, 15),
            2
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_1
        assert result.reason is None
    
    def test_check_eligibility_period_1_viudedad_valid(self):
        """Test elegibilidad período 1 con viudedad (válida)."""
        result = self.service.check_eligibility(
            PensionType.VIUDEDAD,
            date(2020, 6, 15),
            2
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_1
        assert result.reason is None
    
    def test_check_eligibility_period_1_one_child_invalid(self):
        """Test elegibilidad período 1 con 1 hijo (no válida)."""
        result = self.service.check_eligibility(
            PensionType.JUBILACION,
            date(2020, 6, 15),
            1
        )
        
        assert result.eligible == False
        assert result.period == PeriodType.PERIOD_1
        assert "Para el Período 1 se requieren al menos 2 hijos" in result.reason
    
    def test_check_eligibility_period_2_jubilacion_valid(self):
        """Test elegibilidad período 2 con jubilación válida."""
        result = self.service.check_eligibility(
            PensionType.JUBILACION,
            date(2021, 6, 15),
            1
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_2
        assert result.reason is None
    
    def test_check_eligibility_period_2_incapacidad_valid(self):
        """Test elegibilidad período 2 con incapacidad válida."""
        result = self.service.check_eligibility(
            PensionType.INCAPACIDAD,
            date(2021, 6, 15),
            1
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_2
        assert result.reason is None
    
    def test_check_eligibility_period_2_viudedad_valid(self):
        """Test elegibilidad período 2 con viudedad (válida)."""
        result = self.service.check_eligibility(
            PensionType.VIUDEDAD,
            date(2021, 6, 15),
            1
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_2
        assert result.reason is None
    
    def test_check_eligibility_period_1_jubilacion_anticipada_invalid(self):
        """Test elegibilidad período 1 con jubilación anticipada (no válida)."""
        result = self.service.check_eligibility(
            PensionType.JUBILACION_ANTICIPADA,
            date(2020, 6, 15),
            2
        )
        
        assert result.eligible == False
        assert result.period == PeriodType.PERIOD_1
        assert "En el Período 1 solo aplica para jubilación, viudedad e incapacidad" in result.reason
    
    def test_check_eligibility_period_2_jubilacion_anticipada_valid(self):
        """Test elegibilidad período 2 con jubilación anticipada (válida)."""
        result = self.service.check_eligibility(
            PensionType.JUBILACION_ANTICIPADA,
            date(2021, 6, 15),
            1
        )
        
        assert result.eligible == True
        assert result.period == PeriodType.PERIOD_2
        assert result.reason is None
    
    def test_calculate_complement_period_1_two_children(self):
        """Test cálculo período 1 con 2 hijos (5%)."""
        result = self.service.calculate_complement(
            PensionType.JUBILACION,
            date(2020, 6, 15),
            2,
            1000.0
        )
        
        assert result.period == PeriodType.PERIOD_1
        assert result.complement_percent == 5.0
        assert result.complement_fixed is None
        assert result.amount == 50.0  # 5% de 1000€
        assert result.pension_with_complement == 1050.0
    
    def test_calculate_complement_period_1_three_children(self):
        """Test cálculo período 1 con 3 hijos (10%)."""
        result = self.service.calculate_complement(
            PensionType.JUBILACION,
            date(2020, 6, 15),
            3,
            1500.0
        )
        
        assert result.period == PeriodType.PERIOD_1
        assert result.complement_percent == 10.0
        assert result.amount == 150.0  # 10% de 1500€
        assert result.pension_with_complement == 1650.0
    
    def test_calculate_complement_period_1_four_or_more_children(self):
        """Test cálculo período 1 con 4+ hijos (15%)."""
        result = self.service.calculate_complement(
            PensionType.JUBILACION,
            date(2020, 6, 15),
            4,
            2000.0
        )
        
        assert result.period == PeriodType.PERIOD_1
        assert result.complement_percent == 15.0
        assert result.amount == 300.0  # 15% de 2000€
        assert result.pension_with_complement == 2300.0
    
    def test_calculate_complement_period_1_one_child_error(self):
        """Test cálculo período 1 con 1 hijo (error)."""
        with pytest.raises(ValueError) as exc_info:
            self.service.calculate_complement(
                PensionType.JUBILACION,
                date(2020, 6, 15),
                1,
                1000.0
            )
        
        assert "Para el Período 1, se requieren al menos 2 hijos" in str(exc_info.value)
    
    def test_calculate_complement_period_2_one_child(self):
        """Test cálculo período 2 con 1 hijo."""
        result = self.service.calculate_complement(
            PensionType.JUBILACION,
            date(2021, 6, 15),
            1,
            1000.0
        )
        
        assert result.period == PeriodType.PERIOD_2
        assert result.complement_percent is None
        assert result.complement_fixed == 35.90
        assert result.amount == 35.90  # 35,90€ por hijo
        assert result.pension_with_complement == 1035.90
    
    def test_calculate_complement_period_2_four_children(self):
        """Test cálculo período 2 con 4 hijos."""
        result = self.service.calculate_complement(
            PensionType.JUBILACION,
            date(2021, 6, 15),
            4,
            1500.0
        )
        
        assert result.period == PeriodType.PERIOD_2
        assert result.complement_fixed == 35.90
        assert result.amount == 143.60  # 4 × 35,90€
        assert result.pension_with_complement == 1643.60
    
    def test_calculate_complement_period_2_more_than_four_children(self):
        """Test cálculo período 2 con más de 4 hijos (máximo 4)."""
        result = self.service.calculate_complement(
            PensionType.JUBILACION,
            date(2021, 6, 15),
            6,
            1500.0
        )
        
        assert result.period == PeriodType.PERIOD_2
        assert result.amount == 143.60  # máximo 4 × 35,90€
        assert result.pension_with_complement == 1643.60
    
    def test_calculate_retroactive_basic(self):
        """Test cálculo básico de atrasos."""
        result = self.service.calculate_retroactive(
            date(2021, 5, 1),
            date(2021, 8, 1),
            1000.0,
            2
        )
        
        assert result['total_amount'] > 0
        assert result['months_calculated'] == 3
        assert result['period_2_amount'] > 0
        assert result['period_1_amount'] is None
    
    def test_compare_progenitors_both_eligible(self):
        """Test comparación con ambos progenitores elegibles."""
        progenitor_1 = {
            'name': 'María',
            'pension_type': PensionType.JUBILACION,
            'start_date': date(2021, 6, 15),
            'num_children': 2,
            'pension_amount': 1000.0
        }
        
        progenitor_2 = {
            'name': 'José',
            'pension_type': PensionType.JUBILACION,
            'start_date': date(2021, 6, 15),
            'num_children': 2,
            'pension_amount': 1200.0
        }
        
        result = self.service.compare_progenitors(progenitor_1, progenitor_2)
        
        assert result['eligible_progenitor'] == 'María'  # menor pensión
        assert result['progenitor_1']['eligible'] == True
        assert result['progenitor_2']['eligible'] == True
        assert "menor pensión" in result['explanation']
    
    def test_compare_progenitors_one_eligible(self):
        """Test comparación con solo un progenitor elegible."""
        progenitor_1 = {
            'name': 'María',
            'pension_type': PensionType.JUBILACION,
            'start_date': date(2021, 6, 15),
            'num_children': 2,
            'pension_amount': 1000.0
        }
        
        progenitor_2 = {
            'name': 'José',
            'pension_type': PensionType.VIUDEDAD,  # No válido en período 2
            'start_date': date(2021, 6, 15),
            'num_children': 2,
            'pension_amount': 1200.0
        }
        
        result = self.service.compare_progenitors(progenitor_1, progenitor_2)
        
        assert result['eligible_progenitor'] == 'María'
        assert result['progenitor_1']['eligible'] == True
        assert result['progenitor_2']['eligible'] == False
        assert "Solo María cumple" in result['explanation']