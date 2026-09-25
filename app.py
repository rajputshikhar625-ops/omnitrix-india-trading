import streamlit as st
import pandas as pd
from datetime import datetime
from config import APP_VERSION, LOCAL_LLM_MODEL
from market_data import market_snapshot, get_nifty_price
from research_engine import research_stock
from scanner import scan_universe
from ai_engine import ai_call, autonomous_research, test_ai
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
            try: ans=ai_call(prompt+"\nAnswer as an evidence-first trading research assistant. Do not place orders.")
            except Exception as e: ans="AI error: "+str(e)
            st.session_state.chat.append({"role":"assistant","content":ans}); st.rerun()
    with right:
        st.markdown('<div class="bento"><div class="label">PATTERN MEMORY</div><div class="value">Human → Rule</div><div class="sub">Describe your own trading pattern and OMNITRIX converts it into testable conditions.</div></div>',unsafe_allow_html=True)
        p=st.text_area("Pattern description","Example: breakout + volume expansion + positive news + EMA trend.")
        if st.button("CONVERT TO RULE",use_container_width=True):
            try: st.write(ai_call("Convert this trading idea into deterministic conditions, confirmation, invalidation, exit and risk rules. Do not invent evidence.\n"+p))
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
            with st.spinner("LLaMA comparing news + price + chart + historical pattern evidence..."): st.session_state.report=autonomous_research(p)
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
        if st.button("SEND TOP 5 TO AI",use_container_width=True):
            reports=[]
            for s in top.head(5)["symbol"]:
                try: reports.append(autonomous_research(research_stock(s)))
                except Exception as e: reports.append(f"{s}: {e}")
            st.session_state.scan_ai="\n\n---\n\n".join(reports)
        if st.session_state.get("scan_ai"): st.markdown(st.session_state.scan_ai)

elif st.session_state.page=="AI DEPLOYED":
    st.markdown('<div class="section">AI Deployed — Decision Engine</div>',unsafe_allow_html=True)
    st.markdown('<div class="warn">AUTONOMOUS LIVE TRADING IS NOT ACTIVE. The decision pipeline is being built and tested in paper mode only.</div>',unsafe_allow_html=True)
    c=st.columns(4)
    for col,l,v,s in zip(c,["NEWS","PRICE","CHART","RISK"],["Signal","Momentum","Structure","Hard gate"],["YFinance headlines","current movement","indicators + patterns","stop / loss limit"]):
        col.markdown(f'<div class="bento"><div class="label">{l}</div><div class="value">{v}</div><div class="sub">{s}</div></div>',unsafe_allow_html=True)
    selected=st.selectbox("AI focus stock",list(STOCKS),format_func=lambda s:f"{STOCKS[s]} • {s}",key="deploy_stock")
    if st.button("RUN DECISION SIMULATION",use_container_width=True):
        with st.spinner("Comparing news + current price + chart + historical pattern..."):
            p=research_stock(selected); st.session_state.deploy_pkg=p
            st.session_state.deploy_report=autonomous_research(p)
    p=st.session_state.get("deploy_pkg")
    if p:
        nm=p.get("news_match",{}); t=p["technical"]
        c=st.columns(3)
        c[0].metric("NEWS",nm.get("bias","NEUTRAL")); c[1].metric("PRICE",f"₹{t.get('close',0):,.2f}"); c[2].metric("PATTERN",p["patterns"][0]["pattern"] if p["patterns"] else "NONE")
        if st.session_state.get("deploy_report"): st.markdown(st.session_state.deploy_report)
    st.markdown("### Self-learning / mistake review")
    lr=learning_report()
    c=st.columns(4)
    c[0].metric("Completed trades",lr["trades"]); c[1].metric("Win rate",f"{lr['win_rate']:.1f}%" if lr["win_rate"] is not None else "DATA"); c[2].metric("Wins",lr["wins"]); c[3].metric("Avg P&L",f"₹{lr['avg_pnl']:,.2f}" if lr["avg_pnl"] is not None else "DATA")
    st.dataframe(mistakes_by_reason(),use_container_width=True,hide_index=True)
    st.caption("OMNITRIX learns by measuring paper-trade outcomes and updating the research record. It will not silently rewrite its own strategy or risk controls.")

st.markdown("---")
st.caption(f"OMNITRIX v{APP_VERSION} • Local LLaMA • YFinance research/news • Groww feed reserved for later • Cash equities only")
