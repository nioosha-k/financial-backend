# Financial Transaction Analyzer API

A FastAPI backend service that analyzes financial transactions and returns structured summaries with risk assessment and readiness classification.

## Features

- **Transaction Analysis**: Calculate inflows, outflows, net cash flow, and averages
- **Risk Detection**: Automated flagging of concerning financial patterns
- **Readiness Classification**: Assess overall financial health with reasoning

## Project Structure

```
challenge/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── constants/
│   │   ├── __init__.py
│   │   └── thresholds.py          # Configuration constants
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transaction.py         # Transaction Pydantic models
│   │   └── response.py            # Response Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── risk_detection.py      # Risk flag detection logic
│   │   └── readiness.py           # Readiness calculation logic
│   └── routers/
│       ├── __init__.py
│       └── analysis.py            # API route handlers
├── tests/
│   ├── __init__.py
│   └── test_api.py                # Test suite
├── requirements.txt
└── README.md
```

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /analyze-file

Analyzes a set of financial transactions.

**Request Body:**

```json
{
  "transactions": [
    {
      "amount": 5000,
      "type": "inflow",
      "description": "Monthly salary",
      "date": "2024-01-15",
      "category": "income"
    },
    {
      "amount": 1500,
      "type": "outflow",
      "description": "Rent payment",
      "date": "2024-01-01",
      "category": "housing"
    }
  ]
}
```

**Response:**

```json
{
  "total_inflow": 5000.0,
  "total_outflow": 1500.0,
  "net_cash_flow": 3500.0,
  "inflow_count": 1,
  "outflow_count": 1,
  "largest_inflow": 5000.0,
  "largest_outflow": 1500.0,
  "average_transaction_value": 3250.0,
  "risk_flags": [],
  "readiness": "strong",
  "readiness_reasoning": "Healthy positive cash flow with comfortable expense margins. Financial position appears stable.",
  "analyzed_at": "2024-01-20T12:00:00.000000Z"
}
```

### GET /health

Health check endpoint returning service status.

## Risk Flags

The service implements five risk detection rules:

| Flag | Severity | Trigger Condition |
|------|----------|-------------------|
| `NSF_ACTIVITY_DETECTED` | High | Transaction descriptions contain NSF-related keywords (nsf, insufficient, returned, bounced, overdraft) |
| `LARGE_SINGLE_OUTFLOW` | Medium | Any single outflow ≥ $10,000 |
| `NEGATIVE_NET_CASH_FLOW` | High | Total outflows exceed total inflows |
| `HIGH_EXPENSE_CONCENTRATION` | Medium | Outflow/Inflow ratio ≥ 80% |
| `LOW_INFLOW_FREQUENCY` | Low | Inflows represent ≤ 20% of total transactions |

## Readiness Classification Logic

The service classifies financial readiness into three bands:

### `strong`

**Criteria:**
- Positive net cash flow
- Expense ratio below 70%
- No medium or high severity risk flags

**Interpretation:** The financial position shows healthy margins with income comfortably exceeding expenses. No concerning patterns detected.

### `structured`

**Criteria:**
- Positive net cash flow (or expense ratio ≤ 100%)
- May have medium severity flags
- No high severity flags

**Interpretation:** The financial position is manageable but has limited margins or minor areas of concern. Cash flow is positive but warrants monitoring.

### `requires_clarification`

**Criteria (any of the following):**
- Any high severity risk flags present (NSF activity, negative cash flow)
- Expense ratio exceeds 100% (spending more than earning)

**Interpretation:** Significant concerns identified that require manual review. High-severity flags indicate potential financial stress or cash flow management issues.

### Classification Priority

1. **High severity flags** → Always `requires_clarification`
2. **Expense ratio > 100%** → Always `requires_clarification`
3. **Healthy margins + no flags** → `strong`
4. **Everything else** → `structured`

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

## Configuration

Risk detection thresholds are defined in `app/constants/thresholds.py`:

```python
LARGE_OUTFLOW_THRESHOLD = 10000.0      # Outflows above this trigger a flag
HIGH_EXPENSE_RATIO_THRESHOLD = 0.8     # 80% expense ratio triggers flag
LOW_INFLOW_FREQUENCY_THRESHOLD = 0.2   # <20% inflows triggers flag
NSF_KEYWORDS = ["nsf", "insufficient", "returned", "bounced", "overdraft"]
```

Modify these values to adjust sensitivity for your use case.

## Example Scenarios

### Healthy Finances
```json
{
  "transactions": [
    {"amount": 8000, "type": "inflow", "description": "Salary"},
    {"amount": 3000, "type": "inflow", "description": "Freelance"},
    {"amount": 2000, "type": "outflow", "description": "Rent"},
    {"amount": 1000, "type": "outflow", "description": "Expenses"}
  ]
}
```
→ **Result:** `strong` (27% expense ratio, +$8000 net flow)

### Tight Margins
```json
{
  "transactions": [
    {"amount": 5000, "type": "inflow", "description": "Salary"},
    {"amount": 4500, "type": "outflow", "description": "Bills"}
  ]
}
```
→ **Result:** `structured` with `HIGH_EXPENSE_CONCENTRATION` flag (90% expense ratio)

### Financial Stress
```json
{
  "transactions": [
    {"amount": 3000, "type": "inflow", "description": "Income"},
    {"amount": 4000, "type": "outflow", "description": "Expenses"},
    {"amount": 35, "type": "outflow", "description": "NSF fee"}
  ]
}
```
→ **Result:** `requires_clarification` with `NEGATIVE_NET_CASH_FLOW` and `NSF_ACTIVITY_DETECTED` flags
