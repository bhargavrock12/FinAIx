import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class TradingStrategy:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.results = {}
        
    def load_data(self, filepath):
        """Load processed stock data"""
        self.df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return self.df
    
    def simple_momentum_strategy(self, df):
        """RSI + SMA momentum strategy"""
        signals = []
        position = 0  
        cash = self.initial_capital
        shares = 0
        portfolio_value = []
        
        for i in range(1, len(df)):
            current_price = df['Close'].iloc[i]
            rsi = df['RSI_14'].iloc[i]
            sma = df['SMA_10'].iloc[i]
            prev_sma = df['SMA_10'].iloc[i-1]
            
            buy_signal = (rsi < 40) or (sma > prev_sma)
            sell_signal = (rsi > 70) or (sma < prev_sma)
            
            if position == 0 and buy_signal:
                shares = cash / current_price
                cash = 0
                position = 1
                signals.append(("BUY", df.index[i], float(current_price)))
            
            elif position == 1 and sell_signal:
                cash = shares * current_price
                shares = 0
                position = 0
                signals.append(("SELL", df.index[i], float(current_price)))
            
            portfolio_value.append(cash + shares * current_price)
        
        return signals, portfolio_value
    
    def backtest_strategy(self, filepath, strategy_name='momentum'):
        df = self.load_data(filepath)
        
        if strategy_name == "momentum":
            signals, portfolio_values = self.simple_momentum_strategy(df)
        
        final_value = portfolio_values[-1] if portfolio_values else self.initial_capital
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        buy_hold_return = (
            (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
        )
        
        self.results = {
            "signals": signals,
            "portfolio_values": portfolio_values,
            "final_value": final_value,
            "total_return": total_return,
            "buy_hold_return": buy_hold_return,
        }
        
        return self.results

def generate_signals_json(filepath):
    strategy = TradingStrategy(initial_capital=10000)
    results = strategy.backtest_strategy(filepath)
    
    # Convert signals to JSON-safe list
    json_signals = []
    for sig, date, price in results["signals"]:
        json_signals.append({
            "signal": sig,
            "date": str(date),
            "price": float(price)
        })
    return json_signals
