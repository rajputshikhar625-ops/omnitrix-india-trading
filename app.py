import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from config import APP_VERSION, LOCAL_LLM_MODEL
from market_data import market_snapshot, get_nifty_price
from research_engine import research_stock
from scanner import scan_universe
from ai_engine import ai_call, autonomous_research, autonomous_multi_research, test_ai
from charts import candlestick_chart, oscillator_chart, volume_chart
from paper_trading import get_account, monitor_positions
from learning_engine import learning_report, mistakes_by_reason

st.set_page_config(page_title="OMNITRIX",page_icon="◈",layout="wide",initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp{background:#05090f;color:#eef6ff}
.block-container{max-width:1700px;padding:12px 28px 35px}
header[data-testid="stHeader"]{background:transparent}
p,span,label,h1,h2,h3,h4,h5{color:#eef6ff}
input,textarea,[data-baseweb="select"]>div{background:#08111d!important;color:#eef6ff!important;border:1px solid #1b344d!important}
input::placeholder,textarea::placeholder{color:#62788e!important}
.stButton>button{height:42px;background:#091827;color:#f5fbff;border:1px solid #214967;border-radius:8px;font-weight:700;letter-spacing:.2px}
.stButton>button:hover{background:#0d2b44;border-color:#36c7ff}
[data-testid="stMetric"]{background:#08111d;border:1px solid #183149;border-radius:10px;padding:8px}
[data-testid="stDataFrame"]{border:1px solid #173149;border-radius:10px}
div[data-testid="stTabs"] button{color:#8fa5b9!important}
.hero{background:linear-gradient(115deg,#07111c 0%,#0b2033 58%,#08131f 100%);border:1px solid #1e405b;border-radius:15px;padding:20px 24px;margin-bottom:10px;box-shadow:0 12px 40px rgba(0,0,0,.22)}
.kicker{font-size:11px;color:#49d9ff;font-weight:800;letter-spacing:2.2px}
.title{font-size:34px;font-weight:800;letter-spacing:1px;margin:2px 0}
.subtitle{color:#8ea5ba;font-size:13px}
.nav{background:#07111c;border:1px solid #173149;border-radius:10px;padding:5px;margin:8px 0 14px}
.bento{background:linear-gradient(145deg,#081522,#0b1b2a);border:1px solid #19364e;border-radius:12px;padding:15px;min-height:105px}
.bento .label{font-size:11px;color:#6f91aa;letter-spacing:1.2px;font-weight:800}
.bento .value{font-size:22px;font-weight:800;margin-top:5px}
.bento .sub{font-size:12px;color:#8298aa;margin-top:3px}
.section{font-size:18px;font-weight:800;margin:15px 0 8px}
.signal{background:#071522;border:1px solid #1a3a54;border-radius:12px;padding:14px;min-height:120px}
.signal .head{font-size:12px;font-weight:800;letter-spacing:1.2px;color:#51dfff}
.signal .body{font-size:13px;color:#9eb0c0;margin-top:7px;line-height:1.5}
.status{display:inline-block;border:1px solid #245a47;border-radius:20px;padding:4px 10px;color:#36d9a0;background:#071912;font-size:11px;font-weight:800}
.warn{border:1px solid #5a4b20;background:#171306;border-radius:10px;padding:11px;color:#e5c36b}
</style>
""",unsafe_allow_html=True)

STOCKS={
"RELIANCE.NS":"Reliance Industries","TCS.NS":"Tata Consultancy Services","INFY.NS":"Infosys","HDFCBANK.NS":"HDFC Bank","ICICIBANK.NS":"ICICI Bank","SBIN.NS":"State Bank of India","BHARTIARTL.NS":"Bharti Airtel","ITC.NS":"ITC","LT.NS":"Larsen & Toubro","AXISBANK.NS":"Axis Bank","KOTAKBANK.NS":"Kotak Mahindra Bank","HINDUNILVR.NS":"Hindustan Unilever","MARUTI.NS":"Maruti Suzuki","M&M.NS":"Mahindra & Mahindra","TATAMOTORS.NS":"Tata Motors","SUNPHARMA.NS":"Sun Pharma","ADANIENT.NS":"Adani Enterprises","ADANIPORTS.NS":"Adani Ports","NTPC.NS":"NTPC","POWERGRID.NS":"Power Grid","ONGC.NS":"ONGC","COALINDIA.NS":"Coal India","TATASTEEL.NS":"Tata Steel","JSWSTEEL.NS":"JSW Steel","HINDALCO.NS":"Hindalco","WIPRO.NS":"Wipro","HCLTECH.NS":"HCL Technologies","TECHM.NS":"Tech Mahindra","LTIM.NS":"LTIMindtree","ASIANPAINT.NS":"Asian Paints","ULTRACEMCO.NS":"UltraTech Cement","TITAN.NS":"Titan","BAJFINANCE.NS":"Bajaj Finance","BAJAJFINSV.NS":"Bajaj Finserv","HDFCLIFE.NS":"HDFC Life","SBILIFE.NS":"SBI Life","DRREDDY.NS":"Dr Reddy's","CIPLA.NS":"Cipla","DIVISLAB.NS":"Divi's Laboratories","EICHERMOT.NS":"Eicher Motors","HEROMOTOCO.NS":"Hero MotoCorp","BAJAJ-AUTO.NS":"Bajaj Auto","GRASIM.NS":"Grasim","BRITANNIA.NS":"Britannia","NESTLEIND.NS":"Nestle India","TRENT.NS":"Trent","BEL.NS":"Bharat Electronics","HAL.NS":"Hindustan Aeronautics","IRCTC.NS":"IRCTC","IOC.NS":"Indian Oil","BPCL.NS":"BPCL","GAIL.NS":"GAIL","VEDL.NS":"Vedanta","ZOMATO.NS":"Zomato","DLF.NS":"DLF","PIDILITIND.NS":"Pidilite","SIEMENS.NS":"Siemens","ABB.NS":"ABB India","INDUSINDBK.NS":"IndusInd Bank","BANKBARODA.NS":"Bank of Baroda","PNB.NS":"Punjab National Bank","CANBK.NS":"Canara Bank","IDFCFIRSTB.NS":"IDFC First Bank","MOTHERSON.NS":"Samvardhana Motherson","ASHOKLEY.NS":"Ashok Leyland","TVSMOTOR.NS":"TVS Motor","APOLLOHOSP.NS":"Apollo Hospitals","MAXHEALTH.NS":"Max Healthcare","LUPIN.NS":"Lupin","AUROPHARMA.NS":"Aurobindo Pharma","DABUR.NS":"Dabur","GODREJCP.NS":"Godrej Consumer","TATACONSUM.NS":"Tata Consumer","VOLTAS.NS":"Voltas","HAVELLS.NS":"Havells","DIXON.NS":"Dixon Technologies","PERSISTENT.NS":"Persistent Systems","COFORGE.NS":"Coforge","POLYCAB.NS":"Polycab"}

if "page" not in st.session_state: st.session_state.page="MARKET"
if "selected" not in st.session_state: st.session_state.selected="RELIANCE.NS"
if "pkg" not in st.session_state: st.session_state.pkg=None
if "chat" not in st.session_state: st.session_state.chat=[]
if "market_watchlist" not in st.session_state: st.session_state.market_watchlist=["RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","SBIN.NS"]


def mini_trend_chart(frame,symbol):
    if frame is None or frame.empty or "close" not in frame.columns: return None
    values=pd.to_numeric(frame["close"],errors="coerce").dropna().tail(80)
    if len(values)<2: return None
    x=frame.loc[values.index,"datetime"] if "datetime" in frame.columns else values.index
    up=float(values.iloc[-1])>=float(values.iloc[0])
    color="#36d9a0" if up else "#ff667a"
    fig=go.Figure(go.Scatter(x=x,y=values,mode="lines",line={"color":color,"width":2},fill="tozeroy",fillcolor="rgba(54,217,160,.10)" if up else "rgba(255,102,122,.10)",hovertemplate="%{x}<br>₹%{y:,.2f}<extra>"+symbol.replace(".NS","")+"</extra>"))
    fig.update_layout(height=135,margin={"l":0,"r":0,"t":4,"b":0},paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False,xaxis={"visible":False,"fixedrange":True},yaxis={"visible":False,"fixedrange":True})
    return fig

st.markdown(f'<div class="hero"><div class="kicker">OMNITRIX INTELLIGENCE TERMINAL</div><div class="title">OMNITRIX</div><div class="subtitle">Indian cash-equity research • pattern intelligence • local AI • paper execution</div><div style="margin-top:9px"><span class="status">LLaMA {LOCAL_LLM_MODEL} ONLINE</span> <span class="subtitle"> &nbsp; F&O OFF &nbsp;•&nbsp; LIVE ORDERS OFF &nbsp;•&nbsp; PAPER MODE</span></div></div>',unsafe_allow_html=True)

nav=st.columns(5)
for i,name in enumerate(["MARKET","AI","RESEARCHER","SCANNER","AI DEPLOYED"]):
    active=" ▪" if st.session_state.page==name else ""
    if nav[i].button(name+active,use_container_width=True,key="nav_"+name):
        st.session_state.page=name; st.rerun()

if st.session_state.page=="MARKET":
    nifty=get_nifty_price(); a=get_account()
    st.markdown('<div class="section">Command Center</div>',unsafe_allow_html=True)
    c=st.columns(5)
    cards=[("NIFTY 50",f"₹{nifty:,.2f}" if nifty else "DATA","market pulse"),("PAPER CASH",f"₹{a['cash']:,.0f}","test capital"),("REALIZED P&L",f"₹{a['realized_pnl']:,.0f}","paper ledger"),("UNIVERSE",f"{len(STOCKS)}","Indian equities"),("AI STATUS","ONLINE","local LLaMA")]
    for col,(l,v,s) in zip(c,cards):
        col.markdown(f'<div class="bento"><div class="label">{l}</div><div class="value">{v}</div><div class="sub">{s}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">Market Pulse</div>',unsafe_allow_html=True)
    if st.button("REFRESH MARKET SNAPSHOT",use_container_width=True):
        st.cache_data.clear(); st.rerun()
    snap=market_snapshot(list(STOCKS)[:50])
    if not snap.empty: st.dataframe(snap,use_container_width=True,hide_index=True)
    st.caption("Price source: Groww LTP when configured; otherwise YFinance fallback. Exchange-grade live feed will be added only after deliberate activation.")

elif st.session_state.page=="AI":
    st.markdown('<div class="section">AI Workspace</div>',unsafe_allow_html=True)
    left,right=st.columns([1.7,1])
    with left:
        for m in st.session_state.chat[-12:]: st.chat_message(m["role"]).markdown(m["content"])
        prompt=st.chat_input("Ask about a setup, pattern, news reaction, exit rule or research question")
        if prompt:
            st.session_state.chat.append({"role":"user","content":prompt})
            try: ans=ai_call(prompt+"\nAnswer as an evidence-first trading research assistant. Do not place orders.",provider="LOCAL")
            except Exception as e: ans="AI error: "+str(e)
            st.session_state.chat.append({"role":"assistant","content":ans}); st.rerun()
    with right:
        st.markdown('<div class="bento"><div class="label">PATTERN MEMORY</div><div class="value">Human → Rule</div><div class="sub">Describe your own trading pattern and OMNITRIX converts it into testable conditions.</div></div>',unsafe_allow_html=True)
        p=st.text_area("Pattern description","Example: breakout + volume expansion + positive news + EMA trend.")
        if st.button("CONVERT TO RULE",use_container_width=True):
            try: st.write(ai_call("Convert this trading idea into deterministic conditions, confirmation, invalidation, exit and risk rules. Do not invent evidence.\n"+p,provider="LOCAL"))
            except Exception as e: st.error(str(e))

elif st.session_state.page=="RESEARCHER":
    st.markdown('<div class="section">Researcher</div>',unsafe_allow_html=True)
    symbols=list(STOCKS)
    selected=st.selectbox("Security",symbols,index=symbols.index(st.session_state.selected),format_func=lambda s:f"{STOCKS[s]}  •  {s}")
    st.session_state.selected=selected
    if st.button("LOAD RESEARCH PACKAGE",use_container_width=True):
        with st.spinner("Loading 2Y history + intraday chart + indicators + YFinance news..."): st.session_state.pkg=research_stock(selected)
    p=st.session_state.pkg
    if p:
        t=p["technical"]; q=st.columns(6)
        for col,l,k in zip(q,["PRICE","RSI","ADX","VOL RATIO","ATR","PATTERN"],["close","rsi","adx","volume_ratio","atr",None]):
            v=p["patterns"][0]["pattern"] if k is None and p["patterns"] else ("NO CLEAR" if k is None else t.get(k))
            col.metric(l, v if isinstance(v,str) else f"{v:.2f}" if v is not None else "DATA")
        chart_df=p["intraday"] if not p["intraday"].empty else p["history"]
        st.plotly_chart(candlestick_chart(chart_df,selected),use_container_width=True)
        x,y=st.columns(2)
        with x: st.plotly_chart(volume_chart(chart_df),use_container_width=True)
        with y: st.plotly_chart(oscillator_chart(chart_df,["rsi","stoch_k","stoch_d"],"Momentum"),use_container_width=True)
        st.markdown('<div class="section">Evidence Matrix</div>',unsafe_allow_html=True)
        sig=st.columns(3)
        nm=p.get("news_match",{})
        with sig[0]: st.markdown(f'<div class="signal"><div class="head">NEWS</div><div class="body">{nm.get("bias","NEUTRAL")} • score {nm.get("score",0)}<br>{nm.get("headline","No recent headline")}</div></div>',unsafe_allow_html=True)
        with sig[1]: st.markdown(f'<div class="signal"><div class="head">PRICE</div><div class="body">₹{t.get("close",0):,.2f}<br>RSI {t.get("rsi",0):.1f} • Volume {t.get("volume_ratio",0):.2f}x</div></div>',unsafe_allow_html=True)
        with sig[2]: st.markdown(f'<div class="signal"><div class="head">CHART</div><div class="body">{", ".join(x["pattern"] for x in p.get("patterns",[])[:4]) or "No clear pattern"}</div></div>',unsafe_allow_html=True)
        st.markdown("### Historical pattern behaviour")
        st.dataframe(p["pattern_history"],use_container_width=True,hide_index=True)
        st.markdown("### Recent YFinance news")
        for n in p["news"][:10]: st.markdown(f"**{n['title']}** — {n['publisher']}  <span class='subtitle'>{n['published']}</span>",unsafe_allow_html=True)
        if st.button("AI DEEP RESEARCH",use_container_width=True):
            with st.spinner("LLaMA comparing news + price + chart + historical pattern evidence..."): st.session_state.report=autonomous_research(p,provider="LOCAL")
        if st.session_state.get("report"): st.markdown(st.session_state.report)

elif st.session_state.page=="SCANNER":
    st.markdown('<div class="section">50-Stock Scanner</div>',unsafe_allow_html=True)
    st.caption("Deterministic filtering first. AI is used only after the shortlist.")
    n=st.slider("Universe size",20,min(80,len(STOCKS)),50)
    if st.button("SCAN NOW",use_container_width=True):
        with st.spinner(f"Parallel scan of {n} stocks..."): st.session_state.scan=scan_universe(list(STOCKS),n)
    r=st.session_state.get("scan",pd.DataFrame())
    if not r.empty:
        st.dataframe(r,use_container_width=True,hide_index=True)
        st.markdown("### Pattern shortlist")
        top=r.head(10)
        st.dataframe(top[["symbol","price","score","pattern","rsi","volume_ratio","adx"]],use_container_width=True,hide_index=True)
        if st.button("SEND TOP 5 TO LOCAL AI",use_container_width=True):
            symbols=top.head(5)["symbol"].tolist()
            package_map={}
            with st.spinner("Collecting the shortlist in parallel for one local AI comparison…"):
                with ThreadPoolExecutor(max_workers=min(4,len(symbols))) as pool:
                    futures={pool.submit(research_stock,s):s for s in symbols}
                    for future in as_completed(futures):
                        symbol=futures[future]
                        try: package_map[symbol]=future.result()
                        except Exception as error: package_map[symbol]={"symbol":symbol,"technical":{},"fundamentals":{},"levels":{},"news":[],"patterns":[]}
                try:
                    ordered=[package_map[s] for s in symbols if s in package_map]
                    st.session_state.scan_ai=autonomous_multi_research(ordered,provider="LOCAL")
                except Exception as error:
                    st.session_state.scan_ai=f"Local shortlist analysis failed: {error}"
        if st.session_state.get("scan_ai"): st.markdown(st.session_state.scan_ai)

elif st.session_state.page=="AI DEPLOYED":
    st.markdown('<div class="section">AI Deployed — Multi-stock Decision Desk</div>',unsafe_allow_html=True)
    st.markdown('<div class="warn">PAPER RESEARCH ONLY. The pipeline reads market evidence and runs local AI analysis. It does not send broker orders or provide external notifications.</div>',unsafe_allow_html=True)
    status_cols=st.columns(4)
    for col,label,value,detail in zip(status_cols,["NEWS","PRICE","CHART","RISK"],["Headlines","Quote snapshot","Trend + pattern","Hard gate"],["stock-linked feed","provider may be delayed","technical context","live orders disabled"]):
        col.markdown(f'<div class="bento"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{detail}</div></div>',unsafe_allow_html=True)

    selected=st.multiselect("AI focus list · up to 6 stocks",list(STOCKS),default=st.session_state.market_watchlist[:6],max_selections=6,format_func=lambda s:f"{STOCKS[s]} • {s}",key="deploy_stocks")
    if selected!=st.session_state.get("deploy_symbols",[]):
        st.session_state.deploy_packages=[]
        st.session_state.deploy_report=""
        st.session_state.deploy_symbols=list(selected)

    if st.button("COLLECT MULTI-STOCK SNAPSHOT",use_container_width=True,disabled=not selected):
        packages_by_symbol={}
        try:
            with st.spinner(f"Collecting quotes, news and chart evidence for {len(selected)} stocks…"):
                quote_frame=market_snapshot(selected)
                quotes=quote_frame.set_index("symbol")["price"].to_dict() if not quote_frame.empty else {}
                with ThreadPoolExecutor(max_workers=min(4,len(selected))) as pool:
                    futures={pool.submit(research_stock,symbol):symbol for symbol in selected}
                    for future in as_completed(futures):
                        symbol=futures[future]
                        try:
                            package=future.result()
                        except Exception as error:
                            package={"symbol":symbol,"technical":{},"fundamentals":{},"levels":{},"news":[],"history":pd.DataFrame(),"intraday":pd.DataFrame(),"patterns":[],"error":str(error)}
                        package["live_price"]=quotes.get(symbol)
                        packages_by_symbol[symbol]=package
            st.session_state.deploy_packages=[packages_by_symbol[symbol] for symbol in selected]
            st.session_state.deploy_quotes=quotes
            st.session_state.deploy_report=""
        except Exception as error:
            st.error(f"Snapshot collection failed: {error}")

    packages=st.session_state.get("deploy_packages",[])
    if packages:
        rows=[]
        for package in packages:
            symbol=package.get("symbol","")
            technical=package.get("technical",{}) or {}
            history=package.get("history",pd.DataFrame())
            closes=history["close"].dropna() if not history.empty and "close" in history else pd.Series(dtype=float)
            move=None
            if len(closes)>=2:
                base=float(closes.iloc[-6]) if len(closes)>=6 else float(closes.iloc[0])
                move=(float(closes.iloc[-1])/base-1)*100 if base else None
            close=package.get("live_price") or technical.get("close")
            ema9=technical.get("ema9"); ema21=technical.get("ema21")
            trend="DATA UNAVAILABLE"
            if technical.get("close") is not None and ema9 is not None and ema21 is not None:
                trend="UPTREND" if technical["close"]>ema9>ema21 else ("DOWNTREND" if technical["close"]<ema9<ema21 else "MIXED")
            news=package.get("news",[]) or []
            match=package.get("news_match",{}) or {}
            pattern_list=package.get("patterns",[]) or []
            pattern=pattern_list[0].get("pattern","NONE") if pattern_list and isinstance(pattern_list[0],dict) else "NONE"
            rows.append({"Symbol":symbol.replace(".NS",""),"Price (₹)":round(float(close),2) if close is not None else None,"5-day move":f"{move:+.2f}%" if move is not None else "—","EMA structure":trend,"News bias":match.get("bias","NEUTRAL"),"Pattern":pattern,"RSI":round(float(technical["rsi"]),1) if technical.get("rsi") is not None else None})
        st.markdown('<div class="section">Six-stock evidence board</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.caption("5-day movement is historical; quotes may be delayed. Trend and news labels summarize supplied evidence and are not price forecasts.")
        st.markdown('<div class="section">Chart + headline by stock</div>',unsafe_allow_html=True)
        for row_start in range(0,len(packages),3):
            cols=st.columns(3)
            for col,package in zip(cols,packages[row_start:row_start+3]):
                symbol=package.get("symbol","")
                technical=package.get("technical",{}) or {}
                live_price=package.get("live_price") or technical.get("close")
                match=package.get("news_match",{}) or {}
                news=package.get("news",[]) or []
                with col:
                    st.markdown(f'<div class="bento"><div class="label">{STOCKS.get(symbol,symbol)} · {symbol.replace(".NS","")}</div><div class="value">₹{float(live_price):,.2f}</div><div class="sub">News tone: {match.get("bias","NEUTRAL")} · Pattern: {(package.get("patterns") or [{}])[0].get("pattern","NONE")}</div></div>' if live_price is not None else f'<div class="bento"><div class="label">{STOCKS.get(symbol,symbol)}</div><div class="value">QUOTE UNAVAILABLE</div><div class="sub">Check the market data connection.</div></div>',unsafe_allow_html=True)
                    chart_frame=package.get("intraday")
                    if chart_frame is None or chart_frame.empty: chart_frame=package.get("history")
                    chart=mini_trend_chart(chart_frame,symbol)
                    if chart is not None: st.plotly_chart(chart,use_container_width=True,config={"displayModeBar":False},key="deploy_chart_"+symbol)
                    if news:
                        headline=news[0]
                        st.markdown("**Latest linked headline**")
                        st.write(headline.get("title","Headline unavailable"))
                        st.caption(" • ".join(x for x in [headline.get("publisher",""),headline.get("published","")] if x))
                        if headline.get("url"): st.markdown(f"[Open source]({headline['url']})")
                    else:
                        st.caption("No recent headline returned for this stock.")

        with st.expander("Price alerts · checked against the collected quote snapshot",expanded=False):
            st.caption("Set per-stock target and stop levels. Alerts appear here after a snapshot is collected; no push, email or broker actions are sent.")
            alert_hits=[]
            quotes=st.session_state.get("deploy_quotes",{})
            stored=st.session_state.setdefault("deploy_alert_levels",{})
            for symbol in [p.get("symbol") for p in packages]:
                price=quotes.get(symbol)
                saved=stored.get(symbol,{})
                ac=st.columns([1.5,1,1])
                ac[0].markdown(f"**{symbol.replace('.NS','')}**  \n"+(f"₹{price:,.2f}" if price is not None else "Price unavailable"))
                target=ac[1].number_input("Target ₹",min_value=0.0,value=float(saved.get("target",0.0)),step=1.0,key="deploy_target_"+symbol,label_visibility="collapsed")
                stop=ac[2].number_input("Stop ₹",min_value=0.0,value=float(saved.get("stop",0.0)),step=1.0,key="deploy_stop_"+symbol,label_visibility="collapsed")
                stored[symbol]={"target":target,"stop":stop}
                if price is not None and target>0 and price>=target: alert_hits.append(f"{symbol}: target reached at ₹{price:,.2f}")
                if price is not None and stop>0 and price<=stop: alert_hits.append(f"{symbol}: stop level reached at ₹{price:,.2f}")
            for alert in alert_hits: st.warning(alert)
            if not alert_hits: st.caption("No configured levels were reached by this quote snapshot.")

        if st.button("RUN LOCAL OLLAMA COMPARISON",use_container_width=True):
            try:
                with st.spinner("Local Ollama is comparing evidence for all selected stocks…"):
                    st.session_state.deploy_report=autonomous_multi_research(packages,provider="LOCAL")
            except Exception as error:
                st.error(f"Local model analysis failed: {error}")
        if st.session_state.get("deploy_report"):
            st.markdown('<div class="section">Local AI comparison</div>',unsafe_allow_html=True)
            st.markdown(st.session_state.deploy_report)

    st.markdown("### Self-learning / mistake review")
    lr=learning_report()
    c=st.columns(4)
    c[0].metric("Completed trades",lr["trades"]); c[1].metric("Win rate",f"{lr['win_rate']:.1f}%" if lr["win_rate"] is not None else "DATA"); c[2].metric("Wins",lr["wins"]); c[3].metric("Avg P&L",f"₹{lr['avg_pnl']:,.2f}" if lr["avg_pnl"] is not None else "DATA")
    st.dataframe(mistakes_by_reason(),use_container_width=True,hide_index=True)
    st.caption("OMNITRIX learns by measuring paper-trade outcomes and updating the research record. It will not silently rewrite its own strategy or risk controls.")

st.markdown("---")
st.caption(f"OMNITRIX v{APP_VERSION} • Local LLaMA • YFinance research/news • Groww feed reserved for later • Cash equities only")
