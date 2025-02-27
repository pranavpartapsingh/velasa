import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

def render_trading_interface(portfolio):
    """Render the trading interface with stock search and order placement"""
    st.markdown("## Trading")
    
    # Stock Search
    symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
    
    if symbol:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
                # Stock Information
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"${current_price:.2f}")
                with col2:
                    st.metric("Volume", f"{info.get('volume', 0):,.0f}")
                with col3:
                    st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f}B")
                
                # Trading Form
                with st.form("trade_form"):
                    st.markdown("### Place Order")
                    
                    order_type = st.selectbox(
                        "Order Type",
                        ["Market", "Limit"]
                    )
                    
                    action = st.selectbox(
                        "Action",
                        ["Buy", "Sell"]
                    )
                    
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=1
                    )
                    
                    if order_type == "Limit":
                        limit_price = st.number_input(
                            "Limit Price",
                            value=float(current_price),
                            step=0.01
                        )
                    
                    total_cost = quantity * current_price
                    st.markdown(f"**Total Cost: ${total_cost:,.2f}**")
                    
                    if st.form_submit_button("Place Order"):
                        if action == "Buy":
                            success = portfolio.place_buy_order(
                                symbol=symbol,
                                quantity=quantity,
                                price=current_price
                            )
                            if success:
                                st.success(f"Successfully bought {quantity} shares of {symbol}")
                            else:
                                st.error("Insufficient funds for this purchase")
                        else:
                            success = portfolio.place_sell_order(
                                symbol=symbol,
                                quantity=quantity,
                                price=current_price
                            )
                            if success:
                                st.success(f"Successfully sold {quantity} shares of {symbol}")
                            else:
                                st.error("Insufficient shares for this sale")
                
                # Price Chart
                st.markdown("### Price History")
                hist = stock.history(period="1y")
                fig = go.Figure(data=[
                    go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close']
                    )
                ])
                fig.update_layout(
                    title=f"{symbol} Price History",
                    yaxis_title="Price ($)",
                    template="plotly_dark"
                )
                st.plotly_chart(fig)
                
            else:
                st.error(f"No data available for {symbol}")
                
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
