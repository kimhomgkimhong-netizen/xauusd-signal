import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ta

# ======================
# Page Config + Dark Mode
# ======================
st.set_page_config(
    page_title="XAUUSD Signal Bot",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stMetric {
        background-color: #1a1d24;
        padding: 15px;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #fafafa !important;
    }
</style>
""", unsafe_allow_html=True)

# ======================
# Title
# ======================
st.title("🥇 XAUUSD AI Signal")
st.caption("Real-time Gold Signal • Buy / Sell • TP / SL")

# ======================
# Sidebar
# ======================
st.sidebar.header("⚙️ Settings")

timeframe = st.sidebar.selectbox(
    "Timeframe",
    options=["15m", "1h", "4h", "1d"],
    index=1
)

ema_fast = st.sidebar.slider("EMA Fast", 5, 50, 9)
ema_slow = st.sidebar.slider("EMA Slow", 10, 200, 21)
rsi_period = st.sidebar.slider("RSI Period", 7, 21, 14)

# ======================
# Fetch Data
# ======================
@st.cache_data(ttl=60)
def get_data(interval):
    ticker = yf.Ticker("GC=F")
    df = ticker.history(period="5d", interval=interval)
    if df.empty:
        df = ticker.history(period="1mo", interval=interval)
    return df

df = get_data(timeframe)

if df.empty:
    st.error("មិនអាចទាញទិន្នន័យបាន។ សូមព្យាយាមម្តងទៀត។")
    st.stop()

# ======================
# Indicators
# ======================
df["EMA_Fast"] = ta.trend.ema_indicator(df["Close"], window=ema_fast)
df["EMA_Slow"] = ta.trend.ema_indicator(df["Close"], window=ema_slow)
df["RSI"] = ta.momentum.rsi(df["Close"], window=rsi_period)
df["ATR"] = ta.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=14)

# ======================
# Signal Logic
# ======================
latest = df.iloc[-1]
prev = df.iloc[-2]

signal = "HOLD"
entry = latest["Close"]
sl = None
tp1 = None
tp2 = None

if (latest["EMA_Fast"] > latest["EMA_Slow"]) and (prev["EMA_Fast"] <= prev["EMA_Slow"]) and (latest["RSI"] < 70):
    signal = "BUY"
    sl = entry - (latest["ATR"] * 1.5)
    tp1 = entry + (latest["ATR"] * 2)
    tp2 = entry + (latest["ATR"] * 3.5)

elif (latest["EMA_Fast"] < latest["EMA_Slow"]) and (prev["EMA_Fast"] >= prev["EMA_Slow"]) and (latest["RSI"] > 30):
    signal = "SELL"
    sl = entry + (latest["ATR"] * 1.5)
    tp1 = entry - (latest["ATR"] * 2)
    tp2 = entry - (latest["ATR"] * 3.5)

# ======================
# Metrics
# ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("តម្លៃបច្ចុប្បន្ន", f"${entry:,.2f}")

with col2:
    if signal == "BUY":
        st.metric("Signal", "🟢 BUY")
    elif signal == "SELL":
        st.metric("Signal", "🔴 SELL")
    else:
        st.metric("Signal", "⚪ HOLD")

with col3:
    st.metric("RSI", f"{latest['RSI']:.1f}")

with col4:
    st.metric("ATR", f"{latest['ATR']:.2f}")

# ======================
# Signal Details
# ======================
st.markdown("---")

if signal in ["BUY", "SELL"]:
    st.subheader(f"📊 Signal Details — {signal}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entry", f"${entry:,.2f}")
    c2.metric("Stop Loss", f"${sl:,.2f}")
    c3.metric("Take Profit 1", f"${tp1:,.2f}")
    c4.metric("Take Profit 2", f"${tp2:,.2f}")
else:
    st.info("⏳ កំពុងរង់ចាំ Signal... មិនទាន់មាន EMA Cross ទេ។")

# ======================
# Chart
# ======================
st.markdown("---")
st.subheader("📈 XAUUSD Chart")

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="XAUUSD"
))

fig.add_trace(go.Scatter(
    x=df.index, y=df["EMA_Fast"],
    line=dict(color="#00ff88", width=1.5),
    name=f"EMA {ema_fast}"
))

fig.add_trace(go.Scatter(
    x=df.index, y=df["EMA_Slow"],
    line=dict(color="#ff4b4b", width=1.5),
    name=f"EMA {ema_slow}"
))

fig.update_layout(
    template="plotly_dark",
    height=550,
    xaxis_rangeslider_visible=False,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", y=1.02)
)

st.plotly_chart(fig, use_container_width=True)

# ======================
# Footer
# ======================
st.markdown("---")
st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data: Yahoo Finance (GC=F) | Not financial advice")
