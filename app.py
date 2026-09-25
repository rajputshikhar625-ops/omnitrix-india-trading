import streamlit as st
import pandas as pd
from datetime import datetime
from config import APP_VERSION, PAPER_INITIAL_CAPITAL, LOCAL_LLM_MODEL
from market_data import market_snapshot, get_nifty_price, yahoo_history
from indicators import add_indicators
from research_engine import research_stock
from news_engine import fetch_news
from ai_engine import autonomous_research, test_ai, ai_call
from scanner import scan_universe
from charts import candlestick_chart, oscillator_chart, volume_chart
from paper_trading import get_account, buy, sell, monitor_positions
from storage import load_orders

st.set_page_config(page_title="OMNITRIX",page_icon="O",layout="wide",initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 65% -15%,#123a5b 0,#030811 42%);color:#f4f8fc}
.block-container{max-width:1800px;padding:.7rem 1.2rem 2rem}
html,body,[class*="css"]{font-family:Inter,Segoe UI,Arial,sans-serif}
p,span,label,h1,h2,h3,h4{color:#f4f8fc}
input,textarea,div[data-baseweb="select"]>div{background:#071321!important;color:#f4f8fc!important;border:1px solid #24445f!important}
input::placeholder,textarea::placeholder{color:#6e879c!important}
.stButton>button{background:#0b2944;color:#fff;border:1px solid #24597a;border-radius:9px;font-weight:650}
.stButton>button:hover{background:#103b5f;border-color:#4ee7ff}
[data-testid="stMetric"]{background:#071321;border:1px solid #19324a;border-radius:12px}
[data-testid="stDataFrame"]{border:1px solid #19324a;border-radius:12px}
.hero{border:1px solid #21415e;border-radius:18px;padding:24px 28px;margin-bottom:12px;background:linear-gradient(120deg,rgba(6,19,33,.98),rgba(7,33,55,.9))}
.hero .tag{color:#4ee7ff;font-size:.76rem;font-weight:800;letter-spacing:2px}
.hero h1{font-size:2.2rem;margin:.15rem 0}
.hero p{color:#a9bdd0;margin:.25rem 0}
.navhint{color:#7f98ad;font-size:.78rem;margin-bottom:8px}
.bento{border:1px solid #19324a;border-radius:14px;padding:16px;background:linear-gradient(145deg,#071321,#0a1c2e);min-height:130px;margin-bottom:10px}
.bento h3{font-size:1rem;margin:0 0 7px}
.bento .big{font-size:1.4rem;font-weight:750}
.card{border:1px solid #19324a;border-radius:14px;padding:14px;background:#071321;margin-bottom:12px}
.green{color:#22d39b}.red{color:#ff6170}.muted{color:#8da1b6}
</style>
""",unsafe_allow_html=True)

STOCKS={
"RELIANCE.NS":"Reliance Industries","TCS.NS":"Tata Consultancy Services","INFY.NS":"Infosys","HDFCBANK.NS":"HDFC Bank",
"ICICIBANK.NS":"ICICI Bank","SBIN.NS":"State Bank of India","BHARTIARTL.NS":"Bharti Airtel","ITC.NS":"ITC",
"LT.NS":"Larsen & Toubro","AXISBANK.NS":"Axis Bank","KOTAKBANK.NS":"Kotak Mahindra Bank","HINDUNILVR.NS":"Hindustan Unilever",
"MARUTI.NS":"Maruti Suzuki","M&M.NS":"Mahindra & Mahindra","TATAMOTORS.NS":"Tata Motors","SUNPHARMA.NS":"Sun Pharma",
"ADANIENT.NS":"Adani Enterprises","ADANIPORTS.NS":"Adani Ports","NTPC.NS":"NTPC","POWERGRID.NS":"Power Grid",
"ONGC.NS":"ONGC","COALINDIA.NS":"Coal India","TATASTEEL.NS":"Tata Steel","JSWSTEEL.NS":"JSW Steel",
"HINDALCO.NS":"Hindalco","WIPRO.NS":"Wipro","HCLTECH.NS":"HCL Technologies","TECHM.NS":"Tech Mahindra",
"LTIM.NS":"LTIMindtree","ASIANPAINT.NS":"Asian Paints","ULTRACEMCO.NS":"UltraTech Cement","TITAN.NS":"Titan",
"BAJFINANCE.NS":"Bajaj Finance","BAJAJFINSV.NS":"Bajaj Finserv","HDFCLIFE.NS":"HDFC Life","SBILIFE.NS":"SBI Life",
"DRREDDY.NS":"Dr Reddy's","CIPLA.NS":"Cipla","DIVISLAB.NS":"Divi's Laboratories","EICHERMOT.NS":"Eicher Motors",
"HEROMOTOCO.NS":"Hero MotoCorp","BAJAJ-AUTO.NS":"Bajaj Auto","GRASIM.NS":"Grasim","BRITANNIA.NS":"Britannia",
"NESTLEIND.NS":"Nestle India","TRENT.NS":"Trent","BEL.NS":"Bharat Electronics","HAL.NS":"Hindustan Aeronautics",
"IRCTC.NS":"IRCTC","IOC.NS":"Indian Oil","BPCL.NS":"BPCL","GAIL.NS":"GAIL","VEDL.NS":"Vedanta","ZOMATO.NS":"Zomato",
"DLF.NS":"DLF","PIDILITIND.NS":"Pidilite","SIEMENS.NS":"Siemens","ABB.NS":"ABB India","INDUSINDBK.NS":"IndusInd Bank",
"BANKBARODA.NS":"Bank of Baroda","PNB.NS":"Punjab National Bank","CANBK.NS":"Canara Bank","IDFCFIRSTB.NS":"IDFC First Bank",
"MOTHERSON.NS":"Samvardhana Motherson","ASHOKLEY.NS":"Ashok Leyland","TVSMOTOR.NS":"TVS Motor","APOLLOHOSP.NS":"Apollo Hospitals",
"MAXHEALTH.NS":"Max Healthcare","LUPIN.NS":"Lupin","AUROPHARMA.NS":"Aurobindo Pharma","DABUR.NS":"Dabur","GODREJCP.NS":"Godrej Consumer",
"TATACONSUM.NS":"Tata Consumer","VOLTAS.NS":"Voltas","HAVELLS.NS":"Havells","DIXON.NS":"Dixon Technologies","PERSISTENT.NS":"Persistent Systems",
"COFORGE.NS":"Coforge","POLYCAB.NS":"Polycab"}

if "page" not in st.session_state: st.session_state.page="MARKET"
if "symbol" not in st.session_state: st.session_state.symbol="RELIANCE.NS"
if "report" not in st.session_state: st.session_state.report=""
if "chat" not in st.session_state: st.session_state.chat=[]

st.markdown(f'<div class="hero"><div class="tag">ANALYZE • REASON • TRADE</div><h1>OMNITRIX</h1><p>AI-powered Indian cash-equity intelligence terminal</p><p>Local {LOCAL_LLM_MODEL} • Paper environment • F&O disabled • Live execution disabled • v{APP_VERSION}</p></div>',unsafe_allow_html=True)

nav=st.columns(5)
for i,name in enumerate(["MARKET","AI","RESEARCHER","SCANNER","AI DEPLOYED"]):
    if nav[i].button(name,use_container_width=True,key="nav_"+name):
        st.session_state.page=name
        st.rerun()

# MARKET
if st.session_state.page=="MARKET":
    nifty=get_nifty_price(); account=get_account()
    c=st.columns(4)
    c[0].metric("NIFTY 50",f"₹{nifty:,.2f}" if nifty else "DATA")
    c[1].metric("Paper Cash",f"₹{account['cash']:,.0f}")
    c[2].metric("Realized P&L",f"₹{account['realized_pnl']:,.0f}")
    c[3].metric("AI", "ONLINE")
    st.markdown("### Bento command center")
    b=st.columns(4)
    for col,title,big,sub in [
        (b[0],"MARKET","Indian Equities","NSE/BSE research"),
        (b[1],"AI",LOCAL_LLM_MODEL,"Local reasoning"),
        (b[2],"RESEARCHER","Multi-source","Fundamental + technical"),
        (b[3],"SCANNER","50 STOCKS","Fast opportunity scan")]:
        with col: st.markdown(f'<div class="bento"><h3>{title}</h3><div class="big">{big}</div><div class="muted">{sub}</div></div>',unsafe_allow_html=True)
    st.markdown("### Market")
    snap=market_snapshot(list(STOCKS)[:30])
    if not snap.empty: st.dataframe(snap,use_container_width=True,hide_index=True)

# AI
elif st.session_state.page=="AI":
    st.subheader("AI")
    st.caption("Chat with local Llama and turn your trading observations into explicit, testable pattern rules.")
    for m in st.session_state.chat[-10:]:
        st.chat_message(m["role"]).markdown(m["content"])
    prompt=st.chat_input("Ask OMNITRIX about a pattern, chart setup, news impact or rule")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        try:
            ans=ai_call("User request:\n"+prompt+"\nGive a concise, evidence-first answer. If discussing a trading pattern, specify conditions, invalidation and uncertainty.",temperature=.15)
        except Exception as e: ans=f"AI error: {e}"
        st.session_state.chat.append({"role":"assistant","content":ans})
        st.rerun()
    st.markdown("### Pattern training")
    p=st.text_area("Describe your pattern","Example: price breaks resistance, volume expands, trend is above EMA21, news confirms the move.")
    if st.button("ANALYZE PATTERN"):
        try: st.markdown(ai_call("Convert this user pattern into a deterministic research rule. Identify entry evidence, confirmation, invalidation, exit logic, risk constraints and missing data. Pattern:\n"+p,temperature=.1))
        except Exception as e: st.error(str(e))

# RESEARCHER
elif st.session_state.page=="RESEARCHER":
    symbols=list(STOCKS)
    selected=st.selectbox("Security",symbols,index=symbols.index(st.session_state.symbol),format_func=lambda s:f"{STOCKS[s]} • {s}")
    st.session_state.symbol=selected
    if st.button("LOAD FULL RESEARCH",use_container_width=True):
        with st.spinner("Collecting market, technical, fundamental and news evidence..."):
            st.session_state.pkg=research_stock(selected)
    pkg=st.session_state.get("pkg")
    if pkg:
        t=pkg["technical"]; q=st.columns(5)
        q[0].metric("Price",f"₹{t.get('close',0):,.2f}"); q[1].metric("RSI",f"{t.get('rsi',0):.1f}")
        q[2].metric("ADX",f"{t.get('adx',0):.1f}"); q[3].metric("Volume",f"{t.get('volume_ratio',0):.2f}x"); q[4].metric("ATR",f"{t.get('atr',0):.2f}")
        st.plotly_chart(candlestick_chart(pkg["history"],selected),use_container_width=True)
        x,y=st.columns(2)
        with x: st.plotly_chart(volume_chart(pkg["history"]),use_container_width=True)
        with y: st.plotly_chart(oscillator_chart(pkg["history"],["rsi","stoch_k","stoch_d"],"Momentum"),use_container_width=True)
        st.markdown("### Recent news")
        for item in pkg["news"][:10]: st.markdown(f"**{item['title']}**  \n<span class='muted'>{item['publisher']} • {item['published']}</span>",unsafe_allow_html=True)
        if st.button("RUN AI DEEP RESEARCH"):
            with st.spinner("Llama is synthesizing supplied evidence..."):
                st.session_state.report=autonomous_research(pkg)
        if st.session_state.report: st.markdown(st.session_state.report)

# SCANNER
elif st.session_state.page=="SCANNER":
    st.subheader("Scanner")
    st.caption("The scanner checks a large universe first; AI is reserved for the shortlist.")
    n=st.slider("Universe",20,min(80,len(STOCKS)),50)
    if st.button("RUN 50-STOCK SCAN",use_container_width=True):
        with st.spinner("Scanning technical conditions..."):
            st.session_state.scan=scan_universe(list(STOCKS),limit=n)
    result=st.session_state.get("scan",pd.DataFrame())
    if not result.empty:
        st.dataframe(result,use_container_width=True,hide_index=True)
        st.markdown("### Chart scanner")
        st.info("Current chart scanner uses EMA/SMA, RSI, MACD, VWAP, volume, ADX, MFI and related indicators. Advanced named patterns can be added to the rule library next.")

# AI DEPLOYED
elif st.session_state.page=="AI DEPLOYED":
    st.subheader("AI Deployed")
    st.warning("This environment is paper-only. Live broker execution is disabled.")
    a,b,c=st.columns(3)
    a.metric("AI", "ONLINE"); b.metric("Model",LOCAL_LLM_MODEL); c.metric("Execution","PAPER")
    st.markdown("### Three-signal reasoning panel")
    cols=st.columns(3)
    for col,title,body in [
        (cols[0],"NEWS","Good / bad / neutral + relevance"),
        (cols[1],"PRICE","Up / down / mixed + momentum"),
        (cols[2],"CHART","EMA • RSI • MACD • VWAP • Volume • ADX")]:
        with col: st.markdown(f'<div class="bento"><h3>{title}</h3><div class="muted">{body}</div></div>',unsafe_allow_html=True)
    selected=st.selectbox("Focus stock",list(STOCKS),format_func=lambda s:f"{STOCKS[s]} • {s}")
    if st.button("RUN AI ANALYSIS",use_container_width=True):
        with st.spinner("Matching market, chart and news evidence..."):
            pkg=research_stock(selected)
            st.session_state.deploy_report=autonomous_research(pkg)
    if st.session_state.get("deploy_report"): st.markdown(st.session_state.deploy_report)
    st.markdown("### Paper position controls")
    st.caption("Automatic exit monitoring is available in the paper engine; it does not connect to a broker.")
    acct=get_account()
    if acct["positions"]: st.json(acct["positions"])
    else: st.info("No paper positions yet.")

st.markdown("---")
st.caption("OMNITRIX • Local AI • Indian cash equities • F&O disabled • live execution disabled")
