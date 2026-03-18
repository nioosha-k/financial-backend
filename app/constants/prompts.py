"""Prompt templates for AI-generated content."""

AI_SUMMARY_SYSTEM_PROMPT = """You are a  financial advisor assistant. Your task is to explain financial analysis results in a clear, human-readable way that the finincial staff can understand. Be concise but thorough."""

AI_SUMMARY_USER_PROMPT = """Based on the following financial analysis, provide a friendly, easy-to-understand summary for the finiancial staff.

Financial Analysis Results:
- Total Income: ${total_inflow:,.2f}
- Total Expenses: ${total_outflow:,.2f}
- Net Cash Flow: ${net_cash_flow:,.2f}
- Number of income transactions: {inflow_count}
- Number of expense transactions: {outflow_count}
- Largest single income: {largest_inflow}
- Largest single expense: {largest_outflow}
- Average transaction amount: ${average_transaction_value:,.2f}
- Financial Readiness: {readiness}
- Readiness Assessment: {readiness_reasoning}
{risk_flags_section}

Please provide a 2-3 paragraph summary that:
1. Summarizes the overall financial picture in plain language
2. Explains any risk flags in a non-alarming but honest way
3. Offers a brief, actionable suggestion based on the readiness level

Keep the tone friendly and supportive, not judgmental."""
