import numpy as np
import pandas as pd


def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def sma(series, period):

    return series.rolling(
        period
    ).mean()


def rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    return 100 - (
        100 / (1 + rs)
    )


def true_range(df):

    previous_close = df["close"].shift(1)

    tr1 = (
        df["high"] -
        df["low"]
    )

    tr2 = (
        df["high"] -
        previous_close
    ).abs()

    tr3 = (
        df["low"] -
        previous_close
    ).abs()

    return pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)


def atr(df, period=14):

    return true_range(df).rolling(
        period
    ).mean()


def macd(series):

    fast = ema(series, 12)

    slow = ema(series, 26)

    line = fast - slow

    signal = ema(
        line,
        9
    )

    histogram = line - signal

    return (
        line,
        signal,
        histogram
    )


def bollinger(series, period=20):

    middle = sma(
        series,
        period
    )

    std = series.rolling(
        period
    ).std()

    upper = middle + (
        2 * std
    )

    lower = middle - (
        2 * std
    )

    return (
        middle,
        upper,
        lower
    )


def vwap(df):

    typical = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    cumulative_volume = (
        df["volume"].cumsum()
    )

    cumulative_value = (
        typical * df["volume"]
    ).cumsum()

    return (
        cumulative_value /
        cumulative_volume.replace(
            0,
            np.nan
        )
    )


def stochastic(
    df,
    period=14,
    smooth=3
):

    lowest = df["low"].rolling(
        period
    ).min()

    highest = df["high"].rolling(
        period
    ).max()

    k = (
        100 *
        (
            df["close"] - lowest
        ) /
        (
            highest - lowest
        )
    )

    d = k.rolling(
        smooth
    ).mean()

    return k, d


def obv(df):

    direction = np.sign(
        df["close"].diff()
    )

    return (
        direction *
        df["volume"]
    ).fillna(0).cumsum()


def roc(series, period=12):

    return (
        series.pct_change(period) *
        100
    )


def cci(df, period=20):

    typical = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    mean = typical.rolling(
        period
    ).mean()

    deviation = typical.rolling(
        period
    ).apply(
        lambda x: np.mean(
            np.abs(x - np.mean(x))
        ),
        raw=True
    )

    return (
        typical - mean
    ) / (
        0.015 * deviation
    )


def money_flow_index(
    df,
    period=14
):

    typical = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    money_flow = (
        typical *
        df["volume"]
    )

    direction = typical.diff()

    positive = money_flow.where(
        direction > 0,
        0
    )

    negative = money_flow.where(
        direction < 0,
        0
    )

    positive_sum = positive.rolling(
        period
    ).sum()

    negative_sum = negative.abs().rolling(
        period
    ).sum()

    ratio = (
        positive_sum /
        negative_sum.replace(
            0,
            np.nan
        )
    )

    return 100 - (
        100 / (1 + ratio)
    )


def adx(df, period=14):

    high = df["high"]
    low = df["low"]

    plus_dm = (
        high.diff()
    )

    minus_dm = (
        -low.diff()
    )

    plus_dm = plus_dm.where(
        (plus_dm > minus_dm) &
        (plus_dm > 0),
        0
    )

    minus_dm = minus_dm.where(
        (minus_dm > plus_dm) &
        (minus_dm > 0),
        0
    )

    tr = true_range(df)

    atr_value = tr.rolling(
        period
    ).mean()

    plus_di = (
        100 *
        plus_dm.rolling(period).mean() /
        atr_value
    )

    minus_di = (
        100 *
        minus_dm.rolling(period).mean() /
        atr_value
    )

    dx = (
        (
            plus_di - minus_di
        ).abs() /
        (
            plus_di + minus_di
        ).replace(0, np.nan)
    ) * 100

    return dx.rolling(
        period
    ).mean()


def add_indicators(df):

    if df is None or df.empty:
        return df

    df = df.copy()

    required = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for column in required:

        if column not in df.columns:
            return df

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df["ema9"] = ema(
        df["close"],
        9
    )

    df["ema21"] = ema(
        df["close"],
        21
    )

    df["sma20"] = sma(
        df["close"],
        20
    )

    df["sma50"] = sma(
        df["close"],
        50
    )

    df["sma200"] = sma(
        df["close"],
        200
    )

    df["rsi"] = rsi(
        df["close"]
    )

    df["atr"] = atr(df)

    (
        df["macd"],
        df["macd_signal"],
        df["macd_hist"]
    ) = macd(
        df["close"]
    )

    (
        df["bb_middle"],
        df["bb_upper"],
        df["bb_lower"]
    ) = bollinger(
        df["close"]
    )

    df["vwap"] = vwap(df)

    (
        df["stoch_k"],
        df["stoch_d"]
    ) = stochastic(df)

    df["obv"] = obv(df)

    df["roc"] = roc(
        df["close"]
    )

    df["cci"] = cci(df)

    df["mfi"] = money_flow_index(
        df
    )

    df["adx"] = adx(df)

    df["volume_avg20"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    df["volume_ratio"] = (
        df["volume"] /
        df["volume_avg20"]
    )

    return df


def technical_snapshot(df):

    if df is None or df.empty:
        return {}

    df = add_indicators(df)

    latest = df.iloc[-1]

    fields = [
        "close",
        "ema9",
        "ema21",
        "sma20",
        "sma50",
        "sma200",
        "rsi",
        "atr",
        "macd",
        "macd_signal",
        "macd_hist",
        "bb_upper",
        "bb_lower",
        "vwap",
        "stoch_k",
        "stoch_d",
        "obv",
        "roc",
        "cci",
        "mfi",
        "adx",
        "volume_ratio"
    ]

    result = {}

    for field in fields:

        value = latest.get(
            field,
            np.nan
        )

        if pd.isna(value):
            result[field] = None
        else:
            result[field] = float(value)

    return result
