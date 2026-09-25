import numpy as np
import pandas as pd
def ema(s,p):return s.ewm(span=p,adjust=False).mean()
def sma(s,p):return s.rolling(p).mean()
def rsi(s,p=14):
 d=s.diff();g=d.clip(lower=0);l=-d.clip(upper=0);ag=g.ewm(alpha=1/p,adjust=False).mean();al=l.ewm(alpha=1/p,adjust=False).mean();return (100-100/(1+ag/al.replace(0,np.nan))).fillna(100)
def true_range(df):
 pc=df["close"].shift(1);return pd.concat([df["high"]-df["low"],(df["high"]-pc).abs(),(df["low"]-pc).abs()],axis=1).max(axis=1)
def atr(df,p=14):return true_range(df).rolling(p).mean()
def macd(s):
 l=ema(s,12)-ema(s,26);sig=ema(l,9);return l,sig,l-sig
def bollinger(s,p=20):
 m=sma(s,p);sd=s.rolling(p).std();return m,m+2*sd,m-2*sd
def vwap(df):
 t=(df["high"]+df["low"]+df["close"])/3;cv=df["volume"].cumsum();return (t*df["volume"]).cumsum()/cv.replace(0,np.nan)
def stochastic(df,p=14,sm=3):
 lo=df["low"].rolling(p).min();hi=df["high"].rolling(p).max();k=100*(df["close"]-lo)/(hi-lo).replace(0,np.nan);return k,k.rolling(sm).mean()
def obv(df):return (np.sign(df["close"].diff())*df["volume"]).fillna(0).cumsum()
def roc(s,p=12):return s.pct_change(p)*100
def cci(df,p=20):
 t=(df["high"]+df["low"]+df["close"])/3;m=t.rolling(p).mean();dev=t.rolling(p).apply(lambda x:np.mean(np.abs(x-np.mean(x))),raw=True);return (t-m)/(0.015*dev.replace(0,np.nan))
def money_flow_index(df,p=14):
 t=(df["high"]+df["low"]+df["close"])/3;mf=t*df["volume"];d=t.diff();pos=mf.where(d>0,0).rolling(p).sum();neg=mf.where(d<0,0).abs().rolling(p).sum();ratio=pos/neg.replace(0,np.nan);return 100-100/(1+ratio)
def adx(df,p=14):
 up=df["high"].diff();down=-df["low"].diff();plus=up.where((up>down)&(up>0),0.0);minus=down.where((down>up)&(down>0),0.0);a=true_range(df).rolling(p).mean().replace(0,np.nan);pi=100*plus.rolling(p).mean()/a;mi=100*minus.rolling(p).mean()/a;return (100*(pi-mi).abs()/(pi+mi).replace(0,np.nan)).rolling(p).mean()
def add_indicators(df):
 if df is None or df.empty:return df
 df=df.copy()
 for c in ["open","high","low","close","volume"]:
  if c not in df.columns:return df
  df[c]=pd.to_numeric(df[c],errors="coerce")
 df["ema9"]=ema(df.close,9);df["ema21"]=ema(df.close,21);df["sma20"]=sma(df.close,20);df["sma50"]=sma(df.close,50);df["sma200"]=sma(df.close,200);df["rsi"]=rsi(df.close);df["atr"]=atr(df);df["macd"],df["macd_signal"],df["macd_hist"]=macd(df.close);df["bb_middle"],df["bb_upper"],df["bb_lower"]=bollinger(df.close);df["vwap"]=vwap(df);df["stoch_k"],df["stoch_d"]=stochastic(df);df["obv"]=obv(df);df["roc"]=roc(df.close);df["cci"]=cci(df);df["mfi"]=money_flow_index(df);df["adx"]=adx(df);df["volume_ratio"]=df.volume/df.volume.rolling(20).mean().replace(0,np.nan);return df
def technical_snapshot(df):
 if df is None or df.empty:return {}
 x=add_indicators(df).iloc[-1];fields=["close","ema9","ema21","sma20","sma50","sma200","rsi","atr","macd","macd_signal","macd_hist","bb_upper","bb_lower","vwap","stoch_k","stoch_d","obv","roc","cci","mfi","adx","volume_ratio"];return {f:(None if pd.isna(x.get(f,np.nan)) else float(x.get(f))) for f in fields}
