import os
import json
import time
import math
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

try:
    from gnews import GNews
except Exception:
    GNews = None

try:
    from groq import Groq
except Exception:
    Groq = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ============================================================
# OMNITRIX TERMINAL V2
# Institutional Indian Equity Research + Paper Trading Terminal
# ============================================================


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OMNITRIX TERMINAL",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
TRADE_DIR = DATA_DIR / "trades"
RESEARCH_DIR = DATA_DIR / "research"

for folder in [DATA_DIR, LOG_DIR, TRADE_DIR, RESEARCH_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

WATCHLIST_FILE = DATA_DIR / "watchlist.json"
PAPER_ORDERS_FILE = TRADE_DIR / "paper_orders.csv"
JOURNAL_FILE = TRADE_DIR / "journal.csv"
RESEARCH_CACHE_FILE = RESEARCH_DIR / "research_cache.json"


# ============================================================
# 3. SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "page": "Overview",
    "ai_enabled": False,
    "ai_provider": "Local",
    "ai_model": "",
    "ai_endpoint": "http://localhost:11434/v1",
    "ai_temperature": 0.1,
    "ai_max_tokens": 1200,
    "research_result": None,
    "scanner_result": None,
    "selected_stock": "RELIANCE",
    "watchlist": [],
    "paper_mode": True,
    "system_logs": [],
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 4. INDIAN EQUITY MASTER
# ============================================================

STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "MARUTI": "MARUTI.NS",
    "M&M": "M&M.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS",
    "ONGC": "ONGC.NS",
    "COALINDIA": "COALINDIA.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "HINDALCO": "HINDALCO.NS",
    "WIPRO": "WIPRO.NS",
    "TECHM": "TECHM.NS",
    "HCLTECH": "HCLTECH.NS",
    "LTIM": "LTIM.NS",
    "TITAN": "TITAN.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "SBILIFE": "SBILIFE.NS",
    "HDFCLIFE": "HDFCLIFE.NS",
    "DRREDDY": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "TRENT": "TRENT.NS",
    "BEL": "BEL.NS",
    "HAL": "HAL.NS",
    "BHEL": "BHEL.NS",
    "IRFC": "IRFC.NS",
    "RVNL": "RVNL.NS",
    "IRCTC": "IRCTC.NS",
    "IOC": "IOC.NS",
    "BPCL": "BPCL.NS",
    "GAIL": "GAIL.NS",
    "DLF": "DLF.NS",
    "LODHA": "LODHA.NS",
    "PIDILITIND": "PIDILITIND.NS",
    "DMART": "DMART.NS",
    "ZOMATO": "ZOMATO.NS",
    "PAYTM": "PAYTM.NS",
    "JIOFIN": "JIOFIN.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "PNB": "PNB.NS",
    "BANKBARODA": "BANKBARODA.NS",
    "CANBK": "CANBK.NS",
    "IDFCFIRSTB": "IDFCFIRSTB.NS",
    "FEDERALBNK": "FEDERALBNK.NS",
    "YESBANK": "YESBANK.NS",
    "INDIGO": "INDIGO.NS",
    "ADANIGREEN": "ADANIGREEN.NS",
    "ADANIPOWER": "ADANIPOWER.NS",
    "TATAPOWER": "TATAPOWER.NS",
    "SUZLON": "SUZLON.NS",
    "IREDA": "IREDA.NS",
    "DIXON": "DIXON.NS",
    "POLYCAB": "POLYCAB.NS",
    "PERSISTENT": "PERSISTENT.NS",
    "COFORGE": "COFORGE.NS",
    "MPHASIS": "MPHASIS.NS",
    "INDUSTOWER": "INDUSTOWER.NS",
    "BEL": "BEL.NS",
}


# ============================================================
# 5. INSTITUTIONAL CSS
# ============================================================

CSS = """
<style>

html, body, [class*="css"] {
    font-family: Inter, Arial, sans-serif;
}

.stApp {
    background: #080b0f;
    color: #ffffff;
}

[data-testid="stSidebar"] {
    background: #0b0f14;
    border-right: 1px solid #252c34;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 600;
}

p, span, label, div {
    color: #ffffff;
}

.main-title {
    font-size: 23px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #ffffff;
}

.sub-title {
    color: #8f9aa6 !important;
    font-size: 12px;
}

.terminal-header {
    background: #0d1218;
    border: 1px solid #252c34;
    padding: 12px 16px;
    border-radius: 5px;
    margin-bottom: 12px;
}

.status-open {
    color: #23c483 !important;
    font-weight: 700;
}

.status-closed {
    color: #e65b5b !important;
    font-weight: 700;
}

.metric-card {
    background: #0d1218;
    border: 1px solid #252c34;
    border-radius: 5px;
    padding: 12px;
    min-height: 90px;
}

.metric-label {
    color: #87919c !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .5px;
}

.metric-value {
    color: #ffffff !important;
    font-size: 21px;
    font-weight: 650;
    margin-top: 4px;
}

.metric-positive {
    color: #20c997 !important;
}

.metric-negative {
    color: #ef6b73 !important;
}

.section {
    color: #ffffff !important;
    font-size: 15px;
    font-weight: 650;
    margin-top: 12px;
    margin-bottom: 8px;
}

.panel {
    background: #0d1218;
    border: 1px solid #252c34;
    border-radius: 5px;
    padding: 14px;
    margin-bottom: 10px;
}

.small-text {
    color: #8d98a4 !important;
    font-size: 11px;
}

.signal-green {
    color: #21c784 !important;
    font-weight: 700;
}

.signal-red {
    color: #ef626a !important;
    font-weight: 700;
}

.signal-yellow {
    color: #e7b84b !important;
    font-weight: 700;
}

button {
    border-radius: 4px !important;
}

.stButton > button {
    background: #111820;
    color: #ffffff !important;
    border: 1px solid #303943;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #4d5965;
    background: #171e26;
}

[data-testid="stMetric"] {
    background: #0d1218;
    border: 1px solid #252c34;
    padding: 10px;
    border-radius: 5px;
}

[data-testid="stMetricLabel"] {
    color: #8d98a4 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

input, textarea {
    background: #0b1015 !important;
    color: #ffffff !important;
    border: 1px solid #303943 !important;
}

div[data-baseweb="select"] > div {
    background: #0b1015 !important;
    color: #ffffff !important;
    border-color: #303943 !important;
}

.stDataFrame {
    border: 1px solid #252c34;
}

hr {
    border-color: #252c34;
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# 6. LOGGING
# ============================================================

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | {message}"

    st.session_state.system_logs.append(entry)

    if len(st.session_state.system_logs) > 100:
        st.session_state.system_logs = st.session_state.system_logs[-100:]

    try:
        with open(LOG_DIR / "terminal.log", "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


# ============================================================
# 7. WATCHLIST
# ============================================================

def load_watchlist():
    if WATCHLIST_FILE.exists():
        try:
            return json.loads(WATCHLIST_FILE.read_text())
        except Exception:
            pass

    return ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "SBIN"]


def save_watchlist():
    WATCHLIST_FILE.write_text(
        json.dumps(st.session_state.watchlist, indent=2)
    )


if not st.session_state.watchlist:
    st.session_state.watchlist = load_watchlist()


# ============================================================
# 8. MARKET DATA
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_market_data(symbol, period="3mo", interval="1d"):
    ticker = STOCKS.get(symbol, symbol)

    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.columns = [str(c).title() for c in df.columns]

        return df.dropna(subset=["Close"])

    except Exception:
        return pd.DataFrame()


# ============================================================
# 9. TECHNICAL ENGINE
# ============================================================

def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    return 100 - (100 / (1 + rs))


def calculate_indicators(df):
    if df.empty:
        return df

    df = df.copy()

    close = df["Close"]
    volume = df["Volume"]

    df["SMA20"] = close.rolling(20).mean()
    df["SMA50"] = close.rolling(50).mean()

    df["EMA9"] = close.ewm(span=9, adjust=False).mean()
    df["EMA21"] = close.ewm(span=21, adjust=False).mean()

    df["RSI"] = calculate_rsi(close)

    high_low = df["High"] - df["Low"]
    high_close = abs(df["High"] - close.shift())
    low_close = abs(df["Low"] - close.shift())

    true_range = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    df["ATR"] = true_range.rolling(14).mean()

    df["VolumeAvg20"] = volume.rolling(20).mean()
    df["VolumeRatio"] = volume / df["VolumeAvg20"]

    df["Return1D"] = close.pct_change() * 100
    df["Return5D"] = close.pct_change(5) * 100
    df["Return20D"] = close.pct_change(20) * 100

    return df


def get_signal(row):

    if pd.isna(row.get("RSI")):
        return "NEUTRAL"

    bullish = 0
    bearish = 0

    if row["EMA9"] > row["EMA21"]:
        bullish += 1
    else:
        bearish += 1

    if row["Close"] > row["SMA20"]:
        bullish += 1
    else:
        bearish += 1

    if row["Close"] > row["SMA50"]:
        bullish += 1
    else:
        bearish += 1

    if row["RSI"] >= 55:
        bullish += 1
    elif row["RSI"] <= 45:
        bearish += 1

    if bullish >= 3:
        return "BULLISH"

    if bearish >= 3:
        return "BEARISH"

    return "NEUTRAL"


# ============================================================
# 10. MARKET STATUS
# ============================================================

def market_status():

    now = datetime.now()

    weekday = now.weekday()

    if weekday >= 5:
        return "CLOSED"

    market_open = now.replace(
        hour=9,
        minute=15,
        second=0,
        microsecond=0
    )

    market_close = now.replace(
        hour=15,
        minute=30,
        second=0,
        microsecond=0
    )

    if market_open <= now <= market_close:
        return "OPEN"

    return "CLOSED"


# ============================================================
# 11. NEWS
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_news(symbol):

    if GNews is None:
        return []

    try:
        google_news = GNews(
            language="en",
            country="IN",
            period="2d",
            max_results=8
        )

        results = google_news.get_news(
            f"{symbol} stock India NSE"
        )

        return results or []

    except Exception:
        return []


# ============================================================
# 12. THEMATIC ENGINE
# ============================================================

THEMES = {
    "Artificial Intelligence": [
        "artificial intelligence",
        "ai",
        "machine learning",
        "data center",
        "cloud"
    ],

    "Robotics & Automation": [
        "robot",
        "robotics",
        "automation",
        "industrial automation"
    ],

    "Defence": [
        "defence",
        "defense",
        "missile",
        "drone",
        "military"
    ],

    "Renewables": [
        "solar",
        "wind",
        "renewable",
        "green energy",
        "battery"
    ],

    "Electric Vehicles": [
        "electric vehicle",
        "ev",
        "battery",
        "charging"
    ],

    "Semiconductors": [
        "semiconductor",
        "chip",
        "fab",
        "electronics"
    ],

    "Railways": [
        "railway",
        "rail",
        "metro"
    ],

    "Infrastructure": [
        "infrastructure",
        "construction",
        "roads",
        "highway",
        "capital expenditure"
    ],
}


def detect_themes(news):

    detected = []

    text = " ".join(
        [
            str(x.get("title", "")) + " " +
            str(x.get("description", ""))
            for x in news
        ]
    ).lower()

    for theme, keywords in THEMES.items():

        matches = sum(
            1 for keyword in keywords
            if keyword in text
        )

        if matches:
            detected.append(theme)

    return detected


# ============================================================
# 13. FUNDAMENTAL DATA
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def get_fundamentals(symbol):

    ticker_symbol = STOCKS.get(symbol, symbol)

    try:

        ticker = yf.Ticker(ticker_symbol)

        info = ticker.info

        return {
            "Market Cap": info.get("marketCap"),
            "PE": info.get("trailingPE"),
            "Forward PE": info.get("forwardPE"),
            "EPS": info.get("trailingEps"),
            "ROE": info.get("returnOnEquity"),
            "Profit Margin": info.get("profitMargins"),
            "Revenue Growth": info.get("revenueGrowth"),
            "Debt/Equity": info.get("debtToEquity"),
            "52W High": info.get("fiftyTwoWeekHigh"),
            "52W Low": info.get("fiftyTwoWeekLow"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
        }

    except Exception:
        return {}


# ============================================================
# 14. DETERMINISTIC SCANNER
# ============================================================

def scan_stock(symbol):

    df = get_market_data(symbol, period="3mo")

    if df.empty or len(df) < 55:
        return None

    df = calculate_indicators(df)

    row = df.iloc[-1]

    price = float(row["Close"])

    signal = get_signal(row)

    score = 0

    if row["EMA9"] > row["EMA21"]:
        score += 20

    if price > row["SMA20"]:
        score += 20

    if price > row["SMA50"]:
        score += 20

    if 50 <= row["RSI"] <= 70:
        score += 20

    if row["VolumeRatio"] >= 1.2:
        score += 20

    return {
        "Symbol": symbol,
        "Price": round(price, 2),
        "1D %": round(float(row["Return1D"]), 2),
        "5D %": round(float(row["Return5D"]), 2),
        "RSI": round(float(row["RSI"]), 1),
        "Volume Ratio": round(float(row["VolumeRatio"]), 2),
        "Signal": signal,
        "Score": score,
    }


def run_scanner(limit=80):

    results = []

    symbols = list(STOCKS.keys())[:limit]

    progress = st.progress(0)

    for index, symbol in enumerate(symbols):

        try:

            result = scan_stock(symbol)

            if result:
                results.append(result)

        except Exception as error:
            log_event(
                f"Scanner error {symbol}: {error}"
            )

        progress.progress(
            (index + 1) / len(symbols)
        )

    progress.empty()

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)

    return result_df.sort_values(
        "Score",
        ascending=False
    )


# ============================================================
# 15. AI CACHE
# ============================================================

def load_research_cache():

    if RESEARCH_CACHE_FILE.exists():

        try:
            return json.loads(
                RESEARCH_CACHE_FILE.read_text()
            )

        except Exception:
            pass

    return {}


def save_research_cache(cache):

    RESEARCH_CACHE_FILE.write_text(
        json.dumps(
            cache,
            indent=2
        )
    )


def research_cache_key(symbol, model):

    raw = f"{symbol}|{model}|{datetime.now().strftime('%Y-%m-%d')}"

    return hashlib.sha256(
        raw.encode()
    ).hexdigest()


# ============================================================
# 16. AI DEPLOYMENT
# ============================================================

def get_ai_client():

    provider = st.session_state.ai_provider

    if provider == "Local":

        if OpenAI is None:
            return None

        endpoint = st.session_state.ai_endpoint

        return OpenAI(
            base_url=endpoint,
            api_key=os.getenv(
                "LOCAL_LLM_API_KEY",
                "local"
            )
        )

    if provider == "Groq":

        if Groq is None:
            return None

        api_key = st.session_state.get(
            "groq_api_key",
            ""
        )

        if not api_key:
            api_key = os.getenv(
                "GROQ_API_KEY",
                ""
            )

        if not api_key:
            return None

        return Groq(
            api_key=api_key
        )

    return None


def call_ai(prompt):

    if not st.session_state.ai_enabled:
        return None

    client = get_ai_client()

    if client is None:
        return None

    provider = st.session_state.ai_provider
    model = st.session_state.ai_model

    try:

        if provider == "Local":

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an institutional equity "
                            "research assistant. "
                            "Do not invent market data. "
                            "Clearly separate facts, "
                            "analysis and uncertainty."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=st.session_state.ai_temperature,
                max_tokens=st.session_state.ai_max_tokens
            )

        else:

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an institutional equity "
                            "research assistant. "
                            "Do not invent market data."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=st.session_state.ai_temperature,
                max_tokens=st.session_state.ai_max_tokens
            )

        return response.choices[0].message.content

    except Exception as error:

        log_event(
            f"AI error: {error}"
        )

        return f"AI ERROR: {error}"


# ============================================================
# 17. STOCK RESEARCH ENGINE
# ============================================================

def build_research_package(symbol):

    df = get_market_data(
        symbol,
        period="1y"
    )

    if df.empty:
        return None

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    fundamentals = get_fundamentals(symbol)

    news = get_news(symbol)

    themes = detect_themes(news)

    package = {

        "symbol": symbol,

        "price": round(
            float(latest["Close"]),
            2
        ),

        "change_1d": round(
            float(latest["Return1D"]),
            2
        ),

        "change_5d": round(
            float(latest["Return5D"]),
            2
        ),

        "rsi": round(
            float(latest["RSI"]),
            2
        ),

        "atr": round(
            float(latest["ATR"]),
            2
        ),

        "volume_ratio": round(
            float(latest["VolumeRatio"]),
            2
        ),

        "ema9": round(
            float(latest["EMA9"]),
            2
        ),

        "ema21": round(
            float(latest["EMA21"]),
            2
        ),

        "sma20": round(
            float(latest["SMA20"]),
            2
        ),

        "sma50": round(
            float(latest["SMA50"]),
            2
        ),

        "signal": get_signal(latest),

        "fundamentals": fundamentals,

        "themes": themes,

        "news": [
            {
                "title": item.get("title"),
                "publisher": (
                    item.get(
                        "publisher",
                        {}
                    ).get(
                        "title",
                        "Unknown"
                    )
                    if isinstance(
                        item.get("publisher"),
                        dict
                    )
                    else str(
                        item.get(
                            "publisher",
                            "Unknown"
                        )
                    )
                ),
                "description": item.get(
                    "description",
                    ""
                )
            }
            for item in news
        ],
    }

    return package


def generate_quick_research(package):

    price = package["price"]
    rsi = package["rsi"]
    signal = package["signal"]

    if signal == "BULLISH":
        structure = (
            "Price structure is currently "
            "bullish under the deterministic "
            "technical model."
        )

    elif signal == "BEARISH":
        structure = (
            "Price structure is currently "
            "bearish under the deterministic "
            "technical model."
        )

    else:
        structure = (
            "Price structure is mixed and "
            "does not meet the deterministic "
            "trend threshold."
        )

    return {
        "summary": structure,
        "price": price,
        "rsi": rsi,
        "signal": signal,
        "themes": package["themes"],
        "technical": {
            "EMA9": package["ema9"],
            "EMA21": package["ema21"],
            "SMA20": package["sma20"],
            "SMA50": package["sma50"],
            "ATR": package["atr"],
            "Volume Ratio": package["volume_ratio"],
        }
    }


# ============================================================
# 18. AI DEEP RESEARCH
# ============================================================

def generate_ai_research(package):

    symbol = package["symbol"]

    model = st.session_state.ai_model

    cache = load_research_cache()

    key = research_cache_key(
        symbol,
        model
    )

    if key in cache:

        log_event(
            f"Research cache hit: {symbol}"
        )

        return cache[key]

    fundamentals = json.dumps(
        package["fundamentals"],
        indent=2
    )

    news = json.dumps(
        package["news"][:5],
        indent=2
    )

    prompt = f"""
Research the Indian listed company {symbol}.

Use ONLY the supplied market information.
Do not invent financial figures.

TECHNICAL DATA:
Price: {package['price']}
1D Return: {package['change_1d']}%
5D Return: {package['change_5d']}%
RSI: {package['rsi']}
ATR: {package['atr']}
Volume Ratio: {package['volume_ratio']}
EMA9: {package['ema9']}
EMA21: {package['ema21']}
SMA20: {package['sma20']}
SMA50: {package['sma50']}
Model Signal: {package['signal']}

FUNDAMENTALS:
{fundamentals}

THEMES:
{package['themes']}

RECENT NEWS:
{news}

Return a concise institutional research note with:

1. Executive Summary
2. Technical Structure
3. Fundamental Snapshot
4. Catalysts
5. Risks
6. Sector/Theme Context
7. What Would Change The Thesis
8. Data Gaps / Uncertainty

Do NOT provide guaranteed returns.
Do NOT fabricate missing data.
"""

    result = call_ai(prompt)

    if result:

        cache[key] = result

        save_research_cache(
            cache
        )

        log_event(
            f"AI research generated: {symbol}"
        )

    return result


# ============================================================
# 19. PAPER TRADING
# ============================================================

def execute_paper_order(
    symbol,
    side,
    quantity,
    price
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    row = {
        "timestamp": timestamp,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "value": quantity * price,
        "mode": "PAPER",
    }

    df = pd.DataFrame([row])

    if PAPER_ORDERS_FILE.exists():

        old = pd.read_csv(
            PAPER_ORDERS_FILE
        )

        df = pd.concat(
            [old, df],
            ignore_index=True
        )

    df.to_csv(
        PAPER_ORDERS_FILE,
        index=False
    )

    log_event(
        f"PAPER ORDER {side} "
        f"{quantity} {symbol} @ {price}"
    )


def load_orders():

    if not PAPER_ORDERS_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(
            PAPER_ORDERS_FILE
        )
    except Exception:
        return pd.DataFrame()


# ============================================================
# 20. HEADER
# ============================================================

def render_header():

    status = market_status()

    status_class = (
        "status-open"
        if status == "OPEN"
        else "status-closed"
    )

    st.markdown(
        f"""
        <div class="terminal-header">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

        <div>
            <div class="main-title">
                OMNITRIX TERMINAL
            </div>

            <div class="sub-title">
                INDIAN EQUITIES • CASH MARKET • RESEARCH & PAPER EXECUTION
            </div>
        </div>

        <div style="
            display:flex;
            gap:30px;
            align-items:center;
        ">

        <div>
            <span class="{status_class}">
                ● {status}
            </span>
        </div>

        <div>
            <span style="color:#8d98a4;">
                MODE
            </span>
            <br>
            <b style="color:#ffffff;">
                PAPER
            </b>
        </div>

        <div>
            <span style="color:#8d98a4;">
                ASSET
            </span>
            <br>
            <b style="color:#ffffff;">
                NSE / BSE
            </b>
        </div>

        </div>

        </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 21. SIDEBAR NAVIGATION
# ============================================================

def navigation():

    st.sidebar.markdown(
        """
        <div style="
            font-size:19px;
            font-weight:700;
            margin-bottom:3px;
        ">
        OMNITRIX
        </div>

        <div style="
            color:#7f8b96;
            font-size:10px;
            letter-spacing:1px;
            margin-bottom:18px;
        ">
        INSTITUTIONAL TERMINAL
        </div>
        """,
        unsafe_allow_html=True
    )

    groups = {
        "MARKETS": [
            "Overview",
            "Markets",
            "Scanner",
            "Stock Research",
            "Watchlist",
            "News",
            "Themes",
            "IPOs",
        ],

        "TRADING": [
            "Portfolio",
            "Positions",
            "Orders",
            "Paper Trading",
            "Trade Journal",
            "Risk",
        ],

        "AI": [
            "AI Deployment",
            "AI Research",
            "Strategy Lab",
            "Backtesting",
        ],

        "SYSTEM": [
            "System Logs",
            "Settings",
        ],
    }

    for group, pages in groups.items():

        st.sidebar.markdown(
            f"""
            <div style="
                color:#66727e;
                font-size:10px;
                font-weight:700;
                letter-spacing:1px;
                margin-top:13px;
                margin-bottom:5px;
            ">
            {group}
            </div>
            """,
            unsafe_allow_html=True
        )

        for page in pages:

            active = (
                page ==
                st.session_state.page
            )

            label = (
                f"●  {page}"
                if active
                else page
            )

            if st.sidebar.button(
                label,
                key=f"nav_{page}",
                use_container_width=True
            ):

                st.session_state.page = page

                st.rerun()


# ============================================================
# 22. OVERVIEW
# ============================================================

def page_overview():

    st.markdown(
        '<div class="section">MARKET OVERVIEW</div>',
        unsafe_allow_html=True
    )

    nifty = get_market_data(
        "^NSEI",
        period="5d"
    )

    banknifty = get_market_data(
        "^NSEBANK",
        period="5d"
    )

    cols = st.columns(4)

    if not nifty.empty:

        price = float(
            nifty["Close"].iloc[-1]
        )

        change = (
            nifty["Close"].pct_change().iloc[-1]
            * 100
        )

        cols[0].metric(
            "NIFTY 50",
            f"₹{price:,.2f}",
            f"{change:+.2f}%"
        )

    if not banknifty.empty:

        price = float(
            banknifty["Close"].iloc[-1]
        )

        change = (
            banknifty["Close"].pct_change().iloc[-1]
            * 100
        )

        cols[1].metric(
            "BANK NIFTY",
            f"₹{price:,.2f}",
            f"{change:+.2f}%"
        )

    cols[2].metric(
        "WATCHLIST",
        len(st.session_state.watchlist)
    )

    cols[3].metric(
        "AI STATUS",
        "ACTIVE"
        if st.session_state.ai_enabled
        else "STANDBY"
    )

    st.markdown(
        '<div class="section">QUICK ACCESS</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    if c1.button(
        "OPEN SCANNER",
        use_container_width=True
    ):
        st.session_state.page = "Scanner"
        st.rerun()

    if c2.button(
        "STOCK RESEARCH",
        use_container_width=True
    ):
        st.session_state.page = "Stock Research"
        st.rerun()

    if c3.button(
        "AI DEPLOYMENT",
        use_container_width=True
    ):
        st.session_state.page = "AI Deployment"
        st.rerun()

    if c4.button(
        "PAPER TRADING",
        use_container_width=True
    ):
        st.session_state.page = "Paper Trading"
        st.rerun()

    st.markdown(
        '<div class="section">WATCHLIST</div>',
        unsafe_allow_html=True
    )

    rows = []

    for symbol in st.session_state.watchlist:

        df = get_market_data(
            symbol,
            period="5d"
        )

        if df.empty:
            continue

        close = df["Close"]

        rows.append({
            "Symbol": symbol,
            "Price": round(
                float(close.iloc[-1]),
                2
            ),
            "1D %": round(
                float(
                    close.pct_change().iloc[-1]
                    * 100
                ),
                2
            )
        })

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 23. MARKETS
# ============================================================

def page_markets():

    st.markdown(
        '<div class="section">MARKET MONITOR</div>',
        unsafe_allow_html=True
    )

    indices = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "NIFTY IT": "^CNXIT",
        "NIFTY AUTO": "^CNXAUTO",
        "NIFTY PHARMA": "^CNXPHARMA",
    }

    rows = []

    for name, ticker in indices.items():

        df = get_market_data(
            ticker,
            period="5d"
        )

        if df.empty:
            continue

        close = df["Close"]

        rows.append({
            "Index": name,
            "Last": round(
                float(close.iloc[-1]),
                2
            ),
            "1D %": round(
                float(
                    close.pct_change().iloc[-1]
                    * 100
                ),
                2
            )
        })

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 24. SCANNER
# ============================================================

def page_scanner():

    st.markdown(
        '<div class="section">EQUITY SCANNER</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Deterministic screening runs first. "
        "AI is only applied after candidates are shortlisted."
    )

    c1, c2, c3 = st.columns(3)

    universe_size = c1.selectbox(
        "Universe",
        [50, 80, len(STOCKS)],
        index=1
    )

    min_score = c2.slider(
        "Minimum Technical Score",
        0,
        100,
        40,
        10
    )

    ai_shortlist = c3.checkbox(
        "AI shortlist after scan",
        value=False
    )

    if st.button(
        "RUN MARKET SCAN",
        use_container_width=True
    ):

        with st.spinner(
            "Scanning equity universe..."
        ):

            result = run_scanner(
                universe_size
            )

        result = result[
            result["Score"] >= min_score
        ]

        st.session_state.scanner_result = result

        log_event(
            f"Scanner completed: "
            f"{len(result)} candidates"
        )

    result = st.session_state.scanner_result

    if result is None:
        st.info(
            "Run the scanner to generate candidates."
        )
        return

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

    if ai_shortlist and not result.empty:

        if not st.session_state.ai_enabled:

            st.warning(
                "AI is disabled. Enable it from "
                "AI Deployment."
            )

        else:

            candidates = result.head(10)

            prompt = f"""
Review these technically shortlisted Indian
equities.

Do not invent data.

Candidates:
{candidates.to_json(orient="records")}

Return:

SYMBOL
RESEARCH PRIORITY
REASON
RISK FLAG

Do not issue automatic orders.
"""

            ai_result = call_ai(prompt)

            st.markdown(
                '<div class="section">AI SHORTLIST</div>',
                unsafe_allow_html=True
            )

            st.write(ai_result)


# ============================================================
# 25. STOCK RESEARCH
# ============================================================

def page_stock_research():

    st.markdown(
        '<div class="section">STOCK RESEARCH WORKSPACE</div>',
        unsafe_allow_html=True
    )

    symbols = list(STOCKS.keys())

    selected = st.selectbox(
        "Search Indian Equity",
        symbols,
        index=symbols.index(
            st.session_state.selected_stock
        )
        if st.session_state.selected_stock
        in symbols
        else 0
    )

    st.session_state.selected_stock = selected

    c1, c2, c3 = st.columns(3)

    if c1.button(
        "LOAD RESEARCH",
        use_container_width=True
    ):

        with st.spinner(
            "Loading market data..."
        ):

            package = build_research_package(
                selected
            )

        st.session_state.research_result = package

        log_event(
            f"Research loaded: {selected}"
        )

    if c2.button(
        "GENERATE AI DEEP RESEARCH",
        use_container_width=True
    ):

        if not st.session_state.ai_enabled:

            st.warning(
                "Enable AI Deployment first."
            )

        else:

            package = (
                st.session_state.research_result
            )

            if package is None:

                package = build_research_package(
                    selected
                )

                st.session_state.research_result = package

            with st.spinner(
                "Generating research..."
            ):

                result = generate_ai_research(
                    package
                )

            st.session_state.ai_research = result

    if c3.button(
        "ADD TO WATCHLIST",
        use_container_width=True
    ):

        if selected not in st.session_state.watchlist:

            st.session_state.watchlist.append(
                selected
            )

            save_watchlist()

            st.success(
                f"{selected} added."
            )

    package = st.session_state.research_result

    if package is None:

        st.info(
            "Load a stock to open the research workspace."
        )

        return

    price_cols = st.columns(5)

    price_cols[0].metric(
        "PRICE",
        f"₹{package['price']:,.2f}",
        f"{package['change_1d']:+.2f}%"
    )

    price_cols[1].metric(
        "5D RETURN",
        f"{package['change_5d']:+.2f}%"
    )

    price_cols[2].metric(
        "RSI",
        f"{package['rsi']:.1f}"
    )

    price_cols[3].metric(
        "VOLUME RATIO",
        f"{package['volume_ratio']:.2f}x"
    )

    price_cols[4].metric(
        "MODEL SIGNAL",
        package["signal"]
    )

    df = get_market_data(
        selected,
        period="1y"
    )

    if not df.empty:

        st.markdown(
            '<div class="section">PRICE STRUCTURE</div>',
            unsafe_allow_html=True
        )

        st.line_chart(
            df["Close"],
            height=330
        )

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="section">TECHNICAL STRUCTURE</div>',
            unsafe_allow_html=True
        )

        technical = pd.DataFrame({
            "Metric": [
                "EMA 9",
                "EMA 21",
                "SMA 20",
                "SMA 50",
                "ATR",
                "RSI",
                "Volume Ratio"
            ],

            "Value": [
                package["ema9"],
                package["ema21"],
                package["sma20"],
                package["sma50"],
                package["atr"],
                package["rsi"],
                package["volume_ratio"]
            ]
        })

        st.dataframe(
            technical,
            use_container_width=True,
            hide_index=True
        )

    with right:

        st.markdown(
            '<div class="section">FUNDAMENTALS</div>',
            unsafe_allow_html=True
        )

        fundamentals = package["fundamentals"]

        fundamental_rows = []

        for key, value in fundamentals.items():

            if value is None:
                continue

            if isinstance(value, float):
                value = round(
                    value,
                    3
                )

            fundamental_rows.append({
                "Metric": key,
                "Value": value
            })

        if fundamental_rows:

            st.dataframe(
                pd.DataFrame(
                    fundamental_rows
                ),
                use_container_width=True,
                hide_index=True
            )

    st.markdown(
        '<div class="section">THEMES</div>',
        unsafe_allow_html=True
    )

    if package["themes"]:

        st.write(
            " • ".join(
                package["themes"]
            )
        )

    else:

        st.caption(
            "No tracked themes detected."
        )

    st.markdown(
        '<div class="section">RECENT NEWS</div>',
        unsafe_allow_html=True
    )

    for article in package["news"]:

        st.markdown(
            f"**{article['title']}**"
        )

        st.caption(
            f"{article['publisher']} — "
            f"{article['description']}"
        )

    quick = generate_quick_research(
        package
    )

    st.markdown(
        '<div class="section">QUICK RESEARCH</div>',
        unsafe_allow_html=True
    )

    st.write(
        quick["summary"]
    )

    if "ai_research" in st.session_state:

        st.markdown(
            '<div class="section">AI DEEP RESEARCH</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            st.session_state.ai_research
        )


# ============================================================
# 26. WATCHLIST
# ============================================================

def page_watchlist():

    st.markdown(
        '<div class="section">WATCHLIST</div>',
        unsafe_allow_html=True
    )

    symbol = st.selectbox(
        "Add security",
        list(STOCKS.keys())
    )

    if st.button(
        "ADD SECURITY",
        use_container_width=True
    ):

        if symbol not in st.session_state.watchlist:

            st.session_state.watchlist.append(
                symbol
            )

            save_watchlist()

            st.success(
                f"{symbol} added."
            )

    rows = []

    for symbol in st.session_state.watchlist:

        df = get_market_data(
            symbol,
            period="5d"
        )

        if df.empty:
            continue

        close = df["Close"]

        rows.append({
            "Symbol": symbol,
            "Price": round(
                float(close.iloc[-1]),
                2
            ),
            "1D %": round(
                float(
                    close.pct_change().iloc[-1]
                    * 100
                ),
                2
            )
        })

    if rows:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 27. NEWS
# ============================================================

def page_news():

    st.markdown(
        '<div class="section">MARKET NEWS MONITOR</div>',
        unsafe_allow_html=True
    )

    symbol = st.selectbox(
        "Security",
        list(STOCKS.keys())
    )

    news = get_news(symbol)

    if not news:

        st.info(
            "No news available."
        )

        return

    for item in news:

        title = item.get(
            "title",
            "Untitled"
        )

        publisher = item.get(
            "publisher",
            {}
        )

        if isinstance(
            publisher,
            dict
        ):

            publisher = publisher.get(
                "title",
                "Unknown"
            )

        st.markdown(
            f"**{title}**"
        )

        st.caption(
            f"{publisher} | "
            f"{item.get('description', '')}"
        )


# ============================================================
# 28. THEMES
# ============================================================

def page_themes():

    st.markdown(
        '<div class="section">MARKET THEMES</div>',
        unsafe_allow_html=True
    )

    theme_rows = []

    for theme, keywords in THEMES.items():

        theme_rows.append({
            "Theme": theme,
            "Tracked Keywords": ", ".join(
                keywords
            ),
            "Status": "MONITOR"
        })

    st.dataframe(
        pd.DataFrame(theme_rows),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 29. IPO CENTER
# ============================================================

def page_ipos():

    st.markdown(
        '<div class="section">IPO CENTER</div>',
        unsafe_allow_html=True
    )

    st.info(
        "IPO intelligence module is isolated from "
        "the live trading engine. A verified IPO data "
        "provider can be connected here in the next phase."
    )

    st.write(
        "Planned fields:"
    )

    st.write(
        "- IPO name\n"
        "- Issue price\n"
        "- Subscription data\n"
        "- GMP / unofficial data where available\n"
        "- Anchor investors\n"
        "- Financial metrics\n"
        "- Sector\n"
        "- Listing date\n"
        "- AI research"
    )


# ============================================================
# 30. PAPER TRADING
# ============================================================

def page_paper_trading():

    st.markdown(
        '<div class="section">PAPER EXECUTION</div>',
        unsafe_allow_html=True
    )

    st.warning(
        "PAPER MODE ONLY. No broker order is being sent."
    )

    c1, c2, c3 = st.columns(3)

    symbol = c1.selectbox(
        "Security",
        list(STOCKS.keys())
    )

    side = c2.selectbox(
        "Side",
        ["BUY", "SELL"]
    )

    quantity = c3.number_input(
        "Quantity",
        min_value=1,
        value=1
    )

    df = get_market_data(
        symbol,
        period="5d"
    )

    if df.empty:
        return

    price = float(
        df["Close"].iloc[-1]
    )

    st.metric(
        "Reference Price",
        f"₹{price:,.2f}"
    )

    if st.button(
        "SUBMIT PAPER ORDER",
        use_container_width=True
    ):

        execute_paper_order(
            symbol,
            side,
            int(quantity),
            price
        )

        st.success(
            f"PAPER {side} order recorded."
        )

    orders = load_orders()

    if not orders.empty:

        st.markdown(
            '<div class="section">ORDER HISTORY</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            orders.tail(50),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 31. ORDERS
# ============================================================

def page_orders():

    st.markdown(
        '<div class="section">ORDER MANAGEMENT</div>',
        unsafe_allow_html=True
    )

    orders = load_orders()

    if orders.empty:

        st.info(
            "No paper orders."
        )

    else:

        st.dataframe(
            orders,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 32. POSITIONS
# ============================================================

def page_positions():

    st.markdown(
        '<div class="section">POSITIONS</div>',
        unsafe_allow_html=True
    )

    orders = load_orders()

    if orders.empty:

        st.info(
            "No paper positions."
        )

        return

    positions = {}

    for _, row in orders.iterrows():

        symbol = row["symbol"]

        if symbol not in positions:
            positions[symbol] = 0

        if row["side"] == "BUY":
            positions[symbol] += row["quantity"]
        else:
            positions[symbol] -= row["quantity"]

    rows = []

    for symbol, quantity in positions.items():

        if quantity == 0:
            continue

        df = get_market_data(
            symbol,
            period="5d"
        )

        if df.empty:
            continue

        price = float(
            df["Close"].iloc[-1]
        )

        rows.append({
            "Symbol": symbol,
            "Quantity": quantity,
            "Last Price": round(
                price,
                2
            )
        })

    if rows:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 33. PORTFOLIO
# ============================================================

def page_portfolio():

    st.markdown(
        '<div class="section">PORTFOLIO</div>',
        unsafe_allow_html=True
    )

    st.metric(
        "Execution Mode",
        "PAPER"
    )

    st.metric(
        "Live Broker Connection",
        "DISABLED"
    )

    st.info(
        "Broker connectivity will be introduced only "
        "after the research, risk and paper-execution "
        "layers are stable."
    )


# ============================================================
# 34. RISK
# ============================================================

def page_risk():

    st.markdown(
        '<div class="section">RISK CONTROL CENTER</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    max_daily_loss = c1.number_input(
        "Maximum Daily Loss (₹)",
        min_value=1000,
        value=10000
    )

    max_position_size = c2.number_input(
        "Maximum Position Value (₹)",
        min_value=1000,
        value=100000
    )

    max_trades = c3.number_input(
        "Maximum Trades / Day",
        min_value=1,
        value=10
    )

    st.markdown(
        '<div class="section">HARD RULES</div>',
        unsafe_allow_html=True
    )

    rules = [
        "Cash equities only",
        "No F&O",
        "No order without risk validation",
        "AI cannot directly place orders",
        "Paper trading before live trading",
        "Maximum daily loss stops execution",
        "Position size must pass risk engine",
        "System must record every order",
    ]

    for rule in rules:
        st.write(
            f"• {rule}"
        )


# ============================================================
# 35. AI DEPLOYMENT CENTER
# ============================================================

def page_ai_deployment():

    st.markdown(
        '<div class="section">AI DEPLOYMENT CENTER</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "AI Deployment controls the model layer. "
        "It does not grant direct order authority."
    )

    provider = st.selectbox(
        "AI Provider",
        ["Local", "Groq"],
        index=(
            0
            if st.session_state.ai_provider == "Local"
            else 1
        )
    )

    st.session_state.ai_provider = provider

    if provider == "Local":

        endpoint = st.text_input(
            "OpenAI-Compatible Local Endpoint",
            value=st.session_state.ai_endpoint
        )

        model = st.text_input(
            "Local Model Name",
            value=st.session_state.ai_model
        )

        st.session_state.ai_endpoint = endpoint
        st.session_state.ai_model = model

        st.info(
            "Use your local model server's OpenAI-compatible "
            "endpoint. The default shown is suitable for "
            "an Ollama-style local endpoint."
        )

    else:

        api_key = st.text_input(
            "Groq API Key",
            value=os.getenv(
                "GROQ_API_KEY",
                ""
            ),
            type="password"
        )

        model = st.text_input(
            "Groq Model",
            value=(
                st.session_state.ai_model
                or "openai/gpt-oss-20b"
            )
        )

        st.session_state.groq_api_key = api_key
        st.session_state.ai_model = model

    st.markdown(
        '<div class="section">MODEL PARAMETERS</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    temperature = c1.slider(
        "Temperature",
        0.0,
        1.0,
        float(
            st.session_state.ai_temperature
        ),
        0.05
    )

    max_tokens = c2.number_input(
        "Maximum Output Tokens",
        min_value=200,
        max_value=5000,
        value=int(
            st.session_state.ai_max_tokens
        )
    )

    st.session_state.ai_temperature = temperature
    st.session_state.ai_max_tokens = max_tokens

    st.markdown(
        '<div class="section">AI SERVICES</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    research_ai = c1.checkbox(
        "Research AI",
        value=True
    )

    scanner_ai = c2.checkbox(
        "Scanner AI",
        value=False
    )

    news_ai = c3.checkbox(
        "News AI",
        value=False
    )

    strategy_ai = c4.checkbox(
        "Strategy AI",
        value=False
    )

    st.markdown(
        '<div class="section">DEPLOYMENT CONTROL</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    if c1.button(
        "TEST AI CONNECTION",
        use_container_width=True
    ):

        previous = st.session_state.ai_enabled

        st.session_state.ai_enabled = True

        response = call_ai(
            "Reply only with: OMNITRIX AI CONNECTION OK"
        )

        st.session_state.ai_enabled = previous

        if response:
            st.success(
                response
            )
        else:
            st.error(
                "AI connection failed."
            )

    if c2.button(
        "START AI SERVICES",
        use_container_width=True
    ):

        st.session_state.ai_enabled = True

        log_event(
            "AI services enabled"
        )

        st.success(
            "AI services enabled."
        )

    if c3.button(
        "STOP AI SERVICES",
        use_container_width=True
    ):

        st.session_state.ai_enabled = False

        log_event(
            "AI services disabled"
        )

        st.warning(
            "AI services stopped."
        )

    status = (
        "ACTIVE"
        if st.session_state.ai_enabled
        else "STANDBY"
    )

    st.metric(
        "AI SERVICE STATUS",
        status
    )

    st.markdown(
        '<div class="section">AI ARCHITECTURE</div>',
        unsafe_allow_html=True
    )

    architecture = pd.DataFrame([
        {
            "Agent": "Stock Researcher",
            "Status": "ON",
            "Usage": "On demand"
        },
        {
            "Agent": "Scanner Analyst",
            "Status": "OPTIONAL",
            "Usage": "Shortlist only"
        },
        {
            "Agent": "News Analyst",
            "Status": "OPTIONAL",
            "Usage": "Selected events"
        },
        {
            "Agent": "Strategy Analyst",
            "Status": "OPTIONAL",
            "Usage": "Validation"
        },
        {
            "Agent": "Risk Engine",
            "Status": "ALWAYS ON",
            "Usage": "Deterministic"
        },
        {
            "Agent": "Execution",
            "Status": "PAPER",
            "Usage": "No live orders"
        },
    ])

    st.dataframe(
        architecture,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 36. AI RESEARCH
# ============================================================

def page_ai_research():

    st.markdown(
        '<div class="section">AI RESEARCH DESK</div>',
        unsafe_allow_html=True
    )

    st.write(
        "This workspace is deliberately separated "
        "from Stock Research."
    )

    st.write(
        "Stock Research = factual market workspace."
    )

    st.write(
        "AI Research = optional reasoning layer."
    )

    if not st.session_state.ai_enabled:

        st.warning(
            "AI services are currently in standby."
        )

        return

    symbol = st.selectbox(
        "Research Security",
        list(STOCKS.keys())
    )

    if st.button(
        "RUN AI RESEARCH",
        use_container_width=True
    ):

        package = build_research_package(
            symbol
        )

        with st.spinner(
            "AI research running..."
        ):

            result = generate_ai_research(
                package
            )

        st.markdown(
            result
        )


# ============================================================
# 37. STRATEGY LAB
# ============================================================

def page_strategy():

    st.markdown(
        '<div class="section">STRATEGY LAB</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Strategy logic will remain deterministic and "
        "version-controlled. AI can propose or analyze "
        "strategies, but the rule engine remains the authority."
    )

    strategy = st.selectbox(
        "Strategy",
        [
            "Trend + Momentum",
            "EMA Cross",
            "Breakout + Volume",
            "Mean Reversion",
            "Custom Master Trader Rules"
        ]
    )

    st.write(
        f"Selected strategy: **{strategy}**"
    )


# ============================================================
# 38. BACKTESTING
# ============================================================

def page_backtesting():

    st.markdown(
        '<div class="section">BACKTESTING LAB</div>',
        unsafe_allow_html=True
    )

    symbol = st.selectbox(
        "Security",
        list(STOCKS.keys())
    )

    df = get_market_data(
        symbol,
        period="2y"
    )

    if df.empty:

        st.warning(
            "Historical data unavailable."
        )

        return

    df = calculate_indicators(
        df
    )

    df["Strategy"] = np.where(
        (
            (df["EMA9"] > df["EMA21"]) &
            (df["RSI"] > 50)
        ),
        1,
        0
    )

    df["MarketReturn"] = (
        df["Close"].pct_change()
    )

    df["StrategyReturn"] = (
        df["MarketReturn"] *
        df["Strategy"].shift(1)
    )

    equity = (
        1 +
        df["StrategyReturn"].fillna(0)
    ).cumprod()

    st.metric(
        "Strategy Growth",
        f"{(equity.iloc[-1] - 1) * 100:.2f}%"
    )

    st.line_chart(
        equity,
        height=350
    )


# ============================================================
# 39. TRADE JOURNAL
# ============================================================

def page_journal():

    st.markdown(
        '<div class="section">TRADE JOURNAL</div>',
        unsafe_allow_html=True
    )

    symbol = st.selectbox(
        "Security",
        list(STOCKS.keys())
    )

    notes = st.text_area(
        "Trade Notes"
    )

    if st.button(
        "SAVE JOURNAL ENTRY",
        use_container_width=True
    ):

        row = pd.DataFrame([{
            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            "symbol": symbol,
            "notes": notes,
        }])

        if JOURNAL_FILE.exists():

            old = pd.read_csv(
                JOURNAL_FILE
            )

            row = pd.concat(
                [old, row],
                ignore_index=True
            )

        row.to_csv(
            JOURNAL_FILE,
            index=False
        )

        st.success(
            "Journal entry saved."
        )

    if JOURNAL_FILE.exists():

        st.dataframe(
            pd.read_csv(
                JOURNAL_FILE
            ),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 40. SYSTEM LOGS
# ============================================================

def page_logs():

    st.markdown(
        '<div class="section">SYSTEM LOGS</div>',
        unsafe_allow_html=True
    )

    if st.session_state.system_logs:

        for log in reversed(
            st.session_state.system_logs
        ):

            st.code(
                log,
                language=None
            )

    else:

        st.info(
            "No session logs."
        )


# ============================================================
# 41. SETTINGS
# ============================================================

def page_settings():

    st.markdown(
        '<div class="section">SYSTEM SETTINGS</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Execution Mode"
    )

    st.selectbox(
        "Mode",
        [
            "PAPER — ACTIVE",
            "LIVE — DISABLED"
        ]
    )

    st.write(
        "Market"
    )

    st.selectbox(
        "Exchange",
        [
            "NSE",
            "BSE",
            "NSE + BSE"
        ]
    )

    st.write(
        "Asset Class"
    )

    st.info(
        "Cash Equities only. "
        "F&O is disabled in this build."
    )

    if st.button(
        "CLEAR RESEARCH CACHE",
        use_container_width=True
    ):

        try:

            RESEARCH_CACHE_FILE.unlink(
                missing_ok=True
            )

            st.success(
                "Research cache cleared."
            )

        except Exception as error:

            st.error(
                str(error)
            )


# ============================================================
# 42. ROUTER
# ============================================================

navigation()

render_header()

page = st.session_state.page


if page == "Overview":
    page_overview()

elif page == "Markets":
    page_markets()

elif page == "Scanner":
    page_scanner()

elif page == "Stock Research":
    page_stock_research()

elif page == "Watchlist":
    page_watchlist()

elif page == "News":
    page_news()

elif page == "Themes":
    page_themes()

elif page == "IPOs":
    page_ipos()

elif page == "Portfolio":
    page_portfolio()

elif page == "Positions":
    page_positions()

elif page == "Orders":
    page_orders()

elif page == "Paper Trading":
    page_paper_trading()

elif page == "Risk":
    page_risk()

elif page == "AI Deployment":
    page_ai_deployment()

elif page == "AI Research":
    page_ai_research()

elif page == "Strategy Lab":
    page_strategy()

elif page == "Backtesting":
    page_backtesting()

elif page == "Trade Journal":
    page_journal()

elif page == "System Logs":
    page_logs()

elif page == "Settings":
    page_settings()


# ============================================================
# 43. FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        margin-top:30px;
        padding-top:10px;
        border-top:1px solid #252c34;
        color:#66727e;
        font-size:10px;
        text-align:center;
    ">
        OMNITRIX TERMINAL • LOCAL RESEARCH SYSTEM •
        CASH EQUITIES • PAPER EXECUTION
    </div>
    """,
    unsafe_allow_html=True
)
