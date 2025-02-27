import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

class Portfolio:
    def __init__(self, username: str):
        if 'users' not in st.session_state:
            st.session_state.users = {}
        
        if username not in st.session_state.users:
            st.session_state.users[username] = {
                'portfolio': {
                    'cash': 100000,  # Starting cash
                    'positions': {},  # Stock positions
                    'transactions': []  # Transaction history
                }
            }
        
        self.username = username
        self.portfolio = st.session_state.users[username]['portfolio']

    def get_total_value(self) -> float:
        """Calculate total portfolio value including cash and positions"""
        total = self.portfolio['cash']
        
        for symbol, position in self.portfolio['positions'].items():
            try:
                current_price = yf.Ticker(symbol).history(period='1d')['Close'].iloc[-1]
                total += position['quantity'] * current_price
            except:
                continue
                
        return total

    def get_cash_balance(self) -> float:
        """Get available cash balance"""
        return self.portfolio['cash']

    def get_daily_change(self) -> float:
        """Calculate daily portfolio change percentage"""
        try:
            yesterday_value = self.get_total_value() - self.get_daily_profit()
            return (self.get_daily_profit() / yesterday_value) * 100
        except:
            return 0.0

    def get_daily_profit(self) -> float:
        """Calculate daily profit/loss"""
        profit = 0
        for symbol, position in self.portfolio['positions'].items():
            try:
                hist = yf.Ticker(symbol).history(period='2d')
                if len(hist) >= 2:
                    yesterday_price = hist['Close'].iloc[-2]
                    current_price = hist['Close'].iloc[-1]
                    profit += position['quantity'] * (current_price - yesterday_price)
            except:
                continue
        return profit

    def get_daily_profit_percentage(self) -> float:
        """Calculate daily profit/loss percentage"""
        try:
            return (self.get_daily_profit() / self.get_total_value()) * 100
        except:
            return 0.0

    def get_performance_history(self) -> pd.DataFrame:
        """Get portfolio performance history"""
        # For demo, return last 30 days of simulated data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_value = self.get_total_value()
        
        # Generate random-walk data around current value
        import numpy as np
        np.random.seed(42)  # For reproducibility
        daily_returns = np.random.normal(0.0001, 0.02, size=len(dates))
        values = base_value * (1 + np.cumsum(daily_returns))
        
        return pd.DataFrame({
            'Date': dates,
            'Value': values
        }).set_index('Date')

    def get_recent_transactions(self) -> pd.DataFrame:
        """Get recent transaction history"""
        if not self.portfolio['transactions']:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.portfolio['transactions'])
        df['Date'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('Date', ascending=False)
        
        return df[['Date', 'type', 'symbol', 'quantity', 'price', 'total']].head(10)

    def place_buy_order(self, symbol: str, quantity: int, price: float) -> bool:
        """Place a buy order"""
        total_cost = quantity * price
        
        if total_cost > self.portfolio['cash']:
            return False
            
        # Update cash balance
        self.portfolio['cash'] -= total_cost
        
        # Update position
        if symbol not in self.portfolio['positions']:
            self.portfolio['positions'][symbol] = {
                'quantity': quantity,
                'avg_price': price
            }
        else:
            current_position = self.portfolio['positions'][symbol]
            total_quantity = current_position['quantity'] + quantity
            total_cost_basis = (current_position['quantity'] * current_position['avg_price']) + (quantity * price)
            current_position['quantity'] = total_quantity
            current_position['avg_price'] = total_cost_basis / total_quantity
            
        # Record transaction
        self.portfolio['transactions'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_cost
        })
        
        return True

    def place_sell_order(self, symbol: str, quantity: int, price: float) -> bool:
        """Place a sell order"""
        if symbol not in self.portfolio['positions']:
            return False
            
        position = self.portfolio['positions'][symbol]
        if position['quantity'] < quantity:
            return False
            
        total_value = quantity * price
        
        # Update cash balance
        self.portfolio['cash'] += total_value
        
        # Update position
        position['quantity'] -= quantity
        if position['quantity'] == 0:
            del self.portfolio['positions'][symbol]
            
        # Record transaction
        self.portfolio['transactions'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_value
        })
        
        return True
