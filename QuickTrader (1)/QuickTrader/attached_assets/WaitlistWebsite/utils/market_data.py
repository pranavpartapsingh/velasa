import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class MarketData:
    @staticmethod
    def get_stock_data(symbol: str, period: str = '1mo') -> pd.DataFrame:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            return df
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_info(symbol: str) -> dict:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'price': info.get('currentPrice', 0),
                'change': info.get('regularMarketChangePercent', 0),
                'volume': info.get('volume', 0)
            }
        except:
            return {}

    @staticmethod
    def get_current_price(symbol: str) -> float:
        try:
            stock = yf.Ticker(symbol)
            return stock.info.get('currentPrice', 0)
        except:
            return 0
