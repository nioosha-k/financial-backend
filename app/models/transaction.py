"""Transaction-related Pydantic models."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"


class Transaction(BaseModel):
    """A single financial transaction."""

    id: Optional[str] = None
    amount: float = Field(..., description="Transaction amount (positive value)")
    type: TransactionType = Field(..., description="Either 'inflow' or 'outflow'")
    description: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None


class TransactionsPayload(BaseModel):
    """Payload containing list of transactions to analyze."""

    transactions: list[Transaction] = Field(..., min_length=1)
