"""Response-related Pydantic models."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RiskFlag(BaseModel):
    """A risk flag with description and severity."""

    flag: str
    severity: str  # "low", "medium", "high"
    description: str


class ReadinessBand(str, Enum):
    STRONG = "strong"
    STRUCTURED = "structured"
    REQUIRES_CLARIFICATION = "requires_clarification"


class FinancialSummary(BaseModel):
    """Complete financial analysis response."""

    total_inflow: float
    total_outflow: float
    net_cash_flow: float
    inflow_count: int
    outflow_count: int
    largest_inflow: Optional[float]
    largest_outflow: Optional[float]
    average_transaction_value: float
    risk_flags: list[RiskFlag]
    readiness: ReadinessBand
    readiness_reasoning: str
    analyzed_at: str
