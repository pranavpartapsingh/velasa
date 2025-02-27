import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from .market_data import MarketData

class Portfolio:
    def __init__(self, username: str):
        self.username = username
        self.portfolio = st.session_state.users[username]['portfolio']
        if 'transactions' not in self.portfolio:
            self.portfolio['transactions'] = []
        if 'pending_orders' not in self.portfolio:
            self.portfolio['pending_orders'] = []
        if 'created_at' not in st.session_state.users[username]:
            st.session_state.users[username]['created_at'] = datetime.now().isoformat()

    def get_positions(self) -> Dict[str, int]:
        return self.portfolio['positions']

    def get_cash(self) -> float:
        return self.portfolio['cash']

    def execute_trade(
        self,
        symbol: str,
        quantity: int,
        is_buy: bool,
        order_type: str = "Market",
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        validity: str = "Day"
    ) -> bool:
        current_price = MarketData.get_current_price(symbol)

        # For market orders
        if order_type == "Market":
            return self._execute_market_order(symbol, quantity, is_buy, current_price)

        # For limit, stop-loss, and stop-limit orders
        order = {
            'symbol': symbol,
            'quantity': quantity,
            'is_buy': is_buy,
            'order_type': order_type,
            'price': price,
            'trigger_price': trigger_price,
            'validity': validity,
            'created_at': datetime.now().isoformat(),
            'expires_at': None if validity == "GTC" else (
                datetime.now() + timedelta(days=1)
            ).isoformat()
        }

        # Validate order
        if is_buy and (price or current_price) * quantity > self.portfolio['cash']:
            return False
        if not is_buy and (
            symbol not in self.portfolio['positions'] or 
            self.portfolio['positions'][symbol] < quantity
        ):
            return False

        self.portfolio['pending_orders'].append(order)
        return True

    def _execute_market_order(
        self,
        symbol: str,
        quantity: int,
        is_buy: bool,
        current_price: float
    ) -> bool:
        total_cost = current_price * quantity

        if is_buy:
            if total_cost > self.portfolio['cash']:
                return False

            self.portfolio['cash'] -= total_cost
            self.portfolio['positions'][symbol] = (
                self.portfolio['positions'].get(symbol, 0) + quantity
            )

            self._record_transaction(symbol, 'buy', quantity, current_price)
        else:
            if symbol not in self.portfolio['positions'] or self.portfolio['positions'][symbol] < quantity:
                return False

            self.portfolio['cash'] += total_cost
            self.portfolio['positions'][symbol] -= quantity

            self._record_transaction(symbol, 'sell', quantity, current_price)

            if self.portfolio['positions'][symbol] == 0:
                del self.portfolio['positions'][symbol]

        return True

    def _record_transaction(self, symbol: str, trade_type: str, quantity: int, price: float):
        """Record a new transaction in the portfolio history"""
        self.portfolio['transactions'].append({
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'type': trade_type,
            'quantity': quantity,
            'price': price,
            'entry_price': self._get_entry_price(symbol) if trade_type == 'sell' else price
        })

    def _get_entry_price(self, symbol: str) -> float:
        """Calculate the average entry price for a symbol"""
        buys = [t for t in self.portfolio['transactions'] 
                if t['symbol'] == symbol and t['type'] == 'buy']
        if not buys:
            return 0
        total_cost = sum(t['price'] * t['quantity'] for t in buys)
        total_quantity = sum(t['quantity'] for t in buys)
        return total_cost / total_quantity if total_quantity > 0 else 0

    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value including cash and positions"""
        total_value = self.portfolio['cash']
        for symbol, quantity in self.portfolio['positions'].items():
            total_value += MarketData.get_current_price(symbol) * quantity
        return total_value

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Get the full transaction history"""
        return sorted(
            self.portfolio['transactions'],
            key=lambda x: x['timestamp'],
            reverse=True
        )

    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """Get all pending orders"""
        return [
            order for order in self.portfolio['pending_orders']
            if order['expires_at'] is None or
            datetime.fromisoformat(order['expires_at']) > datetime.now()
        ]

    def _get_account_age(self) -> datetime:
        """Get the account creation date"""
        created_at = st.session_state.users[self.username]['created_at']
        return datetime.fromisoformat(created_at)

    def get_portfolio_metrics(self) -> Dict[str, Any]:
        """Get comprehensive portfolio metrics"""
        total_value = self.get_portfolio_value()
        initial_investment = 100000  # Starting cash

        metrics = {
            'total_value': total_value,
            'cash': self.get_cash(),
            'invested_value': total_value - self.get_cash(),
            'total_return': ((total_value - initial_investment) / initial_investment) * 100,
            'position_count': len(self.get_positions()),
            'pending_orders': len(self.get_pending_orders())
        }

        # Calculate daily returns
        if self.get_transaction_history():
            first_trade = min(
                datetime.fromisoformat(t['timestamp'])
                for t in self.get_transaction_history()
            )
            days_trading = (datetime.now() - first_trade).days or 1
            metrics['daily_return'] = metrics['total_return'] / days_trading

        return metrics