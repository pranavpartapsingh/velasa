import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_portfolio_analysis(portfolio):
    """Render portfolio analysis with performance metrics and charts"""
    st.markdown("## Portfolio Analysis")

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_value = portfolio.get_total_value()
        st.metric(
            "Total Portfolio Value",
            f"${total_value:,.2f}",
            f"{portfolio.get_daily_change():+.2f}%"
        )
    
    with col2:
        roi = ((total_value - 100000) / 100000) * 100  # Assuming initial investment of 100k
        st.metric(
            "Return on Investment",
            f"{roi:,.2f}%",
            f"{portfolio.get_daily_profit():+,.2f}"
        )
    
    with col3:
        positions = len(portfolio.portfolio['positions'])
        st.metric(
            "Active Positions",
            positions,
            None
        )

    # Performance chart
    st.markdown("### Performance History")
    performance_data = portfolio.get_performance_history()
    
    if not performance_data.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=performance_data.index,
                y=performance_data['Value'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#FFD700', width=2)
            )
        )
        
        fig.update_layout(
            template='plotly_dark',
            title="Portfolio Value Over Time",
            xaxis_title="Date",
            yaxis_title="Value ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start trading to see your portfolio performance")

    # Position Distribution
    st.markdown("### Position Distribution")
    positions = portfolio.portfolio['positions']
    if positions:
        position_values = []
        for symbol, position in positions.items():
            try:
                current_price = position['current_price']
                value = position['quantity'] * current_price
                position_values.append({
                    'Symbol': symbol,
                    'Value': value
                })
            except:
                continue
        
        if position_values:
            df = pd.DataFrame(position_values)
            fig = go.Figure(data=[
                go.Pie(
                    labels=df['Symbol'],
                    values=df['Value'],
                    hole=.3,
                    marker_colors=['#FFD700', '#FFA500', '#FF4500']
                )
            ])
            
            fig.update_layout(
                template='plotly_dark',
                title="Portfolio Distribution",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active positions to display")
    else:
        st.info("Add positions to see portfolio distribution")

def render_transaction_history(portfolio):
    """Display transaction history"""
    st.markdown("### Transaction History")
    
    transactions = portfolio.get_recent_transactions()
    
    if not transactions.empty:
        # Style the dataframe
        st.dataframe(
            transactions.style.format({
                'price': '${:.2f}',
                'total': '${:.2f}'
            })
        )
    else:
        st.info("No transactions to display")
