import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from utils.market_data import MarketData
from utils.portfolio import Portfolio

def render_portfolio_analysis(portfolio: Portfolio):
    st.subheader("Portfolio Analysis")

    # Portfolio Value Over Time
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Portfolio Performance")
        portfolio_value_history = _get_portfolio_value_history(portfolio)

        # Line chart for portfolio value
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio_value_history.index,
            y=portfolio_value_history['value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#FFD700')
        ))

        fig.update_layout(
            title="Portfolio Value Over Time",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Key Metrics")
        metrics = portfolio.get_portfolio_metrics()

        # Display metrics
        st.metric("Total Return", f"{metrics['total_return']:.2f}%")
        st.metric("Daily Average Return", f"{metrics.get('daily_return', 0):.2f}%")
        st.metric("Total Value", f"${metrics['total_value']:,.2f}")

    # Asset Allocation (Bar Chart)
    st.markdown("### Asset Allocation")
    positions = portfolio.get_positions()
    if positions:
        position_values = {
            symbol: MarketData.get_current_price(symbol) * qty 
            for symbol, qty in positions.items()
        }

        # Bar chart for asset allocation
        fig_allocation = go.Figure(data=[
            go.Bar(
                x=list(position_values.keys()),
                y=list(position_values.values()),
                marker_color='#FFD700'
            )
        ])

        fig_allocation.update_layout(
            title="Asset Allocation by Value",
            xaxis_title="Stocks",
            yaxis_title="Value ($)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_allocation, use_container_width=True)
    else:
        st.info("No positions in portfolio")

    # Daily Returns Distribution (Histogram)
    st.markdown("### Returns Distribution")
    if len(portfolio_value_history) > 1:
        daily_returns = portfolio_value_history['value'].pct_change().dropna()

        fig_returns = go.Figure(data=[
            go.Histogram(
                x=daily_returns,
                nbinsx=30,
                marker_color='#FFD700'
            )
        ])

        fig_returns.update_layout(
            title="Distribution of Daily Returns",
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_returns, use_container_width=True)

def _get_portfolio_value_history(portfolio: Portfolio) -> pd.DataFrame:
    """Generate historical portfolio value data"""
    dates = pd.date_range(
        start=portfolio._get_account_age(),
        end=datetime.now(),
        freq='D'
    )

    values = []
    positions = portfolio.get_positions()

    for date in dates:
        daily_value = portfolio.get_cash()
        for symbol, quantity in positions.items():
            stock_data = MarketData.get_stock_data(
                symbol,
                period='1d',
                start=date,
                end=date + timedelta(days=1)
            )
            if not stock_data.empty:
                daily_value += stock_data['Close'].iloc[0] * quantity
        values.append(daily_value)

    return pd.DataFrame({
        'value': values
    }, index=dates)

def render_transaction_history(portfolio: Portfolio):
    st.subheader("Transaction History")

    transactions = portfolio.get_transaction_history()
    if not transactions:
        st.info("No transactions yet")
        return

    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['profit_loss'] = df.apply(
        lambda x: (x['price'] - x['entry_price']) * x['quantity'] 
        if x['type'] == 'sell' else 0,
        axis=1
    )

    # Transaction Table
    st.dataframe(
        df[['timestamp', 'symbol', 'type', 'quantity', 'price', 'profit_loss']],
        use_container_width=True
    )

    # Profit/Loss Over Time (Line Chart)
    cumulative_pl = df['profit_loss'].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=cumulative_pl,
        mode='lines+markers',
        name='Cumulative P/L',
        line=dict(color='#FFD700' if cumulative_pl.iloc[-1] > 0 else '#FF4B4B')
    ))

    fig.update_layout(
        title="Cumulative Profit/Loss Over Time",
        xaxis_title="Date",
        yaxis_title="Profit/Loss ($)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Trading Activity by Symbol (Bar Chart)
    trades_by_symbol = df.groupby('symbol').size()

    fig_activity = go.Figure(data=[
        go.Bar(
            x=trades_by_symbol.index,
            y=trades_by_symbol.values,
            marker_color='#FFD700'
        )
    ])

    fig_activity.update_layout(
        title="Trading Activity by Symbol",
        xaxis_title="Symbol",
        yaxis_title="Number of Trades",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig_activity, use_container_width=True)