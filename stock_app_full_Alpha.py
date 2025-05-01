import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
import requests
from datetime import datetime, timedelta

# --- CONFIG ---
API_KEY = "7DUI9BT9YC0EE3J0"
NEWS_API_KEY = "eae1f517baad44b79c68847ebab2eda0"
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

# --- FUNCTION TO FETCH STOCK DATA ---
@st.cache_data(ttl=86400)
def fetch_data(ticker, start, end):
    ts = TimeSeries(key=API_KEY, output_format="pandas")
    try:
        data, meta_data = ts.get_daily(symbol=ticker,outputsize="compact")
        data.index = pd.to_datetime(data.index)
        data = data.sort_index()
        filtered_data = data.loc[(data.index >= pd.to_datetime(start)) & (data.index <= pd.to_datetime(end))]
        return filtered_data
    except Exception as e:
        st.error(f"Failed to fetch data for {ticker}: {e}")
        return pd.DataFrame()

# --- FUNCTION TO FETCH NEWS ---
def fetch_news(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json()["articles"][:5]
        return articles
    else:
        st.error("Failed to fetch news")
        return []

# --- PORTFOLIO TRACKER ---
def calculate_portfolio_value(data, shares_owned):
    latest_price = data["4. close"].iloc[-1]
    return latest_price * shares_owned

# --- BACKTEST SMA STRATEGY ---
def backtest_sma(data, short_window, long_window):
    data["SMA_Short"] = data["4. close"].rolling(window=short_window).mean()
    data["SMA_Long"] = data["4. close"].rolling(window=long_window).mean()
    data["Signal"] = 0
    data["Signal"][short_window:] = \
        (data["SMA_Short"][short_window:] > data["SMA_Long"][short_window:]).astype(int)
    data["Position"] = data["Signal"].diff()

    # Plot strategy
    fig, ax = plt.subplots(figsize=(12, 6))
