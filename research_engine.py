import yfinance as yf
import pandas as pd

from market_data import yahoo_history
from indicators import (
    add_indicators,
    technical_snapshot
)
from news_engine import fetch_news


def get_fundamentals(symbol):

    try:

        ticker = yf.Ticker(symbol)

        info = ticker.info

        fields = [
            "longName",
            "sector",
            "industry",
            "marketCap",
            "enterpriseValue",
            "trailingPE",
            "forwardPE",
            "priceToBook",
            "returnOnEquity",
            "profitMargins",
            "revenueGrowth",
            "earningsGrowth",
            "debtToEquity",
            "dividendYield"
        ]

        result = {}

        for field in fields:

            result[field] = info.get(
                field
            )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


def calculate_levels(df):

    if df.empty:
        return {}

    recent = df.tail(100)

    high = float(
        recent["high"].max()
    )

    low = float(
        recent["low"].min()
    )

    last = float(
        recent["close"].iloc[-1]
    )

    pivot = (
        high +
        low +
        last
    ) / 3

    r1 = (
        2 * pivot
    ) - low

    s1 = (
        2 * pivot
    ) - high

    r2 = (
        pivot +
        high -
        low
    )

    s2 = (
        pivot -
        high +
        low
    )

    diff = high - low

    fibonacci = {
        "23.6%": high - (
            diff * 0.236
        ),
        "38.2%": high - (
            diff * 0.382
        ),
        "50.0%": high - (
            diff * 0.500
        ),
        "61.8%": high - (
            diff * 0.618
        )
    }

    return {
        "swing_high": high,
        "swing_low": low,
        "pivot": pivot,
        "r1": r1,
        "r2": r2,
        "s1": s1,
        "s2": s2,
        "fibonacci": fibonacci
    }


def research_stock(symbol):

    price_df = yahoo_history(
        symbol,
        period="3mo",
        interval="1d"
    )

    if price_df.empty:

        return {
            "symbol": symbol,
            "technical": {},
            "fundamentals": {},
            "levels": {},
            "news": [],
            "history": price_df
        }

    price_df = add_indicators(
        price_df
    )

    technical = technical_snapshot(
        price_df
    )

    levels = calculate_levels(
        price_df
    )

    fundamentals = get_fundamentals(
        symbol
    )

    news = fetch_news(
        symbol,
        max_results=20
    )

    return {
        "symbol": symbol,
        "technical": technical,
        "fundamentals": fundamentals,
        "levels": levels,
        "news": news,
        "history": price_df
    }
