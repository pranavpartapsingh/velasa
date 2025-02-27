import streamlit as st
import pandas as pd

def show_portfolio():
    """Display user portfolio and performance"""
    st.subheader("Your Portfolio")
    
    # Sample portfolio data (replace with database integration)
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame({
            'Symbol': ['AAPL', 'GOOGL', 'MSFT'],
            'Quantity': [10, 5, 15],
            'Avg_Price': [150.0, 2800.0, 300.0],
            'Current_Price': [170.0, 2900.0, 330.0],
        })
    
    portfolio = st.session_state.portfolio
    
    # Calculate performance metrics
    portfolio['Market_Value'] = portfolio['Quantity'] * portfolio['Current_Price']
    portfolio['Cost_Basis'] = portfolio['Quantity'] * portfolio['Avg_Price']
    portfolio['Profit_Loss'] = portfolio['Market_Value'] - portfolio['Cost_Basis']
    portfolio['Return'] = (portfolio['Profit_Loss'] / portfolio['Cost_Basis'] * 100).round(2)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Value", f"${portfolio['Market_Value'].sum():,.2f}")
    with col2:
        st.metric("Total P/L", f"${portfolio['Profit_Loss'].sum():,.2f}")
    with col3:
        total_return = (portfolio['Profit_Loss'].sum() / portfolio['Cost_Basis'].sum() * 100)
        st.metric("Total Return", f"{total_return:.2f}%")
    
    # Display portfolio table
    st.dataframe(portfolio)
