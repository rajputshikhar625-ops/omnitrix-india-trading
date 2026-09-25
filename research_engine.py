import yfinance as yf
import pandas as pd
from market_data import yahoo_history
from indicators import add_indicators, technical_snapshot
from news_engine import fetch_news, match_news_to_stock
from pattern_engine import pattern_snapshot, all_pattern_stats

def get_fundamentals(symbol):
    try:
        info=yf.Ticker(symbol).info
        fields=["longName","sector","industry","marketCap","enterpriseValue","trailingPE","forwardPE","priceToBook","returnOnEquity","profitMargins","revenueGrowth","earningsGrowth","debtToEquity","dividendYield"]
        return {f:info.get(f) for f in fields}
    except Exception as e:return {"error":str(e)}

def calculate_levels(df):
    if df.empty:return {}
    recent=df.tail(100); high=float(recent["high"].max()); low=float(recent["low"].min()); last=float(recent["close"].iloc[-1])
    pivot=(high+low+last)/3; diff=high-low
    return {"swing_high":high,"swing_low":low,"pivot":pivot,"r1":2*pivot-low,"r2":pivot+diff,"s1":2*pivot-high,"s2":pivot-diff,
            "fibonacci":{"23.6%":high-diff*.236,"38.2%":high-diff*.382,"50.0%":high-diff*.5,"61.8%":high-diff*.618}}

def research_stock(symbol):
    daily=yahoo_history(symbol,period="2y",interval="1d")
    intraday=yahoo_history(symbol,period="5d",interval="5m")
    base=daily if not daily.empty else intraday
    if base.empty:return {"symbol":symbol,"technical":{},"fundamentals":{},"levels":{},"news":[],"history":base,"intraday":intraday,"patterns":[],"pattern_history":pd.DataFrame()}
    base=add_indicators(base); intraday=add_indicators(intraday) if not intraday.empty else intraday
    news=fetch_news(symbol,20)
    return {"symbol":symbol,"technical":technical_snapshot(base),"fundamentals":get_fundamentals(symbol),
            "levels":calculate_levels(base),"news":news,"news_match":match_news_to_stock(symbol,news),
            "history":base,"intraday":intraday,"patterns":pattern_snapshot(base).get("patterns",[]),
            "pattern_history":all_pattern_stats(base,5)}
