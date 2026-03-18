"""
Financial Transaction Analysis API

A FastAPI service that analyzes financial transactions and returns
structured summaries with risk flags and readiness classification.
"""

from fastapi import FastAPI

from app.routers import analysis_router

app = FastAPI(
    title="Financial Transaction Analyzer",
    description="Analyzes financial transactions and provides risk assessment",
    version="1.0.0",
)

app.include_router(analysis_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
