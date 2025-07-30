"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import date
from app import create_app
from app.schemas import CalculationRequest, RetroactiveRequest, ComparisonRequest, ApplicantData, PensionType


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_calculation_request():
    """Sample calculation request for testing."""
    return CalculationRequest(
        pension_type=PensionType.JUBILACION,
        start_date=date(2020, 1, 1),
        num_children=3,
        pension_amount=1000.0
    )


@pytest.fixture
def sample_retroactive_request():
    """Sample retroactive request for testing."""
    return RetroactiveRequest(
        start_date=date(2020, 1, 1),
        end_date=date(2022, 12, 31),
        pension_amount=1000.0,
        num_children=3
    )


@pytest.fixture
def sample_comparison_request():
    """Sample comparison request for testing."""
    return ComparisonRequest(
        applicant_1=ApplicantData(
            pension_type=PensionType.JUBILACION,
            start_date=date(2020, 1, 1),
            pension_amount=1000.0,
            num_children=3,
            is_mother=True
        ),
        applicant_2=ApplicantData(
            pension_type=PensionType.JUBILACION,
            start_date=date(2022, 1, 1),
            pension_amount=1200.0,
            num_children=3,
            is_mother=False
        )
    )