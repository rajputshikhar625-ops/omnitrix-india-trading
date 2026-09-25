import time
from datetime import datetime

import pandas as pd
import yfinance as yf

from config import (
    GROWW_ACCESS_TOKEN,
    NIFTY_SYMBOL
)

try:
    from growwapi import GrowwAPI
except Exception:
    GrowwAPI = None


# ==========================================
# GROWw CLIENT
# ==========================================

_groww = None


def get_groww():

    global _groww

    if not GROWW_ACCESS_TOKEN:
        return None

    if GrowwAPI is None:
        return None

    if _groww is None:
        try:
            _groww = GrowwAPI(
                GROWW_ACCESS_TOKEN
            )
        except Exception:
            return None

    return _groww


# ==========================================
# SYMBOL CONVERSION
# ==========================================

def clean_symbol(symbol):

    symbol = symbol.upper().strip()

    if symbol.endswith(".NS"):
        return symbol[:-3]

    return symbol


# ==========================================
# YFINANCE
# ==========================================

def yahoo_history(
    symbol,
    period="5d",
    interval="5m"
):

    try:

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        df.columns = [
            str(c).lower().replace(" ", "_")
            for c in df.columns
        ]

        if "datetime" not in df.columns:

            if "date" in df.columns:
                df.rename(
                    columns={"date": "datetime"},
                    inplace=True
                )

        return df

    except Exception:
        return pd.DataFrame()


# ==========================================
# CURRENT PRICE
# ==========================================

def get_price(symbol):

    symbol = symbol.upper()

    try:

        ticker = yf.Ticker(symbol)

        hist = ticker.history(
            period="1d",
            interval="1m"
        )

        if hist.empty:
            return None

        return float(
            hist["Close"].iloc[-1]
        )

    except Exception:

        return None


# ==========================================
# GROWw LTP
# ==========================================

def groww_ltp(symbols):

    groww = get_groww()

    if groww is None:
        return {}

    results = {}

    try:

        exchange_symbols = [
            clean_symbol(x)
            for x in symbols
        ]

        for i in range(
            0,
            len(exchange_symbols),
            50
        ):

            batch = exchange_symbols[
                i:i + 50
            ]

            response = groww.get_ltp(
                exchange=groww.EXCHANGE_NSE,
                segment=groww.SEGMENT_CASH,
                exchange_symbols=batch
            )

            if isinstance(response, dict):
                results.update(response)

    except Exception:
        return {}

    return results


# ==========================================
# MULTI-STOCK SNAPSHOT
# ==========================================

def market_snapshot(symbols):

    rows = []

    live = groww_ltp(symbols)

    for symbol in symbols:

        price = None

        clean = clean_symbol(symbol)

        if clean in live:

            try:
                price = float(
                    live[clean]
                )
            except Exception:
                pass

        if price is None:
            price = get_price(symbol)

        if price is None:
            continue

        rows.append({
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now()
        })

    return pd.DataFrame(rows)


# ==========================================
# NIFTY
# ==========================================

def get_nifty():

    return yahoo_history(
        NIFTY_SYMBOL,
        period="5d",
        interval="5m"
    )


def get_nifty_price():

    return get_price(
        NIFTY_SYMBOL
    )
