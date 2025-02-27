import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_stock_chart(data):
    """Display interactive stock charts"""
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="OHLC"
        ),
        secondary_y=False,
    )

    # Add volume bar chart
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name="Volume",
            opacity=0.3
        ),
        secondary_y=True,
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Close'].rolling(window=20).mean(),
            name="20 SMA",
            line=dict(color='orange', width=1)
        ),
        secondary_y=False,
    )

    # Update layout
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
        title="Stock Price & Volume Analysis",
        yaxis_title="Price",
        yaxis2_title="Volume"
    )

    st.plotly_chart(fig, use_container_width=True)
