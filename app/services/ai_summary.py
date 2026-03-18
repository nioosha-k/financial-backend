"""AI summary generation service using OpenAI."""

import os
from typing import Optional

from openai import OpenAI

from app.constants import AI_SUMMARY_SYSTEM_PROMPT, AI_SUMMARY_USER_PROMPT
from app.models import RiskFlag, ReadinessBand


async def generate_ai_summary(
    total_inflow: float,
    total_outflow: float,
    net_cash_flow: float,
    inflow_count: int,
    outflow_count: int,
    largest_inflow: Optional[float],
    largest_outflow: Optional[float],
    average_transaction_value: float,
    risk_flags: list[RiskFlag],
    readiness: ReadinessBand,
    readiness_reasoning: str,
) -> str:
    """Generate a human-readable AI summary of the financial analysis."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    client = OpenAI(api_key=api_key)

    risk_flags_section = ""
    if risk_flags:
        risk_flags_section = "\nRisk Flags Detected:\n"
        for flag in risk_flags:
            risk_flags_section += f"- {flag.flag} ({flag.severity} severity): {flag.description}\n"
    else:
        risk_flags_section = "\nNo risk flags detected."

    largest_inflow_str = f"${largest_inflow:,.2f}" if largest_inflow else "N/A"
    largest_outflow_str = f"${largest_outflow:,.2f}" if largest_outflow else "N/A"

    user_prompt = AI_SUMMARY_USER_PROMPT.format(
        total_inflow=total_inflow,
        total_outflow=total_outflow,
        net_cash_flow=net_cash_flow,
        inflow_count=inflow_count,
        outflow_count=outflow_count,
        largest_inflow=largest_inflow_str,
        largest_outflow=largest_outflow_str,
        average_transaction_value=average_transaction_value,
        readiness=readiness.value,
        readiness_reasoning=readiness_reasoning,
        risk_flags_section=risk_flags_section,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": AI_SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].message.content
