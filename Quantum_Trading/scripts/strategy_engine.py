# scripts/strategy_engine.py

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
        print(f"✅ Loaded data: {self.df.shape}")
        return self.df
    
    def simple_momentum_strategy(self, df):
        """Improved RSI + Moving Average strategy"""
        signals = []
        position = 0  # 0: out, 1: long
        cash = self.initial_capital
        shares = 0
        portfolio_value = []
        
        for i in range(1, len(df)):
            current_price = df['Close'].iloc[i]
            rsi = df['RSI_14'].iloc[i]
            sma = df['SMA_10'].iloc[i]
            prev_sma = df['SMA_10'].iloc[i-1]
            
            # 🔥 MORE AGGRESSIVE STRATEGY RULES:
            buy_signal = (rsi < 40) or (sma > prev_sma)  # Less strict RSI + any upward momentum
            sell_signal = (rsi > 70) or (sma < prev_sma)  # Take profits earlier
            
            # Execute trades
            if position == 0 and buy_signal and cash > 0:
                # Buy
                shares = cash / current_price
                cash = 0
                position = 1
                signals.append(('BUY', df.index[i], current_price))
                
            elif position == 1 and sell_signal:
                # Sell
                cash = shares * current_price
                shares = 0
                position = 0
                signals.append(('SELL', df.index[i], current_price))
            
            # Track portfolio value
            portfolio_value.append(cash + (shares * current_price))
        
        return signals, portfolio_value
    
    def backtest_strategy(self, filepath, strategy_name='momentum'):
        """Run complete backtest"""
        df = self.load_data(filepath)
        
        if strategy_name == 'momentum':
            signals, portfolio_values = self.simple_momentum_strategy(df)
        
        # Calculate performance metrics
        final_value = portfolio_values[-1] if portfolio_values else self.initial_capital
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # Buy & Hold comparison
        buy_hold_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
        
        self.results = {
            'signals': signals,
            'portfolio_values': portfolio_values,
            'final_value': final_value,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'num_trades': len([s for s in signals if s[0] == 'BUY'])
        }
        
        return self.results
    
    def plot_results(self, df):
        """Plot strategy performance"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Price and signals
        ax1.plot(df.index, df['Close'], label='Price', linewidth=2)
        
        buy_signals = [s for s in self.results['signals'] if s[0] == 'BUY']
        sell_signals = [s for s in self.results['signals'] if s[0] == 'SELL']
        
        if buy_signals:
            buy_dates = [s[1] for s in buy_signals]
            buy_prices = [s[2] for s in buy_signals]
            ax1.scatter(buy_dates, buy_prices, color='green', marker='^', s=100, label='Buy', zorder=5)
        
        if sell_signals:
            sell_dates = [s[1] for s in sell_signals]
            sell_prices = [s[2] for s in sell_signals]
            ax1.scatter(sell_dates, sell_prices, color='red', marker='v', s=100, label='Sell', zorder=5)
        
        ax1.set_title('Trading Signals')
        ax1.legend()
        ax1.grid(True)
        
        # Portfolio value
        ax2.plot(df.index[1:], self.results['portfolio_values'], label='Strategy', linewidth=2)
        ax2.axhline(y=self.initial_capital, color='red', linestyle='--', label='Initial Capital')
        ax2.set_title('Portfolio Value Over Time')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def print_performance(self):
        """Print strategy performance"""
        print("\n" + "="*50)
        print("📊 STRATEGY PERFORMANCE REPORT")
        print("="*50)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Portfolio Value: ${self.results['final_value']:,.2f}")
        print(f"Total Return: {self.results['total_return']:.2f}%")
        print(f"Buy & Hold Return: {self.results['buy_hold_return']:.2f}%")
        print(f"Number of Trades: {self.results['num_trades']}")
        print(f"Strategy vs Buy&Hold: {self.results['total_return'] - self.results['buy_hold_return']:.2f}%")
        print("="*50)

if __name__ == "__main__":
    # Test the strategy on AAPL
    strategy = TradingStrategy(initial_capital=10000)
    results = strategy.backtest_strategy("../data/processed/AAPL_1mo_1d_processed.csv")
    strategy.plot_results(strategy.df)
    strategy.print_performance()