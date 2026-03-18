"""Risk detection service functions."""

from typing import Optional

from app.constants import (
    LARGE_OUTFLOW_THRESHOLD,
    HIGH_EXPENSE_RATIO_THRESHOLD,
    LOW_INFLOW_FREQUENCY_THRESHOLD,
    NSF_KEYWORDS,
)
from app.models import Transaction, TransactionType, RiskFlag


def detect_nsf_activity(transactions: list[Transaction]) -> Optional[RiskFlag]:
    """Detect NSF (Non-Sufficient Funds) related transactions."""
    for txn in transactions:
        if txn.description:
            desc_lower = txn.description.lower()
            if any(keyword in desc_lower for keyword in NSF_KEYWORDS):
                return RiskFlag(
                    flag="NSF_ACTIVITY_DETECTED",
                    severity="high",
                    description="NSF or insufficient funds related activity detected in transactions. "
                    "This may indicate cash flow management issues.",
                )
    return None


def detect_large_outflow(transactions: list[Transaction]) -> Optional[RiskFlag]:
    """Detect unusually large single outflows."""
    outflows = [t.amount for t in transactions if t.type == TransactionType.OUTFLOW]
    if outflows:
        max_outflow = max(outflows)
        if max_outflow >= LARGE_OUTFLOW_THRESHOLD:
            return RiskFlag(
                flag="LARGE_SINGLE_OUTFLOW",
                severity="medium",
                description=f"Large single outflow of ${max_outflow:,.2f} detected. "
                f"Outflows above ${LARGE_OUTFLOW_THRESHOLD:,.2f} warrant review.",
            )
    return None


def detect_negative_cash_flow(
    total_inflow: float, total_outflow: float
) -> Optional[RiskFlag]:
    """Detect negative net cash flow."""
    net = total_inflow - total_outflow
    if net < 0:
        return RiskFlag(
            flag="NEGATIVE_NET_CASH_FLOW",
            severity="high",
            description=f"Negative net cash flow of ${net:,.2f}. "
            "Expenses exceed income, indicating potential financial stress.",
        )
    return None


def detect_high_expense_concentration(
    total_inflow: float, total_outflow: float
) -> Optional[RiskFlag]:
    """Detect when outflows represent a very high proportion of inflows."""
    if total_inflow > 0:
        ratio = total_outflow / total_inflow
        if ratio >= HIGH_EXPENSE_RATIO_THRESHOLD:
            return RiskFlag(
                flag="HIGH_EXPENSE_CONCENTRATION",
                severity="medium",
                description=f"Expense ratio of {ratio:.1%} indicates high spending relative to income. "
                "Limited buffer for unexpected expenses.",
            )
    return None


def detect_low_inflow_frequency(
    transactions: list[Transaction],
) -> Optional[RiskFlag]:
    """Detect when inflows are infrequent relative to total transactions."""
    if not transactions:
        return None

    inflow_count = sum(1 for t in transactions if t.type == TransactionType.INFLOW)
    inflow_ratio = inflow_count / len(transactions)

    if inflow_ratio <= LOW_INFLOW_FREQUENCY_THRESHOLD:
        return RiskFlag(
            flag="LOW_INFLOW_FREQUENCY",
            severity="low",
            description=f"Only {inflow_ratio:.1%} of transactions are inflows. "
            "This may indicate irregular income patterns.",
        )
    return None
