"""Analysis router for transaction endpoints."""

from datetime import datetime
from statistics import mean

from fastapi import APIRouter, HTTPException

from app.models import (
    Transaction,
    TransactionType,
    TransactionsPayload,
    RiskFlag,
    FinancialSummary,
)
from app.services import (
    detect_nsf_activity,
    detect_large_outflow,
    detect_negative_cash_flow,
    detect_high_expense_concentration,
    detect_low_inflow_frequency,
    calculate_readiness,
)

router = APIRouter()


@router.post("/analyze-file", response_model=FinancialSummary)
async def analyze_transactions(payload: TransactionsPayload) -> FinancialSummary:
    """
    Analyze a set of financial transactions and return a structured summary.

    Accepts a JSON payload with transactions and returns:
    - Cash flow totals and metrics
    - Risk flags based on transaction patterns
    - Readiness classification with reasoning
    """
    transactions = payload.transactions

    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions provided")

    inflows = [t for t in transactions if t.type == TransactionType.INFLOW]
    outflows = [t for t in transactions if t.type == TransactionType.OUTFLOW]

    total_inflow = sum(t.amount for t in inflows)
    total_outflow = sum(t.amount for t in outflows)
    net_cash_flow = total_inflow - total_outflow

    largest_inflow = max((t.amount for t in inflows), default=None)
    largest_outflow = max((t.amount for t in outflows), default=None)

    all_amounts = [t.amount for t in transactions]
    average_value = mean(all_amounts) if all_amounts else 0.0

    risk_flags: list[RiskFlag] = []

    nsf_flag = detect_nsf_activity(transactions)
    if nsf_flag:
        risk_flags.append(nsf_flag)

    large_outflow_flag = detect_large_outflow(transactions)
    if large_outflow_flag:
        risk_flags.append(large_outflow_flag)

    negative_flow_flag = detect_negative_cash_flow(total_inflow, total_outflow)
    if negative_flow_flag:
        risk_flags.append(negative_flow_flag)

    expense_flag = detect_high_expense_concentration(total_inflow, total_outflow)
    if expense_flag:
        risk_flags.append(expense_flag)

    inflow_freq_flag = detect_low_inflow_frequency(transactions)
    if inflow_freq_flag:
        risk_flags.append(inflow_freq_flag)

    readiness, readiness_reasoning = calculate_readiness(
        net_cash_flow, risk_flags, total_inflow, total_outflow
    )

    return FinancialSummary(
        total_inflow=round(total_inflow, 2),
        total_outflow=round(total_outflow, 2),
        net_cash_flow=round(net_cash_flow, 2),
        inflow_count=len(inflows),
        outflow_count=len(outflows),
        largest_inflow=round(largest_inflow, 2) if largest_inflow else None,
        largest_outflow=round(largest_outflow, 2) if largest_outflow else None,
        average_transaction_value=round(average_value, 2),
        risk_flags=risk_flags,
        readiness=readiness,
        readiness_reasoning=readiness_reasoning,
        analyzed_at=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "financial-analyzer"}
