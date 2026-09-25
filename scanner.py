import pandas as pd

from market_data import yahoo_history
from indicators import (
    add_indicators
)


def score_stock(
    symbol
):

    df = yahoo_history(
        symbol,
        period="3mo",
        interval="1d"
    )

    if df.empty:
        return None

    df = add_indicators(
        df
    )

    latest = df.iloc[-1]

    score = 0

    close = latest["close"]

    if close > latest["ema9"]:
        score += 10

    if close > latest["ema21"]:
        score += 10

    if close > latest["sma20"]:
        score += 10

    if close > latest["sma50"]:
        score += 10

    if latest["rsi"] > 55:
        score += 10

    if latest["macd"] > latest["macd_signal"]:
        score += 10

    if close > latest["vwap"]:
        score += 10

    if latest["volume_ratio"] > 1.2:
        score += 10

    if latest["adx"] > 20:
        score += 10

    if latest["mfi"] > 50:
        score += 10

    return {
        "symbol": symbol,
        "price": close,
        "score": score,
        "rsi": latest["rsi"],
        "volume_ratio": latest[
            "volume_ratio"
        ],
        "adx": latest["adx"],
        "macd": latest["macd"],
        "macd_signal": latest[
            "macd_signal"
        ]
    }


def scan_universe(
    symbols,
    limit=None
):

    rows = []

    if limit:
        symbols = symbols[:limit]

    for symbol in symbols:

        try:

            result = score_stock(
                symbol
            )

            if result:
                rows.append(
                    result
                )

        except Exception:
            continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(
        rows
    )

    return df.sort_values(
        "score",
        ascending=False
    ).reset_index(
        drop=True
    )
