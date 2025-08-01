"""
Lógica de negocio para el cálculo del Complemento de Paternidad.
"""

import logging
from datetime import date, datetime
from typing import Tuple, Optional
from .schemas import PensionType, PeriodType, EligibilityResponse, CalculationResponse
from .utils import date_to_period, calculate_months_between_dates

logger = logging.getLogger(__name__)

class ComplementoPaternidadService:
    """Servicio para calcular el Complemento de Paternidad."""
    
    # Constantes para los cálculos
    PERIOD_1_START = date(2016, 1, 1)
    PERIOD_1_END = date(2021, 2, 3)
    PERIOD_2_START = date(2021, 2, 4)
    
    # Porcentajes para el Período 1
    PERIOD_1_PERCENTAGES = {
        2: 5.0,   # 5%
        3: 10.0,  # 10%
        4: 15.0   # 15% para 4 o más hijos
    }
    
    # Importe fijo para el Período 2 (35,90€ por hijo desde febrero 2021)
    PERIOD_2_AMOUNT_PER_CHILD = 35.90
    
    def check_eligibility(
        self, 
        pension_type: PensionType, 
        start_date: date, 
        num_children: int
    ) -> EligibilityResponse:
        """
        Verificar si el solicitante cumple los criterios básicos de elegibilidad.
        
        Args:
            pension_type: Tipo de pensión
            start_date: Fecha de inicio de la pensión
            num_children: Número de hijos
            
        Returns:
            EligibilityResponse con el resultado de la elegibilidad
        """
        logger.info(f"Verificando elegibilidad: {pension_type}, {start_date}, {num_children} hijos")
        
        # Determinar el período
        period = date_to_period(start_date)
        
        if period == PeriodType.PERIOD_1:
            # Período 1: Jubilaciones (excepto anticipadas voluntarias), viudedad e incapacidad
            if pension_type not in [PensionType.JUBILACION, PensionType.VIUDEDAD, PensionType.INCAPACIDAD]:
                return EligibilityResponse(
                    eligible=False,
                    period=period,
                    reason=f"En el Período 1 solo aplica para jubilación (excepto anticipadas voluntarias), viudedad e incapacidad, no {pension_type}"
                )
            
            # Período 1 requiere mínimo 2 hijos
            if num_children < 2:
                return EligibilityResponse(
                    eligible=False,
                    period=period,
                    reason=f"Para el Período 1 se requieren al menos 2 hijos (tiene {num_children})"
                )
        
        elif period == PeriodType.PERIOD_2:
            # Período 2: Jubilaciones (ordinarias y anticipadas), incapacidad y viudedad
            if pension_type not in [PensionType.JUBILACION, PensionType.JUBILACION_ANTICIPADA, 
                                   PensionType.INCAPACIDAD, PensionType.VIUDEDAD]:
                return EligibilityResponse(
                    eligible=False,
                    period=period,
                    reason=f"En el Período 2 solo aplica para jubilación, incapacidad y viudedad, no {pension_type}"
                )
        
        else:
            return EligibilityResponse(
                eligible=False,
                reason="Fecha fuera del rango de aplicación del complemento"
            )
        
        # Verificar número mínimo de hijos
        if num_children < 1:
            return EligibilityResponse(
                eligible=False,
                period=period,
                reason="Debe tener al menos 1 hijo para optar al complemento"
            )
        
        logger.info(f"Elegibilidad aprobada para el período {period}")
        return EligibilityResponse(
            eligible=True,
            period=period
        )
    
    def calculate_complement(
        self,
        pension_type: PensionType,
        start_date: date,
        num_children: int,
        pension_amount: float
    ) -> CalculationResponse:
        """
        Calcular el complemento de paternidad.
        
        Args:
            pension_type: Tipo de pensión
            start_date: Fecha de inicio
            num_children: Número de hijos
            pension_amount: Cuantía de la pensión
            
        Returns:
            CalculationResponse con el cálculo del complemento
        """
        logger.info(f"Calculando complemento: {pension_type}, {start_date}, {num_children} hijos, {pension_amount}€")
        
        # Verificar elegibilidad primero
        eligibility = self.check_eligibility(pension_type, start_date, num_children)
        
        if not eligibility.eligible:
            raise ValueError(f"No cumple los criterios de elegibilidad: {eligibility.reason}")
        
        period = eligibility.period
        
        if period == PeriodType.PERIOD_1:
            return self._calculate_period_1(num_children, pension_amount)
        else:
            return self._calculate_period_2(num_children, pension_amount)
    
    def _calculate_period_1(self, num_children: int, pension_amount: float) -> CalculationResponse:
        """Calcular complemento para el Período 1 (porcentajes)."""
        
        # Determinar el porcentaje según número de hijos
        if num_children >= 4:
            percentage = self.PERIOD_1_PERCENTAGES[4]
        else:
            percentage = self.PERIOD_1_PERCENTAGES.get(num_children, 0.0)
        
        if percentage == 0.0:
            raise ValueError(f"Para el Período 1, se requieren al menos 2 hijos (tiene {num_children})")
        
        complement_amount = pension_amount * (percentage / 100)
        
        logger.info(f"Período 1: {percentage}% de {pension_amount}€ = {complement_amount}€")
        
        return CalculationResponse(
            period=PeriodType.PERIOD_1,
            complement_percent=percentage,
            complement_fixed=None,
            amount=complement_amount,
            pension_with_complement=pension_amount + complement_amount
        )
    
    def _calculate_period_2(self, num_children: int, pension_amount: float) -> CalculationResponse:
        """Calcular complemento para el Período 2 (importe fijo)."""
        
        # Máximo 4 hijos para el cálculo
        children_for_calculation = min(num_children, 4)
        complement_amount = self.PERIOD_2_AMOUNT_PER_CHILD * children_for_calculation
        
        logger.info(f"Período 2: {children_for_calculation} hijos x {self.PERIOD_2_AMOUNT_PER_CHILD}€ = {complement_amount}€")
        
        return CalculationResponse(
            period=PeriodType.PERIOD_2,
            complement_percent=None,
            complement_fixed=self.PERIOD_2_AMOUNT_PER_CHILD,
            amount=complement_amount,
            pension_with_complement=pension_amount + complement_amount
        )
    
    def calculate_retroactive(
        self,
        start_date: date,
        end_date: date,
        pension_amount: float,
        num_children: int
    ) -> dict:
        """
        Calcular atrasos acumulados entre dos fechas.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            pension_amount: Cuantía de la pensión
            num_children: Número de hijos
            
        Returns:
            Dict con el cálculo de atrasos
        """
        logger.info(f"Calculando atrasos del {start_date} al {end_date}")
        
        total_amount = 0.0
        period_1_amount = 0.0
        period_2_amount = 0.0
        total_months = 0
        
        current_date = start_date
        
        while current_date < end_date:
            # Determinar qué período aplica para esta fecha
            period = date_to_period(current_date)
            
            try:
                if period == PeriodType.PERIOD_1:
                    # Calcular solo si es pensión de jubilación y tiene al menos 2 hijos
                    if num_children >= 2:
                        calc = self._calculate_period_1(num_children, pension_amount)
                        monthly_amount = calc.amount
                        period_1_amount += monthly_amount
                        total_amount += monthly_amount
                        total_months += 1
                
                elif period == PeriodType.PERIOD_2:
                    calc = self._calculate_period_2(num_children, pension_amount)
                    monthly_amount = calc.amount
                    period_2_amount += monthly_amount
                    total_amount += monthly_amount
                    total_months += 1
                    
            except ValueError:
                # No aplica para esta fecha/condiciones
                pass
            
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        logger.info(f"Atrasos calculados: {total_amount}€ en {total_months} meses")
        
        return {
            "total_amount": round(total_amount, 2),
            "months_calculated": total_months,
            "period_1_amount": round(period_1_amount, 2) if period_1_amount > 0 else None,
            "period_2_amount": round(period_2_amount, 2) if period_2_amount > 0 else None
        }
    
    def compare_progenitors(
        self,
        progenitor_1_data: dict,
        progenitor_2_data: dict
    ) -> dict:
        """
        Comparar dos progenitores para determinar quién tiene derecho al complemento.
        
        Args:
            progenitor_1_data: Datos del primer progenitor
            progenitor_2_data: Datos del segundo progenitor
            
        Returns:
            Dict con el resultado de la comparación
        """
        logger.info("Comparando dos progenitores para determinar derecho al complemento")
        
        results = []
        
        for i, data in enumerate([progenitor_1_data, progenitor_2_data], 1):
            try:
                calculation = self.calculate_complement(
                    data['pension_type'],
                    data['start_date'], 
                    data['num_children'],
                    data['pension_amount']
                )
                
                results.append({
                    'name': data['name'],
                    'eligible': True,
                    'complement_amount': calculation.amount,
                    'total_pension': calculation.pension_with_complement
                })
                
            except ValueError as e:
                results.append({
                    'name': data['name'],
                    'eligible': False,
                    'complement_amount': None,
                    'total_pension': None,
                    'reason': str(e)
                })
        
        # Determinar quién tiene derecho
        eligible_results = [r for r in results if r['eligible']]
        
        if len(eligible_results) == 0:
            eligible_progenitor = "Ninguno"
            explanation = "Ninguno de los progenitores cumple los criterios"
        elif len(eligible_results) == 1:
            eligible_progenitor = eligible_results[0]['name']
            explanation = f"Solo {eligible_progenitor} cumple los criterios de elegibilidad"
        else:
            # Ambos son elegibles, se otorga al de menor pensión
            min_pension = min(eligible_results, key=lambda x: x['total_pension'])
            eligible_progenitor = min_pension['name']
            explanation = f"Ambos son elegibles, se otorga a {eligible_progenitor} por tener menor pensión"
        
        logger.info(f"Resultado comparación: {eligible_progenitor} tiene derecho")
        
        return {
            'eligible_progenitor': eligible_progenitor,
            'progenitor_1': results[0],
            'progenitor_2': results[1],
            'explanation': explanation
        }