import yfinance as yf
import pandas as pd

def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def get_stock_info(symbol: str) -> dict:
    """Get stock information and company details"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'name': info.get('longName', ''),
            'sector': info.get('sector', ''),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
        }
    except:
        return {}
