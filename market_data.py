from datetime import datetime
import pandas as pd
import yfinance as yf
from config import GROWW_ACCESS_TOKEN,NIFTY_SYMBOL
try:
 from growwapi import GrowwAPI
except Exception: GrowwAPI=None
_groww=None
def get_groww():
 global _groww
 if not GROWW_ACCESS_TOKEN or GrowwAPI is None:return None
 if _groww is None:
  try:_groww=GrowwAPI(GROWW_ACCESS_TOKEN)
  except Exception:_groww=None
 return _groww
def clean_symbol(symbol):
 s=str(symbol).upper().strip(); return s[:-3] if s.endswith(".NS") else s
def yahoo_history(symbol,period="5d",interval="5m"):
 try:
  df=yf.download(symbol,period=period,interval=interval,progress=False,auto_adjust=False,threads=False)
  if df is None or df.empty:return pd.DataFrame()
  if isinstance(df.columns,pd.MultiIndex):df.columns=df.columns.get_level_values(0)
  df=df.reset_index(); df.columns=[str(c).lower().replace(" ","_") for c in df.columns]
  if "datetime" not in df.columns and "date" in df.columns:df.rename(columns={"date":"datetime"},inplace=True)
  req=["open","high","low","close","volume"]
  return df if all(c in df.columns for c in req) else pd.DataFrame()
 except Exception:return pd.DataFrame()
def get_price(symbol):
 try:
  h=yf.Ticker(symbol).history(period="1d",interval="1m",auto_adjust=False)
  return None if h is None or h.empty else float(h["Close"].iloc[-1])
 except Exception:return None
def groww_ltp(symbols):
 g=get_groww()
 if g is None:return {}
 out={}
 try:
  vals=[clean_symbol(s) for s in symbols]
  for i in range(0,len(vals),50):
   resp=g.get_ltp(exchange=g.EXCHANGE_NSE,segment=g.SEGMENT_CASH,exchange_symbols=vals[i:i+50])
   if isinstance(resp,dict):out.update(resp)
 except Exception:return {}
 return out
def market_snapshot(symbols):
 live=groww_ltp(symbols); rows=[]
 for symbol in symbols:
  price=None; clean=clean_symbol(symbol)
  if clean in live:
   try:price=float(live[clean])
   except Exception:pass
  if price is None:price=get_price(symbol)
  if price is not None:rows.append({"symbol":symbol,"price":price,"timestamp":datetime.now()})
 return pd.DataFrame(rows)
def get_nifty():return yahoo_history(NIFTY_SYMBOL,"5d","5m")
def get_nifty_price():return get_price(NIFTY_SYMBOL)
