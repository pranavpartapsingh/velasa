import streamlit as st
import plotly.graph_objects as go
from utils.portfolio import Portfolio
from utils.market_data import MarketData
from utils.sentiment import SentimentAnalyzer

def render_dashboard(portfolio: Portfolio):
    st.subheader("Portfolio Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Portfolio Value", f"${portfolio.get_portfolio_value():,.2f}")
    with col2:
        st.metric("Cash Balance", f"${portfolio.get_cash():,.2f}")
    with col3:
        st.metric("Positions", len(portfolio.get_positions()))

    # Portfolio Composition
    if portfolio.get_positions():
        fig = go.Figure(data=[go.Pie(
            labels=list(portfolio.get_positions().keys()),
            values=[MarketData.get_current_price(symbol) * qty 
                   for symbol, qty in portfolio.get_positions().items()],
            hole=.3
        )])
        fig.update_layout(
            title="Portfolio Composition",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig)

    # Position Details
    st.subheader("Positions")
    for symbol, quantity in portfolio.get_positions().items():
        with st.container():
            col1, col2, col3 = st.columns(3)
            current_price = MarketData.get_current_price(symbol)
            position_value = current_price * quantity
            
            with col1:
                st.write(f"**{symbol}**")
                st.write(f"Quantity: {quantity}")
            with col2:
                st.write(f"Current Price: ${current_price:,.2f}")
                st.write(f"Position Value: ${position_value:,.2f}")
            with col3:
                sentiment = SentimentAnalyzer().analyze_news(symbol)
                st.write(f"Sentiment: {sentiment['sentiment_label']}")
