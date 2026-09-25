from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re
import yfinance as yf

def _clean(symbol):
    return symbol.replace(".NS","").replace(".BO","").strip()

def _one(symbol,max_results=10):
    rows=[]
    try:
        items=yf.Ticker(symbol).news or []
        for item in items[:max_results]:
            content=item.get("content",item)
            title=content.get("title","") if isinstance(content,dict) else item.get("title","")
            if not title: continue
            provider=content.get("provider",{}) if isinstance(content,dict) else {}
            publisher=provider.get("displayName","Yahoo Finance") if isinstance(provider,dict) else "Yahoo Finance"
            link=content.get("canonicalUrl",{}) if isinstance(content,dict) else {}
            if isinstance(link,dict): link=link.get("url","")
            ts=content.get("pubDate","") if isinstance(content,dict) else ""
            rows.append({"title":title,"publisher":publisher,"url":link or "",
                         "description":content.get("summary","") if isinstance(content,dict) else "",
                         "published":ts,"symbol":symbol,"source":"YFinance"})
    except Exception:
        pass
    return rows

def fetch_news(symbol,max_results=20):
    rows=_one(symbol,max_results)
    return rows if rows else [{"title":"No YFinance news returned","publisher":"YFinance","url":"","description":"","published":"","symbol":symbol,"source":"YFinance"}]

def fetch_news_batch(symbols,max_results=5,max_workers=10):
    out={}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures={ex.submit(_one,s,max_results):s for s in symbols}
        for future in as_completed(futures):
            s=futures[future]
            try: out[s]=future.result()
            except Exception: out[s]=[]
    return out

POSITIVE={"beat","growth","surge","rises","wins","order","contract","approval","upgrade","profit","record","expands","partnership","launch","strong","buyback"}
NEGATIVE={"fall","falls","drop","loss","downgrade","probe","fraud","delay","weak","cut","warning","resign","lawsuit","decline","miss","debt"}

def match_news_to_stock(symbol,items,company=""):
    text=" ".join((x.get("title","")+" "+x.get("description","")) for x in items).lower()
    tokens=re.findall(r"[a-z0-9]+",text)
    pos=sum(1 for t in tokens if t in POSITIVE)
    neg=sum(1 for t in tokens if t in NEGATIVE)
    score=max(-10,min(10,(pos-neg)*2))
    bias="POSITIVE" if score>0 else ("NEGATIVE" if score<0 else "NEUTRAL")
    headline=items[0].get("title","") if items else "No recent news"
    return {"symbol":symbol,"company":company,"bias":bias,"score":score,"headline":headline,"items":items}

def news_text(news):
    if not news: return "No news available."
    return "\n\n".join(
        f"Headline: {x.get('title','')}\nPublisher: {x.get('publisher','')}\nPublished: {x.get('published','')}\nDescription: {x.get('description','')}"
        for x in news
    )
