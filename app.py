import os
import re
import json
import time
import math
import difflib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from gnews import GNews

# Optional AI imports
try:
    from groq import Groq
except ImportError:
    Groq = None


# ============================================================
# OMNITRIX AI — LOCAL INDIAN EQUITY TRADING TERMINAL
# ============================================================
# Phase 1:
#   Indian cash equities
#   Intraday/day trading
#   No F&O
#
# Architecture:
#   DATA -> SCANNER -> NEWS/THEMES -> AI -> STRATEGY -> RISK
#                                      -> PAPER EXECUTION
#
# Live broker execution is intentionally separated from the AI.
# ============================================================


APP_NAME = "OMNITRIX AI"
DATA_DIR = Path("data")
TRADE_DIR = DATA_DIR / "trades"
LOG_DIR = DATA_DIR / "logs"

for directory in [DATA_DIR, TRADE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="OMNITRIX AI — India Trading Terminal",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# OMNITRIX / BEN 10 INSPIRED UI
# ============================================================

BEN10_CSS = """
<style>

:root {
    --omni-green: #39ff14;
    --omni-dark: #071009;
    --omni-panel: #0c1710;
    --omni-border: #234b2a;
    --omni-text: #e9ffe8;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(57,255,20,0.08), transparent 25%),
        radial-gradient(circle at 85% 80%, rgba(57,255,20,0.05), transparent 30%),
        #050805;
}

[data-testid="stSidebar"] {
    background: #071009;
    border-right: 1px solid #234b2a;
}

.omni-title {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 2px;
    color: #39ff14;
    text-shadow: 0 0 12px rgba(57,255,20,0.45);
}

.omni-subtitle {
    color: #a6cfa3;
    font-size: 14px;
}

.omni-card {
    background: rgba(12,23,16,0.90);
    border: 1px solid #234b2a;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}

.signal-buy {
    color: #39ff14;
    font-weight: 900;
}

.signal-sell {
    color: #ff5555;
    font-weight: 900;
}

.signal-neutral {
    color: #ffd84d;
    font-weight: 900;
}

.small-muted {
    color: #8ca88d;
    font-size: 12px;
}

</style>
"""

st.markdown(BEN10_CSS, unsafe_allow_html=True)


# ============================================================
# INSTRUMENT MASTER
# ============================================================

# This is intentionally expandable.
# Eventually we should replace this with a complete NSE/BSE
# instrument master downloaded/imported into the local database.

INSTRUMENTS = [
    ("RELIANCE", "Reliance Industries", "RELIANCE.NS", "500325", "Energy"),
    ("TCS", "Tata Consultancy Services", "TCS.NS", "532540", "IT"),
    ("TATAMOTORS", "Tata Motors", "TATAMOTORS.NS", "500570", "Auto"),
    ("TATASTEEL", "Tata Steel", "TATASTEEL.NS", "500470", "Metals"),
    ("TATAPOWER", "Tata Power", "TATAPOWER.NS", "500400", "Power"),
    ("INFY", "Infosys", "INFY.NS", "500209", "IT"),
    ("HDFCBANK", "HDFC Bank", "HDFCBANK.NS", "500180", "Banking"),
    ("ICICIBANK", "ICICI Bank", "ICICIBANK.NS", "532174", "Banking"),
    ("SBIN", "State Bank of India", "SBIN.NS", "500112", "Banking"),
    ("AXISBANK", "Axis Bank", "AXISBANK.NS", "532215", "Banking"),
    ("KOTAKBANK", "Kotak Mahindra Bank", "KOTAKBANK.NS", "500247", "Banking"),
    ("LT", "Larsen & Toubro", "LT.NS", "500510", "Infrastructure"),
    ("BHARTIARTL", "Bharti Airtel", "BHARTIARTL.NS", "532454", "Telecom"),
    ("ITC", "ITC", "ITC.NS", "500875", "FMCG"),
    ("HINDUNILVR", "Hindustan Unilever", "HINDUNILVR.NS", "500696", "FMCG"),
    ("MARUTI", "Maruti Suzuki India", "MARUTI.NS", "532500", "Auto"),
    ("M&M", "Mahindra & Mahindra", "M&M.NS", "500520", "Auto"),
    ("SUNPHARMA", "Sun Pharmaceutical", "SUNPHARMA.NS", "524715", "Pharma"),
    ("DRREDDY", "Dr Reddy's Laboratories", "DRREDDY.NS", "500124", "Pharma"),
    ("CIPLA", "Cipla", "CIPLA.NS", "500087", "Pharma"),
    ("ADANIENT", "Adani Enterprises", "ADANIENT.NS", "512599", "Conglomerate"),
    ("ADANIPORTS", "Adani Ports", "ADANIPORTS.NS", "532921", "Infrastructure"),
    ("NTPC", "NTPC", "NTPC.NS", "532555", "Power"),
    ("POWERGRID", "Power Grid Corporation", "POWERGRID.NS", "532898", "Power"),
    ("ONGC", "Oil & Natural Gas Corporation", "ONGC.NS", "500312", "Energy"),
    ("COALINDIA", "Coal India", "COALINDIA.NS", "533278", "Mining"),
    ("BEL", "Bharat Electronics", "BEL.NS", "500049", "Defence"),
    ("HAL", "Hindustan Aeronautics", "HAL.NS", "541154", "Defence"),
    ("TRENT", "Trent", "TRENT.NS", "500251", "Retail"),
    ("ZOMATO", "Eternal / Zomato", "ZOMATO.NS", "543320", "Consumer Tech"),
    ("PAYTM", "One 97 Communications", "PAYTM.NS", "543396", "Fintech"),
    ("IRCTC", "Indian Railway Catering & Tourism", "IRCTC.NS", "542830", "Railways"),
    ("DLF", "DLF", "DLF.NS", "532868", "Real Estate"),
    ("ULTRACEMCO", "UltraTech Cement", "ULTRACEMCO.NS", "532538", "Cement"),
    ("ASIANPAINT", "Asian Paints", "ASIANPAINT.NS", "500820", "Paints"),
    ("EICHERMOT", "Eicher Motors", "EICHERMOT.NS", "505200", "Auto"),
    ("BAJFINANCE", "Bajaj Finance", "BAJFINANCE.NS", "500034", "NBFC"),
    ("BAJAJFINSV", "Bajaj Finserv", "BAJAJFINSV.NS", "532978", "Financial"),
    ("HCLTECH", "HCL Technologies", "HCLTECH.NS", "532281", "IT"),
    ("WIPRO", "Wipro", "WIPRO.NS", "507685", "IT"),
    ("TECHM", "Tech Mahindra", "TECHM.NS", "532755", "IT"),
    ("JSWSTEEL", "JSW Steel", "JSWSTEEL.NS", "500228", "Metals"),
    ("HINDALCO", "Hindalco Industries", "HINDALCO.NS", "500440", "Metals"),
    ("GRASIM", "Grasim Industries", "GRASIM.NS", "500300", "Conglomerate"),
    ("NESTLEIND", "Nestle India", "NESTLEIND.NS", "500790", "FMCG"),
    ("BRITANNIA", "Britannia Industries", "BRITANNIA.NS", "500825", "FMCG"),
    ("APOLLOHOSP", "Apollo Hospitals", "APOLLOHOSP.NS", "508869", "Healthcare"),
    ("DIVISLAB", "Divi's Laboratories", "DIVISLAB.NS", "532488", "Pharma"),
    ("TITAN", "Titan Company", "TITAN.NS", "500114", "Consumer"),
    ("HEROMOTOCO", "Hero MotoCorp", "HEROMOTOCO.NS", "500182", "Auto"),
    ("TVSMOTOR", "TVS Motor Company", "TVSMOTOR.NS", "532343", "Auto"),
    ("INDUSINDBK", "IndusInd Bank", "INDUSINDBK.NS", "532187", "Banking"),
    ("BANKBARODA", "Bank of Baroda", "BANKBARODA.NS", "532134", "Banking"),
    ("PNB", "Punjab National Bank", "PNB.NS", "532461", "Banking"),
    ("IOC", "Indian Oil Corporation", "IOC.NS", "530965", "Energy"),
    ("BPCL", "Bharat Petroleum", "BPCL.NS", "500547", "Energy"),
    ("HDFCLIFE", "HDFC Life Insurance", "HDFCLIFE.NS", "540777", "Insurance"),
    ("SBILIFE", "SBI Life Insurance", "SBILIFE.NS", "540719", "Insurance"),
    ("ICICIPRULI", "ICICI Prudential Life", "ICICIPRULI.NS", "540133", "Insurance"),
    ("DIXON", "Dixon Technologies", "DIXON.NS", "540699", "Electronics"),
    ("POLYCAB", "Polycab India", "POLYCAB.NS", "542652", "Electrical"),
    ("VOLTAS", "Voltas", "VOLTAS.NS", "500575", "Consumer"),
    ("CROMPTON", "Crompton Greaves Consumer", "CROMPTON.NS", "539876", "Consumer"),
    ("INDIGO", "InterGlobe Aviation", "INDIGO.NS", "539448", "Aviation"),
    ("ADANIGREEN", "Adani Green Energy", "ADANIGREEN.NS", "541450", "Renewable Energy"),
    ("TATACONSUM", "Tata Consumer Products", "TATACONSUM.NS", "500800", "FMCG"),
    ("PIDILITIND", "Pidilite Industries", "PIDILITIND.NS", "500331", "Chemicals"),
    ("SIEMENS", "Siemens India", "SIEMENS.NS", "500550", "Industrial"),
    ("ABB", "ABB India", "ABB.NS", "500002", "Industrial"),
    ("CUMMINSIND", "Cummins India", "CUMMINSIND.NS", "500480", "Industrial"),
    ("BHEL", "Bharat Heavy Electricals", "BHEL.NS", "500103", "Industrial"),
    ("RVNL", "Rail Vikas Nigam", "RVNL.NS", "542649", "Railways"),
    ("IRFC", "Indian Railway Finance Corporation", "IRFC.NS", "543257", "Railways"),
    ("BANDHANBNK", "Bandhan Bank", "BANDHANBNK.NS", "541153", "Banking"),
    ("IDFCFIRSTB", "IDFC First Bank", "IDFCFIRSTB.NS", "539437", "Banking"),
    ("YESBANK", "Yes Bank", "YESBANK.NS", "532648", "Banking"),
    ("CANBK", "Canara Bank", "CANBK.NS", "532483", "Banking"),
    ("TATAELXSI", "Tata Elxsi", "TATAELXSI.NS", "500408", "IT"),
    ("PERSISTENT", "Persistent Systems", "PERSISTENT.NS", "533179", "IT"),
    ("COFORGE", "Coforge", "COFORGE.NS", "532541", "IT"),
    ("LTIM", "LTIMindtree", "LTIM.NS", "540005", "IT"),
    ("MOTHERSON", "Samvardhana Motherson", "MOTHERSON.NS", "517334", "Auto"),
    ("ASHOKLEY", "Ashok Leyland", "ASHOKLEY.NS", "500477", "Auto"),
    ("BOSCHLTD", "Bosch", "BOSCHLTD.NS", "500530", "Auto"),
    ("VEDL", "Vedanta", "VEDL.NS", "500295", "Metals"),
    ("SAIL", "Steel Authority of India", "SAIL.NS", "500113", "Metals"),
    ("JINDALSTEL", "Jindal Steel", "JINDALSTEL.NS", "532286", "Metals"),
    ("NMDC", "NMDC", "NMDC.NS", "526371", "Mining"),
    ("RECLTD", "REC", "RECLTD.NS", "532955", "Financial"),
    ("PFC", "Power Finance Corporation", "PFC.NS", "532810", "Financial"),
]


INSTRUMENT_DF = pd.DataFrame(
    INSTRUMENTS,
    columns=["symbol", "name", "yf_symbol", "bse_code", "sector"]
)


# ============================================================
# SEARCH ENGINE
# ============================================================

ALIASES = {
    "tata motors": "TATAMOTORS",
    "tata motor": "TATAMOTORS",
    "tata motors ltd": "TATAMOTORS",
    "tcs": "TCS",
    "reliance": "RELIANCE",
    "hdfc": "HDFCBANK",
    "hdfc bank": "HDFCBANK",
    "icici": "ICICIBANK",
    "sbi": "SBIN",
    "state bank": "SBIN",
    "infosys": "INFY",
    "infy": "INFY",
    "zomato": "ZOMATO",
    "eternal": "ZOMATO",
    "larsen": "LT",
    "l&t": "LT",
    "mahindra": "M&M",
    "m and m": "M&M",
}


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9& ]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def search_instruments(query: str, limit: int = 10) -> pd.DataFrame:
    query_norm = normalize_text(query)

    if not query_norm:
        return INSTRUMENT_DF.head(limit)

    # Direct alias
    if query_norm in ALIASES:
        symbol = ALIASES[query_norm]
        return INSTRUMENT_DF[
            INSTRUMENT_DF["symbol"].str.upper() == symbol.upper()
        ].head(limit)

    rows = []

    for _, row in INSTRUMENT_DF.iterrows():
        symbol = normalize_text(row["symbol"])
        name = normalize_text(row["name"])
        sector = normalize_text(row["sector"])

        score = 0

        if query_norm == symbol:
            score += 100
        if query_norm == name:
            score += 100

        if name.startswith(query_norm):
            score += 80

        if symbol.startswith(query_norm):
            score += 70

        if query_norm in name:
            score += 60

        if query_norm in symbol:
            score += 50

        similarity_name = difflib.SequenceMatcher(
            None, query_norm, name
        ).ratio()

        similarity_symbol = difflib.SequenceMatcher(
            None, query_norm, symbol
        ).ratio()

        score += max(similarity_name, similarity_symbol) * 40

        if query_norm in sector:
            score += 10

        rows.append((score, row))

    rows.sort(key=lambda x: x[0], reverse=True)

    result = pd.DataFrame([r for score, r in rows[:limit]])

    return result


# ============================================================
# MARKET DATA
# ============================================================

@st.cache_data(ttl=20, show_spinner=False)
def get_history(yf_symbol: str, period="5d", interval="15m") -> pd.DataFrame:
    try:
        df = yf.download(
            yf_symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False,
        )

        if df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        return df

    except Exception:
        return pd.DataFrame()


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    result = df.copy()

    close = result["Close"]
    high = result["High"]
    low = result["Low"]
    volume = result["Volume"]

    result["SMA20"] = close.rolling(20).mean()
    result["SMA50"] = close.rolling(50).mean()

    result["EMA9"] = close.ewm(span=9, adjust=False).mean()
    result["EMA21"] = close.ewm(span=21, adjust=False).mean()

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    result["RSI"] = 100 - (100 / (1 + rs))

    result["ATR"] = (
        pd.concat(
            [
                high - low,
                (high - close.shift()).abs(),
                (low - close.shift()).abs(),
            ],
            axis=1,
        )
        .max(axis=1)
        .rolling(14)
        .mean()
    )

    result["VOL_AVG20"] = volume.rolling(20).mean()

    result["VOL_RATIO"] = (
        volume / result["VOL_AVG20"].replace(0, np.nan)
    )

    result["DAY_HIGH_20"] = high.rolling(20).max()
    result["DAY_LOW_20"] = low.rolling(20).min()

    return result


# ============================================================
# TECHNICAL SIGNAL ENGINE
# ============================================================

def analyze_symbol(row: pd.Series) -> Dict:

    yf_symbol = row["yf_symbol"]

    hist = get_history(
        yf_symbol,
        period="5d",
        interval="15m",
    )

    if hist.empty or len(hist) < 20:
        return {
            "symbol": row["symbol"],
            "name": row["name"],
            "sector": row["sector"],
            "price": np.nan,
            "change_pct": np.nan,
            "rsi": np.nan,
            "volume_ratio": np.nan,
            "trend": "DATA UNAVAILABLE",
            "signal": "NO DATA",
            "score": 0,
        }

    data = calculate_indicators(hist)

    latest = data.iloc[-1]
    previous = data.iloc[-2]

    price = float(latest["Close"])

    previous_close = float(previous["Close"])

    change_pct = (
        (price - previous_close)
        / previous_close
        * 100
    )

    rsi = float(latest["RSI"]) if not pd.isna(latest["RSI"]) else 50

    volume_ratio = (
        float(latest["VOL_RATIO"])
        if not pd.isna(latest["VOL_RATIO"])
        else 1
    )

    ema9 = float(latest["EMA9"])
    ema21 = float(latest["EMA21"])

    sma20 = (
        float(latest["SMA20"])
        if not pd.isna(latest["SMA20"])
        else price
    )

    score = 0

    # Trend
    if price > ema9 > ema21:
        trend = "BULLISH"
        score += 2
    elif price < ema9 < ema21:
        trend = "BEARISH"
        score -= 2
    else:
        trend = "SIDEWAYS"

    # RSI
    if 50 <= rsi <= 70:
        score += 1
    elif 30 <= rsi < 50:
        score -= 0.5
    elif rsi > 75:
        score -= 1

    # Volume confirmation
    if volume_ratio >= 2:
        score += 2
    elif volume_ratio >= 1.3:
        score += 1

    # Momentum
    if price > sma20:
        score += 1
    else:
        score -= 1

    if score >= 4:
        signal = "WATCH BUY"
    elif score <= -3:
        signal = "WATCH SELL"
    else:
        signal = "NEUTRAL"

    return {
        "symbol": row["symbol"],
        "name": row["name"],
        "sector": row["sector"],
        "price": round(price, 2),
        "change_pct": round(change_pct, 2),
        "rsi": round(rsi, 2),
        "volume_ratio": round(volume_ratio, 2),
        "trend": trend,
        "signal": signal,
        "score": round(score, 2),
    }


# ============================================================
# SCANNER
# ============================================================

def scan_market(universe: pd.DataFrame) -> pd.DataFrame:

    results = []

    progress = st.progress(0)

    total = len(universe)

    for i, (_, row) in enumerate(universe.iterrows()):

        result = analyze_symbol(row)

        results.append(result)

        progress.progress((i + 1) / total)

    progress.empty()

    return pd.DataFrame(results)


# ============================================================
# NEWS ENGINE
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_news(query: str, max_results: int = 10) -> List[Dict]:

    try:

        google_news = GNews(
            language="en",
            country="IN",
            period="2d",
            max_results=max_results,
        )

        return google_news.get_news(query)

    except Exception:
        return []


def news_to_text(results: List[Dict]) -> str:

    if not results:
        return "No recent news available."

    output = []

    for item in results:

        title = item.get("title", "")
        description = item.get("description", "")
        publisher = item.get("publisher", "")

        if isinstance(publisher, dict):
            publisher = publisher.get("title", "")

        output.append(
            f"Headline: {title}\n"
            f"Publisher: {publisher}\n"
            f"Description: {description}\n"
        )

    return "\n".join(output)


# ============================================================
# THEME / TREND DETECTION
# ============================================================

THEMES = {
    "Artificial Intelligence": [
        "artificial intelligence",
        "AI",
        "generative AI",
        "machine learning",
    ],
    "Robotics": [
        "robot",
        "robotics",
        "automation",
    ],
    "Defence": [
        "defence",
        "defense",
        "missile",
        "military",
    ],
    "Renewable Energy": [
        "solar",
        "renewable",
        "green energy",
        "wind power",
    ],
    "Electric Vehicles": [
        "EV",
        "electric vehicle",
        "battery",
        "charging",
    ],
    "Semiconductors": [
        "semiconductor",
        "chip",
        "fab",
        "electronics",
    ],
    "Railways": [
        "railway",
        "rail",
        "vande bharat",
    ],
    "Infrastructure": [
        "infrastructure",
        "roads",
        "highway",
        "construction",
    ],
}


def detect_themes(news_items: List[Dict]) -> pd.DataFrame:

    counts = []

    combined_text = " ".join(
        [
            f"{x.get('title', '')} {x.get('description', '')}"
            for x in news_items
        ]
    ).lower()

    for theme, keywords in THEMES.items():

        hits = 0
        matched = []

        for keyword in keywords:

            count = combined_text.count(keyword.lower())

            if count:
                hits += count
                matched.append(keyword)

        counts.append(
            {
                "Theme": theme,
                "Mentions": hits,
                "Matched Terms": ", ".join(matched),
            }
        )

    return pd.DataFrame(counts).sort_values(
        "Mentions",
        ascending=False,
    )


# ============================================================
# AI ENGINE
# ============================================================

def get_groq_client(api_key: str):

    if not Groq:
        raise RuntimeError(
            "Groq package is not installed. "
            "Run: pip install groq"
        )

    return Groq(api_key=api_key)


def ask_ai(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:

    client = get_groq_client(api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content


# ============================================================
# RISK ENGINE
# ============================================================

class RiskEngine:

    def __init__(
        self,
        max_daily_loss: float,
        max_position_value: float,
        max_trades_per_day: int,
        minimum_rr: float,
    ):

        self.max_daily_loss = max_daily_loss
        self.max_position_value = max_position_value
        self.max_trades_per_day = max_trades_per_day
        self.minimum_rr = minimum_rr

    def validate_trade(
        self,
        action: str,
        entry: float,
        stop_loss: float,
        target: float,
        quantity: int,
        current_daily_pnl: float,
        trade_count: int,
    ) -> Tuple[bool, List[str]]:

        reasons = []

        if action not in ["BUY", "SELL"]:
            reasons.append("Invalid action.")

        if entry <= 0:
            reasons.append("Invalid entry price.")

        if stop_loss <= 0 or target <= 0:
            reasons.append("Invalid stop or target.")

        if quantity <= 0:
            reasons.append("Invalid quantity.")

        position_value = entry * quantity

        if position_value > self.max_position_value:
            reasons.append("Position value exceeds limit.")

        if current_daily_pnl <= -abs(self.max_daily_loss):
            reasons.append("Daily loss limit reached.")

        if trade_count >= self.max_trades_per_day:
            reasons.append("Maximum daily trades reached.")

        risk = abs(entry - stop_loss)
        reward = abs(target - entry)

        rr = reward / risk if risk > 0 else 0

        if rr < self.minimum_rr:
            reasons.append(
                f"Risk/reward {rr:.2f} is below "
                f"required {self.minimum_rr:.2f}."
            )

        return len(reasons) == 0, reasons


# ============================================================
# PAPER EXECUTION ENGINE
# ============================================================

def load_paper_trades() -> pd.DataFrame:

    path = TRADE_DIR / "paper_trades.csv"

    if path.exists():

        try:
            return pd.read_csv(path)
        except Exception:
            pass

    return pd.DataFrame(
        columns=[
            "timestamp",
            "symbol",
            "action",
            "entry",
            "stop_loss",
            "target",
            "quantity",
            "status",
            "pnl",
        ]
    )


def save_paper_trade(trade: Dict):

    df = load_paper_trades()

    new_row = pd.DataFrame([trade])

    df = pd.concat(
        [df, new_row],
        ignore_index=True,
    )

    df.to_csv(
        TRADE_DIR / "paper_trades.csv",
        index=False,
    )


# ============================================================
# BROKER ABSTRACTION
# ============================================================

class BrokerAdapter:

    name = "Abstract Broker"

    def connect(self):
        raise NotImplementedError

    def place_equity_order(
        self,
        symbol,
        side,
        quantity,
        order_type="MARKET",
    ):
        raise NotImplementedError


class GrowwBroker(BrokerAdapter):

    name = "Groww"

    def connect(self):
        return {
            "connected": False,
            "message": (
                "Groww adapter placeholder. "
                "Connect official broker API credentials "
                "before enabling live execution."
            ),
        }


class SBISecuritiesBroker(BrokerAdapter):

    name = "SBI Securities"

    def connect(self):
        return {
            "connected": False,
            "message": (
                "SBI Securities adapter placeholder. "
                "Official API/execution integration must be "
                "implemented and verified before live trading."
            ),
        }


# ============================================================
# BACKTEST ENGINE
# ============================================================

def simple_backtest(df: pd.DataFrame) -> Dict:

    if df.empty or len(df) < 50:

        return {
            "trades": 0,
            "return_pct": 0,
            "win_rate": 0,
        }

    data = calculate_indicators(df)

    capital = 100000.0
    starting_capital = capital

    wins = 0
    trades = 0

    for i in range(1, len(data)):

        row = data.iloc[i]

        if pd.isna(row["EMA9"]) or pd.isna(row["EMA21"]):
            continue

        if row["EMA9"] > row["EMA21"] and row["RSI"] < 70:

            entry = float(row["Close"])

            exit_price = float(
                data.iloc[min(i + 3, len(data) - 1)]["Close"]
            )

            pnl = (
                (exit_price - entry)
                / entry
                * capital
                * 0.01
            )

            capital += pnl
            trades += 1

            if pnl > 0:
                wins += 1

    return {
        "trades": trades,
        "return_pct": (
            (capital - starting_capital)
            / starting_capital
            * 100
        ),
        "win_rate": (
            wins / trades * 100
            if trades
            else 0
        ),
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 👽 OMNITRIX CONTROL"
)

st.sidebar.caption(
    "Phase 1: Indian Cash Equities / Intraday"
)

groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    value=os.getenv("GROQ_API_KEY", ""),
    type="password",
)

# Current Groq model choices
selected_model = st.sidebar.selectbox(
    "AI Model",
    [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ],
    index=0,
)

st.sidebar.divider()

st.sidebar.subheader("🛡️ Risk Engine")

max_daily_loss = st.sidebar.number_input(
    "Maximum Daily Loss ₹",
    min_value=100.0,
    value=5000.0,
    step=500.0,
)

max_position_value = st.sidebar.number_input(
    "Maximum Position Value ₹",
    min_value=1000.0,
    value=100000.0,
    step=5000.0,
)

max_trades_per_day = st.sidebar.number_input(
    "Maximum Trades / Day",
    min_value=1,
    max_value=100,
    value=10,
)

minimum_rr = st.sidebar.slider(
    "Minimum Risk : Reward",
    1.0,
    5.0,
    2.0,
    0.25,
)

st.sidebar.divider()

st.sidebar.subheader("🤖 Autonomous Mode")

autonomous_mode = st.sidebar.toggle(
    "Enable Autonomous PAPER Trading",
    value=False,
)

if autonomous_mode:

    st.sidebar.warning(
        "Paper trading only. Live order execution is disabled."
    )

scan_size = st.sidebar.slider(
    "Stocks to Scan",
    min_value=10,
    max_value=100,
    value=50,
    step=10,
)

interval = st.sidebar.selectbox(
    "Market Data Interval",
    ["5m", "15m", "30m", "1h"],
    index=1,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="omni-title">👽 OMNITRIX AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="omni-subtitle">'
    "Autonomous Indian Equity Research & Paper-Trading Terminal"
    "</div>",
    unsafe_allow_html=True,
)

st.caption(
    "NSE/BSE • Cash Equity • Intraday • AI Research • "
    "Technical Scanner • News • IPO • Risk Engine"
)


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "🏠 Dashboard",
    "🔎 Market Scanner",
    "📈 Chart & Analysis",
    "📰 News & Themes",
    "🚀 IPO Center",
    "⭐ Watchlist",
    "💼 Portfolio",
    "🤖 AI Agent",
    "🛡️ Risk Management",
    "🧪 Backtesting",
    "📒 Trade Journal",
    "⚙️ Settings",
]

page = st.sidebar.radio(
    "Terminal",
    pages,
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.subheader("⚡ Market Command Center")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Scanner Universe",
        f"{scan_size} stocks",
    )

    c2.metric(
        "Trading Mode",
        "PAPER" if autonomous_mode else "MANUAL",
    )

    c3.metric(
        "Instrument Type",
        "CASH EQUITY",
    )

    c4.metric(
        "F&O",
        "DISABLED",
    )

    st.divider()

    search = st.text_input(
        "🔎 Search any Indian stock",
        placeholder="Try: tata, tata motor, reliance, sbi, infosys...",
    )

    if search:

        matches = search_instruments(
            search,
            limit=8,
        )

        st.dataframe(
            matches[
                [
                    "symbol",
                    "name",
                    "yf_symbol",
                    "bse_code",
                    "sector",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.info(
        "The search engine is local. Users do not need to enter "
        ".NS or .BO suffixes."
    )


# ============================================================
# MARKET SCANNER
# ============================================================

elif page == "🔎 Market Scanner":

    st.subheader(
        f"🔎 Market Scanner — {scan_size} Stocks"
    )

    st.caption(
        "The system analyzes many instruments programmatically. "
        "It does not need to open 100 separate visual chart windows."
    )

    universe = INSTRUMENT_DF.head(scan_size)

    if st.button(
        f"🚀 Scan {scan_size} Stocks",
        type="primary",
    ):

        with st.spinner(
            "Scanning market data..."
        ):

            scan_results = scan_market(
                universe
            )

        st.session_state["scan_results"] = scan_results

    scan_results = st.session_state.get(
        "scan_results",
        pd.DataFrame(),
    )

    if not scan_results.empty:

        st.dataframe(
            scan_results.sort_values(
                "score",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader(
            "🔥 Highest Technical Scores"
        )

        top = scan_results[
            scan_results["signal"] != "NO DATA"
        ].sort_values(
            "score",
            ascending=False,
        ).head(10)

        st.dataframe(
            top,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# CHART & ANALYSIS
# ============================================================

elif page == "📈 Chart & Analysis":

    st.subheader("📈 Chart & Technical Analysis")

    search = st.text_input(
        "Search stock",
        value="tata motor",
    )

    matches = search_instruments(
        search,
        limit=5,
    )

    if not matches.empty:

        selected_name = st.selectbox(
            "Select instrument",
            matches["name"].tolist(),
        )

        selected = matches[
            matches["name"] == selected_name
        ].iloc[0]

        hist = get_history(
            selected["yf_symbol"],
            period="1mo",
            interval=interval,
        )

        if not hist.empty:

            data = calculate_indicators(hist)

            latest = data.iloc[-1]

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Price",
                f"₹{latest['Close']:,.2f}",
            )

            c2.metric(
                "RSI",
                f"{latest['RSI']:.2f}",
            )

            c3.metric(
                "Volume Ratio",
                f"{latest['VOL_RATIO']:.2f}x",
            )

            c4.metric(
                "Trend",
                (
                    "BULLISH"
                    if latest["EMA9"] > latest["EMA21"]
                    else "BEARISH"
                ),
            )

            st.line_chart(
                data[
                    [
                        "Close",
                        "EMA9",
                        "EMA21",
                        "SMA20",
                    ]
                ]
            )

            st.subheader(
                "Technical Data"
            )

            st.dataframe(
                data.tail(50),
                use_container_width=True,
            )

        else:

            st.error(
                "No market data returned for this instrument."
            )


# ============================================================
# NEWS & THEMES
# ============================================================

elif page == "📰 News & Themes":

    st.subheader(
        "📰 Indian Market News + Theme Detection"
    )

    query = st.text_input(
        "News search",
        value="Indian stock market AI robotics IPO",
    )

    if st.button(
        "🔄 Scan News",
        type="primary",
    ):

        news = get_news(
            query,
            max_results=20,
        )

        st.session_state["news"] = news

    news = st.session_state.get(
        "news",
        [],
    )

    if news:

        for item in news:

            title = item.get(
                "title",
                "No title",
            )

            description = item.get(
                "description",
                "",
            )

            publisher = item.get(
                "publisher",
                "",
            )

            if isinstance(
                publisher,
                dict,
            ):
                publisher = publisher.get(
                    "title",
                    "",
                )

            url = item.get(
                "url",
                "#",
            )

            st.markdown(
                f"### [{title}]({url})"
            )

            st.caption(
                f"{publisher} — {description}"
            )

        st.subheader(
            "🌐 Detected Market Themes"
        )

        themes = detect_themes(
            news
        )

        st.dataframe(
            themes,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Press Scan News to collect recent market news."
        )


# ============================================================
# IPO CENTER
# ============================================================

elif page == "🚀 IPO Center":

    st.subheader(
        "🚀 IPO Intelligence Center"
    )

    st.info(
        "IPO data will be connected to verified exchange/official "
        "sources in the next module. News discovery is available now."
    )

    ipo_news = get_news(
        "India IPO NSE BSE IPO subscription listing",
        max_results=15,
    )

    if ipo_news:

        for item in ipo_news:

            st.markdown(
                f"**{item.get('title', 'IPO News')}**"
            )

            st.caption(
                item.get(
                    "description",
                    "",
                )
            )

    st.divider()

    st.subheader(
        "IPO Analysis Framework"
    )

    st.write(
        """
        The IPO engine will evaluate:

        • Issue size
        • Price band
        • Subscription
        • QIB/NII/retail participation
        • GMP as a separate non-official indicator
        • Revenue and profit growth
        • Valuation
        • Debt
        • Promoter/shareholder information
        • Sector/theme
        • Listing-day liquidity
        • Market conditions
        • Post-listing momentum
        """
    )


# ============================================================
# WATCHLIST
# ============================================================

elif page == "⭐ Watchlist":

    st.subheader("⭐ Watchlist")

    default_watchlist = [
        "RELIANCE",
        "TCS",
        "TATAMOTORS",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "INFY",
    ]

    watchlist = st.multiselect(
        "Select stocks",
        INSTRUMENT_DF["symbol"].tolist(),
        default=default_watchlist,
    )

    if watchlist:

        selected_df = INSTRUMENT_DF[
            INSTRUMENT_DF["symbol"].isin(
                watchlist
            )
        ]

        results = scan_market(
            selected_df
        )

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# PORTFOLIO
# ============================================================

elif page == "💼 Portfolio":

    st.subheader(
        "💼 Portfolio & Positions"
    )

    paper_trades = load_paper_trades()

    if paper_trades.empty:

        st.info(
            "No paper trades yet."
        )

    else:

        st.dataframe(
            paper_trades,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# AI AGENT
# ============================================================

elif page == "🤖 AI Agent":

    st.subheader(
        "🤖 Omnitrix AI Research Agent"
    )

    search = st.text_input(
        "Stock to analyze",
        value="tata motor",
    )

    matches = search_instruments(
        search,
        limit=5,
    )

    if not matches.empty:

        selected_name = st.selectbox(
            "Select stock",
            matches["name"].tolist(),
        )

        selected = matches[
            matches["name"] == selected_name
        ].iloc[0]

        if st.button(
            "🧠 RUN AI RESEARCH",
            type="primary",
        ):

            if not groq_api_key:

                st.error(
                    "Enter your Groq API key first."
                )

            else:

                hist = get_history(
                    selected["yf_symbol"],
                    period="5d",
                    interval="15m",
                )

                indicators = calculate_indicators(
                    hist
                )

                if indicators.empty:

                    st.error(
                        "Market data unavailable."
                    )

                else:

                    latest = indicators.iloc[-1]

                    news = get_news(
                        f"{selected['name']} India stock",
                        max_results=8,
                    )

                    news_text = news_to_text(
                        news
                    )

                    prompt = f"""
You are the research intelligence layer of a
cash-equity intraday trading system.

IMPORTANT:
You are NOT the execution layer.

Stock:
{selected['name']}

Symbol:
{selected['symbol']}

Latest price:
{latest['Close']}

RSI:
{latest['RSI']}

EMA9:
{latest['EMA9']}

EMA21:
{latest['EMA21']}

Volume ratio:
{latest['VOL_RATIO']}

Recent news:
{news_text}

Return:

1. MARKET REGIME
2. TECHNICAL STRUCTURE
3. NEWS/SENTIMENT
4. POSSIBLE SETUP
5. INVALIDATION
6. RISK FACTORS
7. CONFIDENCE 0-100
8. ACTION:
   WATCH
   BUY_CANDIDATE
   SELL_CANDIDATE
   NO_TRADE

Do not invent data.
Do not guarantee profit.
Do not directly place an order.
"""

                    with st.spinner(
                        "AI analyzing..."
                    ):

                        result = ask_ai(
                            groq_api_key,
                            selected_model,
                            """
You are a disciplined financial
research assistant. Separate facts,
signals and uncertainty. Never claim
certainty about market direction.
""",
                            prompt,
                        )

                    st.markdown(
                        "### 🧠 AI Research Report"
                    )

                    st.write(result)


# ============================================================
# RISK MANAGEMENT
# ============================================================

elif page == "🛡️ Risk Management":

    st.subheader(
        "🛡️ Deterministic Risk Engine"
    )

    risk = RiskEngine(
        max_daily_loss=max_daily_loss,
        max_position_value=max_position_value,
        max_trades_per_day=max_trades_per_day,
        minimum_rr=minimum_rr,
    )

    entry = st.number_input(
        "Entry Price",
        min_value=0.01,
        value=100.0,
    )

    stop = st.number_input(
        "Stop Loss",
        min_value=0.01,
        value=98.0,
    )

    target = st.number_input(
        "Target",
        min_value=0.01,
        value=104.0,
    )

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=100,
    )

    if st.button(
        "Validate Trade"
    ):

        valid, reasons = risk.validate_trade(
            action="BUY",
            entry=entry,
            stop_loss=stop,
            target=target,
            quantity=quantity,
            current_daily_pnl=0,
            trade_count=0,
        )

        if valid:

            st.success(
                "TRADE PASSED RISK ENGINE"
            )

        else:

            st.error(
                "TRADE REJECTED"
            )

            for reason in reasons:
                st.write(
                    f"❌ {reason}"
                )


# ============================================================
# BACKTESTING
# ============================================================

elif page == "🧪 Backtesting":

    st.subheader(
        "🧪 Strategy Backtesting"
    )

    search = st.text_input(
        "Backtest stock",
        value="reliance",
    )

    matches = search_instruments(
        search,
        limit=5,
    )

    if not matches.empty:

        selected_name = st.selectbox(
            "Instrument",
            matches["name"].tolist(),
        )

        selected = matches[
            matches["name"] == selected_name
        ].iloc[0]

        if st.button(
            "Run Backtest",
            type="primary",
        ):

            hist = get_history(
                selected["yf_symbol"],
                period="1mo",
                interval="15m",
            )

            result = simple_backtest(
                hist
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Trades",
                result["trades"],
            )

            c2.metric(
                "Return",
                f"{result['return_pct']:.2f}%",
            )

            c3.metric(
                "Win Rate",
                f"{result['win_rate']:.2f}%",
            )

            st.warning(
                "This is a basic development backtest. "
                "It is not yet suitable for validating a live strategy."
            )


# ============================================================
# TRADE JOURNAL
# ============================================================

elif page == "📒 Trade Journal":

    st.subheader(
        "📒 Trade Journal"
    )

    trades = load_paper_trades()

    if trades.empty:

        st.info(
            "No trades recorded."
        )

    else:

        st.dataframe(
            trades,
            use_container_width=True,
            hide_index=True,
        )

        total_pnl = (
            pd.to_numeric(
                trades["pnl"],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        st.metric(
            "Recorded P&L",
            f"₹{total_pnl:,.2f}",
        )


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.subheader(
        "⚙️ System Settings"
    )

    st.write(
        """
        ### Trading scope

        ✅ Indian equities  
        ✅ NSE/BSE research  
        ✅ Intraday/day trading  
        ✅ Paper trading  
        ❌ Futures  
        ❌ Options  
        ❌ Unrestricted AI order execution  

        ### Planned broker adapters

        • Groww  
        • SBI Securities  

        ### Planned next modules

        • Complete NSE/BSE instrument master  
        • Real-time broker market feed  
        • WebSocket data  
        • Real-time order book  
        • Advanced candlestick recognition  
        • Support/resistance engine  
        • Breakout detector  
        • Pattern image analysis  
        • News credibility scoring  
        • Theme momentum engine  
        • IPO official-data connector  
        • Advanced backtesting  
        • Portfolio analytics  
        • Broker execution gateway  
        • Authentication and licensing
        """
    )

    st.subheader(
        "Broker Connectivity"
    )

    groww = GrowwBroker()
    sbi = SBISecuritiesBroker()

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "### 🟢 Groww"
        )

        st.info(
            groww.connect()["message"]
        )

    with c2:

        st.markdown(
            "### 🔵 SBI Securities"
        )

        st.info(
            sbi.connect()["message"]
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "OMNITRIX AI • Local Trading Terminal • "
    "Phase 1 Indian Equities • F&O Disabled"
)
