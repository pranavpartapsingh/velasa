import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_dashboard(portfolio):
    """Render the main dashboard with portfolio overview and market insights"""
    st.markdown("## Dashboard")
    
    # Portfolio Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Portfolio Value",
            f"${portfolio.get_total_value():,.2f}",
            f"{portfolio.get_daily_change():+.2f}%"
        )
    
    with col2:
        st.metric(
            "Today's P/L",
            f"${portfolio.get_daily_profit():,.2f}",
            f"{portfolio.get_daily_profit_percentage():+.2f}%"
        )
    
    with col3:
        st.metric(
            "Available Cash",
            f"${portfolio.get_cash_balance():,.2f}"
        )

    # Portfolio Performance Chart
    st.markdown("### Portfolio Performance")
    performance_data = portfolio.get_performance_history()
    if not performance_data.empty:
        st.line_chart(performance_data)
    else:
        st.info("Start trading to see your portfolio performance")

    # Recent Transactions
    st.markdown("### Recent Transactions")
    transactions = portfolio.get_recent_transactions()
    if not transactions.empty:
        st.dataframe(transactions)
    else:
        st.info("No recent transactions")
