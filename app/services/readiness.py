"""Readiness calculation service."""

from app.models import RiskFlag, ReadinessBand


def calculate_readiness(
    net_cash_flow: float,
    risk_flags: list[RiskFlag],
    total_inflow: float,
    total_outflow: float,
) -> tuple[ReadinessBand, str]:
    """
    Determine readiness band based on financial health indicators.

    Logic:
    - STRONG: Positive cash flow, no high-severity flags, healthy expense ratio
    - STRUCTURED: Some concerns but manageable (medium flags or tight margins)
    - REQUIRES_CLARIFICATION: High-severity flags or concerning patterns
    """
    high_severity_count = sum(1 for f in risk_flags if f.severity == "high")
    medium_severity_count = sum(1 for f in risk_flags if f.severity == "medium")

    expense_ratio = total_outflow / total_inflow if total_inflow > 0 else float("inf")

    if high_severity_count > 0:
        return (
            ReadinessBand.REQUIRES_CLARIFICATION,
            f"High-severity risk flags detected ({high_severity_count}). "
            "Manual review recommended to understand cash flow challenges.",
        )

    if expense_ratio > 1.0:
        return (
            ReadinessBand.REQUIRES_CLARIFICATION,
            "Expenses exceed income. Additional context needed to assess financial viability.",
        )

    if net_cash_flow > 0 and expense_ratio < 0.7 and medium_severity_count == 0:
        return (
            ReadinessBand.STRONG,
            "Healthy positive cash flow with comfortable expense margins. "
            "Financial position appears stable.",
        )

    return (
        ReadinessBand.STRUCTURED,
        "Cash flow is positive but with limited margins or minor concerns. "
        "Position is manageable but warrants monitoring.",
    )
