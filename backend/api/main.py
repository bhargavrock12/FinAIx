from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import numpy as np

# Import strategy engine
from Quantum_Trading.scripts.strategy_engine import generate_signals_json

app = FastAPI(title="Smart FinTech AI - Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Quantum_Trading/data/processed"))

@app.get("/")
def root():
    return {"message": "Backend is running 🔥"}

@app.get("/historical/{ticker}")
def get_historical(ticker: str):
    ticker = ticker.upper()

    try:
        files = os.listdir(DATA_DIR)
    except:
        return {"error": "DATA_DIR missing"}

    match = next((f for f in files if f.startswith(ticker) and f.endswith("_processed.csv")), None)

    if not match:
        return {"error": f"No processed file found for {ticker}"}

    filepath = os.path.join(DATA_DIR, match)
    df = pd.read_csv(filepath)

    df = df.replace([np.nan, np.inf, -np.inf], None)

    return {
        "ticker": ticker,
        "rows": len(df),
        "columns": df.columns.tolist(),
        "data": df.to_dict(orient="records")
    }

@app.get("/score/{ticker}")
def get_score(ticker: str):
    return {
        "ticker": ticker.upper(),
        "score": 75,
        "breakdown": {
            "momentum": 80,
            "volatility": 60,
            "sentiment": 70,
            "model_confidence": 90
        },
        "risk_tag": "medium"
    }

@app.get("/portfolio")
def get_portfolio():
    return {
        "portfolio_value": 100000,
        "cash": 5000,
        "positions": [
            {"ticker": "AAPL", "qty": 5, "price": 230},
            {"ticker": "MSFT", "qty": 2, "price": 410}
        ]
    }

@app.get("/signals/{ticker}")
def get_signals(ticker: str):
    ticker = ticker.upper()

    match = next(
        (f for f in os.listdir(DATA_DIR) if f.startswith(ticker) and f.endswith("_processed.csv")),
        None
    )

    if not match:
        return {"error": f"No processed data found for {ticker}"}

    filepath = os.path.join(DATA_DIR, match)

    signals = generate_signals_json(filepath)

    return {
        "ticker": ticker,
        "count": len(signals),
        "signals": signals
    }
