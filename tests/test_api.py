"""
Tests for the Financial Transaction Analyzer API.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import ReadinessBand


client = TestClient(app)


class TestHealthCheck:
    """Tests for the health endpoint."""

    def test_health_returns_healthy(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAnalyzeTransactions:
    """Tests for the /analyze-file endpoint."""

    def test_basic_analysis(self):
        """Test basic transaction analysis with mixed inflows/outflows."""
        payload = {
            "transactions": [
                {"amount": 5000, "type": "inflow", "description": "Salary"},
                {"amount": 1500, "type": "outflow", "description": "Rent"},
                {"amount": 200, "type": "outflow", "description": "Utilities"},
                {"amount": 300, "type": "outflow", "description": "Groceries"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["total_inflow"] == 5000.0
        assert data["total_outflow"] == 2000.0
        assert data["net_cash_flow"] == 3000.0
        assert data["inflow_count"] == 1
        assert data["outflow_count"] == 3
        assert data["largest_inflow"] == 5000.0
        assert data["largest_outflow"] == 1500.0

    def test_empty_transactions_rejected(self):
        """Test that empty transaction list returns 422."""
        payload = {"transactions": []}
        response = client.post("/analyze-file", json=payload)
        assert response.status_code == 422

    def test_missing_transactions_rejected(self):
        """Test that missing transactions field returns 422."""
        payload = {}
        response = client.post("/analyze-file", json=payload)
        assert response.status_code == 422

    def test_average_calculation(self):
        """Test average transaction value calculation."""
        payload = {
            "transactions": [
                {"amount": 100, "type": "inflow"},
                {"amount": 200, "type": "outflow"},
                {"amount": 300, "type": "inflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["average_transaction_value"] == 200.0


class TestRiskFlags:
    """Tests for risk flag detection."""

    def test_nsf_detection(self):
        """Test NSF activity detection."""
        payload = {
            "transactions": [
                {"amount": 1000, "type": "inflow", "description": "Deposit"},
                {"amount": 50, "type": "outflow", "description": "NSF fee"},
                {"amount": 100, "type": "outflow", "description": "Purchase"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        flag_names = [f["flag"] for f in data["risk_flags"]]
        assert "NSF_ACTIVITY_DETECTED" in flag_names

    def test_nsf_detection_insufficient_keyword(self):
        """Test NSF detection with 'insufficient' keyword."""
        payload = {
            "transactions": [
                {"amount": 1000, "type": "inflow"},
                {"amount": 35, "type": "outflow", "description": "Insufficient funds charge"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        flag_names = [f["flag"] for f in data["risk_flags"]]
        assert "NSF_ACTIVITY_DETECTED" in flag_names

    def test_large_outflow_detection(self):
        """Test large single outflow detection."""
        payload = {
            "transactions": [
                {"amount": 50000, "type": "inflow", "description": "Investment"},
                {"amount": 15000, "type": "outflow", "description": "Large purchase"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        flag_names = [f["flag"] for f in data["risk_flags"]]
        assert "LARGE_SINGLE_OUTFLOW" in flag_names

    def test_negative_cash_flow_detection(self):
        """Test negative net cash flow detection."""
        payload = {
            "transactions": [
                {"amount": 1000, "type": "inflow"},
                {"amount": 1500, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        flag_names = [f["flag"] for f in data["risk_flags"]]
        assert "NEGATIVE_NET_CASH_FLOW" in flag_names

    def test_high_expense_concentration(self):
        """Test high expense concentration detection."""
        payload = {
            "transactions": [
                {"amount": 1000, "type": "inflow"},
                {"amount": 900, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        flag_names = [f["flag"] for f in data["risk_flags"]]
        assert "HIGH_EXPENSE_CONCENTRATION" in flag_names

    def test_low_inflow_frequency(self):
        """Test low inflow frequency detection."""
        payload = {
            "transactions": [
                {"amount": 5000, "type": "inflow"},
                {"amount": 100, "type": "outflow"},
                {"amount": 200, "type": "outflow"},
                {"amount": 150, "type": "outflow"},
                {"amount": 300, "type": "outflow"},
                {"amount": 250, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        flag_names = [f["flag"] for f in data["risk_flags"]]
        assert "LOW_INFLOW_FREQUENCY" in flag_names

    def test_no_flags_for_healthy_transactions(self):
        """Test that healthy transactions generate no flags."""
        payload = {
            "transactions": [
                {"amount": 5000, "type": "inflow", "description": "Salary"},
                {"amount": 2000, "type": "inflow", "description": "Freelance"},
                {"amount": 1500, "type": "outflow", "description": "Rent"},
                {"amount": 500, "type": "outflow", "description": "Utilities"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert len(data["risk_flags"]) == 0


class TestReadinessClassification:
    """Tests for readiness band classification."""

    def test_strong_readiness(self):
        """Test strong readiness classification."""
        payload = {
            "transactions": [
                {"amount": 10000, "type": "inflow"},
                {"amount": 5000, "type": "inflow"},
                {"amount": 3000, "type": "outflow"},
                {"amount": 2000, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["readiness"] == "strong"

    def test_structured_readiness(self):
        """Test structured readiness classification."""
        payload = {
            "transactions": [
                {"amount": 5000, "type": "inflow"},
                {"amount": 2500, "type": "inflow"},
                {"amount": 4000, "type": "outflow"},
                {"amount": 2500, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["readiness"] == "structured"

    def test_requires_clarification_negative_flow(self):
        """Test requires_clarification for negative cash flow."""
        payload = {
            "transactions": [
                {"amount": 2000, "type": "inflow"},
                {"amount": 3000, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["readiness"] == "requires_clarification"

    def test_requires_clarification_nsf(self):
        """Test requires_clarification for NSF activity."""
        payload = {
            "transactions": [
                {"amount": 5000, "type": "inflow"},
                {"amount": 1000, "type": "outflow"},
                {"amount": 35, "type": "outflow", "description": "NSF fee"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["readiness"] == "requires_clarification"

    def test_readiness_reasoning_provided(self):
        """Test that readiness reasoning is always provided."""
        payload = {
            "transactions": [
                {"amount": 1000, "type": "inflow"},
                {"amount": 500, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert "readiness_reasoning" in data
        assert len(data["readiness_reasoning"]) > 0


class TestEdgeCases:
    """Tests for edge cases."""

    def test_all_inflows(self):
        """Test handling of only inflows."""
        payload = {
            "transactions": [
                {"amount": 1000, "type": "inflow"},
                {"amount": 2000, "type": "inflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["total_inflow"] == 3000.0
        assert data["total_outflow"] == 0.0
        assert data["largest_outflow"] is None
        assert data["readiness"] == "strong"

    def test_all_outflows(self):
        """Test handling of only outflows."""
        payload = {
            "transactions": [
                {"amount": 500, "type": "outflow"},
                {"amount": 300, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["total_inflow"] == 0.0
        assert data["total_outflow"] == 800.0
        assert data["largest_inflow"] is None
        assert data["readiness"] == "requires_clarification"

    def test_single_transaction(self):
        """Test handling of single transaction."""
        payload = {"transactions": [{"amount": 1000, "type": "inflow"}]}

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["inflow_count"] == 1
        assert data["outflow_count"] == 0
        assert data["average_transaction_value"] == 1000.0

    def test_decimal_amounts(self):
        """Test handling of decimal amounts."""
        payload = {
            "transactions": [
                {"amount": 1234.56, "type": "inflow"},
                {"amount": 789.12, "type": "outflow"},
            ]
        }

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert data["total_inflow"] == 1234.56
        assert data["total_outflow"] == 789.12
        assert data["net_cash_flow"] == 445.44

    def test_analyzed_at_timestamp(self):
        """Test that analyzed_at timestamp is provided."""
        payload = {"transactions": [{"amount": 100, "type": "inflow"}]}

        response = client.post("/analyze-file", json=payload)
        data = response.json()

        assert "analyzed_at" in data
        assert data["analyzed_at"].endswith("Z")
