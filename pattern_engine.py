import numpy as np
import pandas as pd

def _safe(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

def detect_patterns(df):
    if df is None or len(df) < 30:
        return []
    x=df.copy().reset_index(drop=True)
    r=[]
    a=x.iloc[-1]; p=x.iloc[-2]
    close=_safe(a.get("close")); prev=_safe(p.get("close"))
    ema9=_safe(a.get("ema9")); ema21=_safe(a.get("ema21"))
    rsi=_safe(a.get("rsi")); vol=_safe(a.get("volume_ratio")); adx=_safe(a.get("adx"))
    high20=_safe(x["high"].tail(20).iloc[:-1].max()); low20=_safe(x["low"].tail(20).iloc[:-1].min())
    if prev <= high20 and close > high20 and vol >= 1.2:
        r.append({"pattern":"BREAKOUT","direction":"UP","strength":min(100,60+vol*15),"reason":"Close above prior 20-bar high with volume expansion"})
    if prev >= low20 and close < low20 and vol >= 1.2:
        r.append({"pattern":"BREAKDOWN","direction":"DOWN","strength":min(100,60+vol*15),"reason":"Close below prior 20-bar low with volume expansion"})
    if ema9 > ema21 and _safe(p.get("ema9")) <= _safe(p.get("ema21")):
        r.append({"pattern":"EMA_CROSS_UP","direction":"UP","strength":65,"reason":"EMA9 crossed above EMA21"})
    if ema9 < ema21 and _safe(p.get("ema9")) >= _safe(p.get("ema21")):
        r.append({"pattern":"EMA_CROSS_DOWN","direction":"DOWN","strength":65,"reason":"EMA9 crossed below EMA21"})
    if close > ema21 and 45 <= rsi <= 65 and vol >= 1.0:
        r.append({"pattern":"TREND_PULLBACK","direction":"UP","strength":60,"reason":"Price above EMA21 with non-extreme RSI and normal/strong volume"})
    if close < ema21 and 35 <= rsi <= 55 and vol >= 1.0:
        r.append({"pattern":"BEAR_PULLBACK","direction":"DOWN","strength":60,"reason":"Price below EMA21 with non-extreme RSI and normal/strong volume"})
    if rsi >= 70:
        r.append({"pattern":"RSI_OVERBOUGHT","direction":"RISK","strength":70,"reason":"RSI above 70"})
    elif rsi <= 30:
        r.append({"pattern":"RSI_OVERSOLD","direction":"RISK","strength":70,"reason":"RSI below 30"})
    if adx >= 25:
        r.append({"pattern":"STRONG_TREND","direction":"TREND","strength":min(100,50+adx),"reason":"ADX indicates stronger trend conditions"})
    return r

def pattern_snapshot(df):
    pats=detect_patterns(df)
    return {"patterns":pats,"primary":pats[0]["pattern"] if pats else "NO_CLEAR_PATTERN"}

def historical_pattern_stats(df, pattern_name, horizon=5):
    if df is None or len(df) < 80:
        return {"pattern":pattern_name,"samples":0,"win_rate":None,"avg_return":None,"status":"INSUFFICIENT_DATA"}
    x=df.copy().reset_index(drop=True)
    hits=[]
    for i in range(30,len(x)-horizon):
        sub=x.iloc[:i+1]
        names=[p["pattern"] for p in detect_patterns(sub)]
        if pattern_name in names:
            entry=_safe(x.iloc[i]["close"])
            future=_safe(x.iloc[i+horizon]["close"])
            if entry:
                hits.append((future/entry-1)*100)
    if not hits:
        return {"pattern":pattern_name,"samples":0,"win_rate":None,"avg_return":None,"status":"NO_MATCHES"}
    arr=np.array(hits,dtype=float)
    return {"pattern":pattern_name,"samples":int(len(arr)),"win_rate":round(float((arr>0).mean()*100),1),"avg_return":round(float(arr.mean()),2),"median_return":round(float(np.median(arr)),2),"status":"HISTORICAL_ONLY"}

def all_pattern_stats(df, horizon=5):
    names=["BREAKOUT","BREAKDOWN","EMA_CROSS_UP","EMA_CROSS_DOWN","TREND_PULLBACK","BEAR_PULLBACK"]
    return pd.DataFrame([historical_pattern_stats(df,n,horizon) for n in names])
