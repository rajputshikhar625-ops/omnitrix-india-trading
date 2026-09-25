import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from market_data import yahoo_history
from indicators import add_indicators
from pattern_engine import pattern_snapshot

def score_stock(symbol, period="3mo", interval="1d"):
    df=yahoo_history(symbol,period=period,interval=interval)
    if df.empty:return None
    df=add_indicators(df)
    latest=df.iloc[-1]
    close=float(latest["close"])
    score=0
    tests=[
        close>latest["ema9"],close>latest["ema21"],close>latest["sma20"],close>latest["sma50"],
        latest["rsi"]>55,latest["macd"]>latest["macd_signal"],close>latest["vwap"],
        latest["volume_ratio"]>1.2,latest["adx"]>20,latest["mfi"]>50]
    score=sum(10 for x in tests if bool(x))
    ps=pattern_snapshot(df)
    primary=ps["primary"]
    if primary in ("BREAKOUT","EMA_CROSS_UP","TREND_PULLBACK"): score+=10
    if primary in ("BREAKDOWN","EMA_CROSS_DOWN","BEAR_PULLBACK"): score-=10
    return {"symbol":symbol,"price":round(close,2),"score":score,"rsi":round(float(latest["rsi"]),1),
            "volume_ratio":round(float(latest["volume_ratio"]),2),"adx":round(float(latest["adx"]),1),
            "macd":round(float(latest["macd"]),3),"pattern":primary}

def scan_universe(symbols,limit=None,max_workers=12):
    symbols=symbols[:limit] if limit else list(symbols)
    rows=[]
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures={ex.submit(score_stock,s):s for s in symbols}
        for fut in as_completed(futures):
            try:
                x=fut.result()
                if x: rows.append(x)
            except Exception:
                pass
    return pd.DataFrame(rows).sort_values("score",ascending=False).reset_index(drop=True) if rows else pd.DataFrame()
