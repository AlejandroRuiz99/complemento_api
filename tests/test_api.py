"""
Tests de integración para la API REST.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date
import json

# Importar la aplicación
from app import app

@pytest.fixture
def client():
    """Cliente de prueba para la API."""
    return TestClient(app)

class TestAPIEndpoints:
    """Tests de integración para los endpoints de la API."""
    
    def test_health_endpoint(self, client):
        """Test endpoint de salud."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_eligibility_endpoint_valid_period_1(self, client):
        """Test endpoint de elegibilidad válida período 1."""
        response = client.get(
            "/eligibility",
            params={
                "pension_type": "jubilacion",
                "start_date": "2020-06-15",
                "num_children": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] == True
        assert data["period"] == "1"
        assert data["reason"] is None
    
    def test_eligibility_endpoint_invalid_period_1(self, client):
        """Test endpoint de elegibilidad inválida período 1."""
        response = client.get(
            "/eligibility",
            params={
                "pension_type": "incapacidad",
                "start_date": "2020-06-15",
                "num_children": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] == False
        assert data["period"] == "1"
        assert "Período 1 solo aplica para pensiones de jubilación" in data["reason"]
    
    def test_eligibility_endpoint_valid_period_2(self, client):
        """Test endpoint de elegibilidad válida período 2."""
        response = client.get(
            "/eligibility",
            params={
                "pension_type": "jubilacion",
                "start_date": "2021-06-15",
                "num_children": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] == True
        assert data["period"] == "2"
    
    def test_eligibility_endpoint_invalid_params(self, client):
        """Test endpoint de elegibilidad con parámetros inválidos."""
        response = client.get(
            "/eligibility",
            params={
                "pension_type": "invalidtype",
                "start_date": "2021-06-15",
                "num_children": 1
            }
        )
        
        assert response.status_code == 400
    
    def test_calculate_endpoint_period_1(self, client):
        """Test endpoint de cálculo período 1."""
        payload = {
            "pension_type": "jubilacion",
            "start_date": "2020-06-15",
            "num_children": 2,
            "pension_amount": 1000.0
        }
        
        response = client.post("/calculate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "1"
        assert data["complement_percent"] == 2.0
        assert data["complement_fixed"] is None
        assert data["amount"] == 20.0
        assert data["pension_with_complement"] == 1020.0
    
    def test_calculate_endpoint_period_2(self, client):
        """Test endpoint de cálculo período 2."""
        payload = {
            "pension_type": "jubilacion",
            "start_date": "2021-06-15",
            "num_children": 2,
            "pension_amount": 1000.0
        }
        
        response = client.post("/calculate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "2"
        assert data["complement_percent"] is None
        assert data["complement_fixed"] == 35.0
        assert data["amount"] == 70.0
        assert data["pension_with_complement"] == 1070.0
    
    def test_calculate_endpoint_invalid_eligibility(self, client):
        """Test endpoint de cálculo con elegibilidad inválida."""
        payload = {
            "pension_type": "incapacidad",
            "start_date": "2020-06-15",
            "num_children": 2,
            "pension_amount": 1000.0
        }
        
        response = client.post("/calculate", json=payload)
        
        assert response.status_code == 400
        assert "elegibilidad" in response.json()["detail"]
    
    def test_retroactive_endpoint(self, client):
        """Test endpoint de cálculo retroactivo."""
        response = client.get(
            "/retroactive",
            params={
                "start_date": "2021-05-01",
                "end_date": "2021-08-01",
                "pension_amount": 1000.0,
                "num_children": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] > 0
        assert data["months_calculated"] == 3
        assert data["period_2_amount"] > 0
        assert data["period_1_amount"] is None
    
    def test_retroactive_endpoint_invalid_dates(self, client):
        """Test endpoint retroactivo con fechas inválidas."""
        response = client.get(
            "/retroactive",
            params={
                "start_date": "2021-08-01",  # Fecha posterior a end_date
                "end_date": "2021-05-01",
                "pension_amount": 1000.0,
                "num_children": 2
            }
        )
        
        assert response.status_code == 400
    
    def test_compare_endpoint(self, client):
        """Test endpoint de comparación."""
        payload = {
            "progenitor_1": {
                "name": "María",
                "pension_amount": 1000.0,
                "num_children": 2,
                "start_date": "2021-06-15",
                "pension_type": "jubilacion"
            },
            "progenitor_2": {
                "name": "José",
                "pension_amount": 1200.0,
                "num_children": 2,
                "start_date": "2021-06-15",
                "pension_type": "jubilacion"
            }
        }
        
        response = client.post("/compare", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible_progenitor"] == "María"  # menor pensión
        assert data["progenitor_1"]["eligible"] == True
        assert data["progenitor_2"]["eligible"] == True
        assert "menor pensión" in data["explanation"]
    
    def test_compare_endpoint_one_eligible(self, client):
        """Test endpoint de comparación con uno elegible."""
        payload = {
            "progenitor_1": {
                "name": "María",
                "pension_amount": 1000.0,
                "num_children": 2,
                "start_date": "2021-06-15",
                "pension_type": "jubilacion"
            },
            "progenitor_2": {
                "name": "José",
                "pension_amount": 1200.0,
                "num_children": 2,
                "start_date": "2021-06-15",
                "pension_type": "viudedad"  # No válido en período 2
            }
        }
        
        response = client.post("/compare", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["eligible_progenitor"] == "María"
        assert data["progenitor_1"]["eligible"] == True
        assert data["progenitor_2"]["eligible"] == False
    
    def test_spec_endpoint(self, client):
        """Test endpoint de especificación OpenAPI."""
        response = client.get("/spec")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Complemento de Paternidad API"
    
    def test_openapi_docs_endpoint(self, client):
        """Test endpoint de documentación automática."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_endpoint(self, client):
        """Test endpoint de ReDoc."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")