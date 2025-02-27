import streamlit as st
import plotly.graph_objects as go
from utils.market_data import MarketData
from utils.portfolio import Portfolio
from utils.sentiment import SentimentAnalyzer
import pandas as pd

def render_trading_interface(portfolio: Portfolio):
    st.subheader("Advanced Trading")

    # Stock Search and Analysis
    col1, col2 = st.columns([2, 1])

    with col1:
        symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()

    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd"],
            index=2
        )

    if symbol:
        stock_data = MarketData.get_stock_data(symbol, period=timeframe)
        stock_info = MarketData.get_stock_info(symbol)

        if not stock_data.empty:
            # Advanced Price Chart
            fig = go.Figure()

            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close'],
                name="OHLC"
            ))

            # Add volume bars
            fig.add_trace(go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name="Volume",
                yaxis="y2",
                opacity=0.3
            ))

            # Calculate moving averages
            stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
            stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()

            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['MA20'],
                name="20 MA",
                line=dict(color='orange')
            ))

            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['MA50'],
                name="50 MA",
                line=dict(color='blue')
            ))

            fig.update_layout(
                title=f"{symbol} Advanced Analysis",
                yaxis_title="Price",
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right"
                ),
                xaxis_rangeslider_visible=False,
                height=600,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )

            st.plotly_chart(fig, use_container_width=True)

            # Trading Stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"${stock_info['price']:,.2f}")
            with col2:
                st.metric("24h Change", f"{stock_info['change']:.2f}%")
            with col3:
                sentiment = SentimentAnalyzer().analyze_news(symbol)
                st.metric("Sentiment", sentiment['sentiment_label'])
            with col4:
                st.metric("Volume", f"{stock_info['volume']:,}")

            # Advanced Order Types
            with st.form("advanced_trade_form"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    order_type = st.selectbox(
                        "Order Type",
                        ["Market", "Limit", "Stop Loss", "Stop Limit"]
                    )
                    quantity = st.number_input("Quantity", min_value=1, value=1)

                with col2:
                    trade_type = st.selectbox("Trade Type", ["Buy", "Sell"])
                    if order_type != "Market":
                        price = st.number_input(
                            "Price",
                            min_value=0.01,
                            value=float(stock_info['price']),
                            step=0.01
                        )

                with col3:
                    if order_type in ["Stop Loss", "Stop Limit"]:
                        trigger_price = st.number_input(
                            "Trigger Price",
                            min_value=0.01,
                            value=float(stock_info['price']),
                            step=0.01
                        )

                    validity = st.selectbox(
                        "Validity",
                        ["Day", "GTC (Good Till Cancelled)"]
                    )

                # Order preview
                total_cost = quantity * stock_info['price']
                st.info(f"Order Preview: {trade_type} {quantity} shares of {symbol} @ {order_type} order")
                st.write(f"Estimated Cost: ${total_cost:,.2f}")

                if st.form_submit_button("Place Order", use_container_width=True):
                    success = portfolio.execute_trade(
                        symbol, 
                        quantity, 
                        trade_type == "Buy",
                        order_type=order_type,
                        price=price if order_type != "Market" else None,
                        trigger_price=trigger_price if order_type in ["Stop Loss", "Stop Limit"] else None,
                        validity=validity
                    )
                    if success:
                        st.success(f"Successfully placed {order_type} order for {quantity} shares of {symbol}")
                    else:
                        st.error(f"Failed to place order. Please check your balance/positions.")

            # Holdings for this stock
            if symbol in portfolio.get_positions():
                st.subheader(f"Your {symbol} Position")
                position_qty = portfolio.get_positions()[symbol]
                position_value = position_qty * stock_info['price']
                avg_price = portfolio._get_entry_price(symbol)
                profit_loss = (stock_info['price'] - avg_price) * position_qty

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Quantity", position_qty)
                with col2:
                    st.metric("Average Price", f"${avg_price:.2f}")
                with col3:
                    st.metric("Current Value", f"${position_value:,.2f}")
                with col4:
                    st.metric("P&L", f"${profit_loss:,.2f}", f"{(profit_loss/position_value)*100:.2f}%")