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

st.set_page_config(page_title="OMNITRIX",page_icon="◈",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
:root {
  --bg-primary: #05080e;
  --bg-card: rgba(10, 21, 33, 0.72);
  --bg-card-hover: rgba(15, 30, 48, 0.85);
  --border-cyan: rgba(54, 199, 255, 0.22);
  --neon-cyan: #36c7ff;
  --neon-green: #36d9a0;
  --neon-purple: #a855f7;
  --text-primary: #eff7ff;
  --text-secondary: #7e9bb5;
}

.stApp, [data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 50% 0%, #0b1c2d 0%, #05080e 70%) !important;
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.block-container {
  max-width: 1740px;
  padding: 16px 28px 40px;
  animation: omniFadeIn 400ms cubic-bezier(.16, 1, .3, 1) both;
}

header[data-testid="stHeader"] { background: transparent !important; }
p, span, label, h1, h2, h3, h4, h5 { color: var(--text-primary); }

input, textarea, [data-baseweb="select"] > div {
  background: rgba(8, 17, 29, 0.9) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-cyan) !important;
  border-radius: 8px !important;
  backdrop-filter: blur(8px);
}
input::placeholder, textarea::placeholder { color: #58728a !important; }

/* Enhanced Button Styling with Neon Effects */
.stButton > button {
  height: 40px;
  background: linear-gradient(135deg, rgba(13, 32, 48, 0.9) 0%, rgba(8, 20, 32, 0.9) 100%);
  color: var(--text-primary);
  border: 1px solid rgba(54, 199, 255, 0.3);
  border-radius: 8px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 11px;
  transition: all 220ms cubic-bezier(.16, 1, .3, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.stButton > button:hover {
  transform: translateY(-2px);
  border-color: var(--neon-cyan);
  background: linear-gradient(135deg, rgba(18, 48, 72, 0.95) 0%, rgba(10, 28, 45, 0.95) 100%);
  box-shadow: 0 0 16px rgba(54, 199, 255, 0.35), 0 6px 20px rgba(0, 0, 0, 0.4);
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
  border: 1px solid #38bdf8 !important;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
}

.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #0369a1 0%, #0f766e 100%) !important;
  box-shadow: 0 0 22px rgba(56, 189, 248, 0.5);
}

/* Glassmorphism Cards & Bentos */
.bento, .signal, [data-testid="stMetric"], [data-testid="stDataFrame"], [data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--bg-card) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-cyan) !important;
  border-radius: 12px !important;
  transition: all 250ms ease;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  animation: omniCardSlide 450ms cubic-bezier(.16, 1, .3, 1) both;
}

.bento:hover, .signal:hover, [data-testid="stMetric"]:hover {
  transform: translateY(-3px) scale(1.002);
  border-color: rgba(54, 199, 255, 0.5) !important;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(54, 199, 255, 0.15);
}

.bento { padding: 16px; min-height: 105px; }
.bento .label { font-size: 10px; color: var(--text-secondary); letter-spacing: 1.4px; font-weight: 800; text-transform: uppercase; }
.bento .value { font-size: 22px; font-weight: 800; margin-top: 6px; color: #f8fafc; }
.bento .sub { font-size: 11px; color: #64748b; margin-top: 4px; }

[data-testid="stMetric"] { padding: 12px 16px; }
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 10px; letter-spacing: 1.2px; font-weight: 700; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-size: 22px; font-weight: 800; }

[data-testid="stDataFrame"] { border: 1px solid var(--border-cyan); background: rgba(5, 12, 20, 0.8); }

/* Sidebar styling */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #08111b 0%, #04080e 100%) !important;
  border-right: 1px solid rgba(23, 43, 59, 0.8);
  min-width: 250px !important;
  max-width: 250px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 18px 14px 20px; }

.rail-brand {
  display: flex; align-items: center; gap: 11px; padding: 8px 5px 20px;
  border-bottom: 1px solid rgba(23, 43, 59, 0.8); margin-bottom: 18px;
}
.rail-brand-mark {
  display: grid; place-items: center; width: 36px; height: 36px; border-radius: 10px;
  color: var(--neon-cyan); font-size: 20px; font-weight: 900;
  background: linear-gradient(145deg, #10263a, #0a1420); border: 1px solid #1d4660;
  box-shadow: 0 0 20px rgba(54, 199, 255, 0.25);
  animation: pulseNeon 3s infinite ease-in-out;
}
.rail-brand-name { color: var(--text-primary); font-size: 14px; font-weight: 900; letter-spacing: 1.5px; }
.rail-brand-sub { color: var(--text-secondary); font-size: 9px; letter-spacing: 1.5px; margin-top: 3px; }

.rail-section-label { color: var(--text-secondary); font-size: 9px; letter-spacing: 1.8px; font-weight: 800; margin: 14px 7px 8px; }

[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label {
  min-height: 42px; padding: 8px 12px; border: 1px solid transparent;
  border-radius: 10px; background: transparent; transition: all 200ms ease;
  cursor: pointer;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:hover {
  background: rgba(11, 26, 40, 0.8); border-color: rgba(26, 55, 77, 0.8); transform: translateX(3px);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(54, 199, 255, 0.18), rgba(15, 35, 52, 0.2));
  border-color: rgba(54, 199, 255, 0.4); box-shadow: inset 3px 0 0 var(--neon-cyan), 0 0 12px rgba(54, 199, 255, 0.15);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p {
  color: #f8fafc !important; font-weight: 800;
}

.rail-status {
  margin-top: 22px; padding: 12px; border-radius: 10px;
  border: 1px solid rgba(25, 53, 74, 0.8); background: linear-gradient(145deg, #0a1824, #08121c);
}
.rail-status-title { color: var(--text-secondary); font-size: 9px; font-weight: 800; letter-spacing: 1.5px; }
.rail-status-mode { color: var(--neon-green); font-size: 12px; font-weight: 800; margin-top: 6px; display: flex; align-items: center; gap: 6px; }

/* Terminal Topbar & Elements */
.terminal-topbar {
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 10px 0 18px; margin-bottom: 12px; border-bottom: 1px solid rgba(20, 39, 55, 0.8);
}
.terminal-eyebrow { color: var(--neon-cyan); font-size: 9px; font-weight: 800; letter-spacing: 2px; }
.terminal-page-title { color: var(--text-primary); font-size: 22px; font-weight: 900; margin-top: 3px; letter-spacing: 0.5px; }
.terminal-top-meta { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }

.top-pill {
  display: inline-flex; align-items: center; border: 1px solid rgba(29, 57, 78, 0.9);
  background: rgba(9, 21, 33, 0.8); border-radius: 999px; padding: 5px 11px;
  color: #94a3b8; font-size: 9px; font-weight: 800; letter-spacing: 0.8px;
}
.top-pill.paper { color: var(--neon-green); border-color: rgba(32, 83, 63, 0.8); background: rgba(10, 26, 20, 0.8); }

.section { color: var(--text-primary); font-size: 18px; font-weight: 800; letter-spacing: 0.2px; margin: 16px 0 8px; }

/* Visual Pipeline Connector Cards & Flow Lines */
.pipeline-wrapper {
  margin: 16px 0 24px;
  padding: 16px;
  background: rgba(6, 14, 24, 0.7);
  border: 1px solid rgba(30, 60, 85, 0.8);
  border-radius: 14px;
  backdrop-filter: blur(10px);
}
.pipeline-title {
  font-size: 11px; font-weight: 800; letter-spacing: 1.8px; color: var(--neon-cyan); margin-bottom: 12px; text-transform: uppercase;
  display: flex; align-items: center; gap: 8px;
}
.pipeline-flow {
  display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: nowrap; overflow-x: auto; padding: 4px 0;
}
.pipeline-step {
  flex: 1; min-width: 140px; padding: 12px 14px;
  background: linear-gradient(145deg, rgba(12, 28, 44, 0.85), rgba(8, 18, 28, 0.85));
  border: 1px solid rgba(34, 68, 96, 0.7); border-radius: 10px;
  position: relative; transition: all 200ms ease;
}
.pipeline-step:hover {
  border-color: var(--neon-cyan); transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3), 0 0 12px rgba(54, 199, 255, 0.2);
}
.pipeline-step .step-badge {
  font-size: 9px; font-weight: 800; color: #0284c7; background: rgba(56, 189, 248, 0.12);
  padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 6px;
}
.pipeline-step .step-name { font-size: 12px; font-weight: 800; color: var(--text-primary); }
.pipeline-step .step-desc { font-size: 10px; color: var(--text-secondary); margin-top: 3px; }

.pipeline-arrow {
  display: flex; align-items: center; justify-content: center; color: var(--neon-cyan);
  font-size: 16px; opacity: 0.8; padding: 0 4px; animation: pulseGlow 2s infinite ease-in-out;
}

/* Status indicators and Pulse animations */
.pulse-dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--neon-green);
  display: inline-block; box-shadow: 0 0 8px var(--neon-green);
  animation: pulseDot 1.8s infinite ease-in-out;
}

/* Keyframe Animations */
@keyframes omniFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes omniCardSlide {
  from { opacity: 0; transform: translateY(10px) scale(0.99); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes pulseDot {
  0% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 4px var(--neon-green); }
  50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px var(--neon-green); }
  100% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 4px var(--neon-green); }
}
@keyframes pulseNeon {
  0%, 100% { box-shadow: 0 0 15px rgba(54, 199, 255, 0.2); }
  50% { box-shadow: 0 0 28px rgba(54, 199, 255, 0.45); }
}
@keyframes pulseGlow {
  0%, 100% { opacity: 0.5; transform: translateX(0); }
  50% { opacity: 1; transform: translateX(2px); }
}

@media (max-width: 900px) {
  [data-testid="stSidebar"] { min-width: 210px !important; max-width: 210px !important; }
  .block-container { padding-left: 14px; padding-right: 14px; }
  .terminal-topbar { align-items: flex-start; flex-direction: column; }
  .pipeline-flow { flex-direction: column; align-items: stretch; }
  .pipeline-arrow { transform: rotate(90deg); margin: 4px 0; }
}
</style>
""",unsafe_allow_html=True)

STOCKS={
"RELIANCE.NS":"Reliance Industries","TCS.NS":"Tata Consultancy Services","INFY.NS":"Infosys","HDFCBANK.NS":"HDFC Bank","ICICIBANK.NS":"ICICI Bank","SBIN.NS":"State Bank of India","BHARTIARTL.NS":"Bharti Airtel","ITC.NS":"ITC","LT.NS":"Larsen & Toubro","AXISBANK.NS":"Axis Bank","KOTAKBANK.NS":"Kotak Mahindra Bank","HINDUNILVR.NS":"Hindustan Unilever","MARUTI.NS":"Maruti Suzuki","M&M.NS":"Mahindra & Mahindra","TMPV.NS":"Tata Motors Passenger Vehicles","SUNPHARMA.NS":"Sun Pharma","ADANIENT.NS":"Adani Enterprises","ADANIPORTS.NS":"Adani Ports","NTPC.NS":"NTPC","POWERGRID.NS":"Power Grid","ONGC.NS":"ONGC","COALINDIA.NS":"Coal India","TATASTEEL.NS":"Tata Steel","JSWSTEEL.NS":"JSW Steel","HINDALCO.NS":"Hindalco","WIPRO.NS":"Wipro","HCLTECH.NS":"HCL Technologies","TECHM.NS":"Tech Mahindra","LTM.NS":"LTIMindtree","ASIANPAINT.NS":"Asian Paints","ULTRACEMCO.NS":"UltraTech Cement","TITAN.NS":"Titan","BAJFINANCE.NS":"Bajaj Finance","BAJAJFINSV.NS":"Bajaj Finserv","HDFCLIFE.NS":"HDFC Life","SBILIFE.NS":"SBI Life","DRREDDY.NS":"Dr Reddy's","CIPLA.NS":"Cipla","DIVISLAB.NS":"Divi's Laboratories","EICHERMOT.NS":"Eicher Motors","HEROMOTOCO.NS":"Hero MotoCorp","BAJAJ-AUTO.NS":"Bajaj Auto","GRASIM.NS":"Grasim","BRITANNIA.NS":"Britannia","NESTLEIND.NS":"Nestle India","TRENT.NS":"Trent","BEL.NS":"Bharat Electronics","HAL.NS":"Hindustan Aeronautics","IRCTC.NS":"IRCTC","IOC.NS":"Indian Oil","BPCL.NS":"BPCL","GAIL.NS":"GAIL","VEDL.NS":"Vedanta","ZOMATO.NS":"Zomato","DLF.NS":"DLF","PIDILITIND.NS":"Pidilite","SIEMENS.NS":"Siemens","ABB.NS":"ABB India","INDUSINDBK.NS":"IndusInd Bank","BANKBARODA.NS":"Bank of Baroda","PNB.NS":"Punjab National Bank","CANBK.NS":"Canara Bank","IDFCFIRSTB.NS":"IDFC First Bank","MOTHERSON.NS":"Samvardhana Motherson","ASHOKLEY.NS":"Ashok Leyland","TVSMOTOR.NS":"TVS Motor","APOLLOHOSP.NS":"Apollo Hospitals","MAXHEALTH.NS":"Max Healthcare","LUPIN.NS":"Lupin","AUROPHARMA.NS":"Aurobindo Pharma","DABUR.NS":"Dabur","GODREJCP.NS":"Godrej Consumer","TATACONSUM.NS":"Tata Consumer","VOLTAS.NS":"Voltas","HAVELLS.NS":"Havells","DIXON.NS":"Dixon Technologies","PERSISTENT.NS":"Persistent Systems","COFORGE.NS":"Coforge","POLYCAB.NS":"Polycab"}

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

PAGE_TITLES = {
    "MARKET": "Command Center",
    "AI": "AI Workspace",
    "RESEARCHER": "Security Researcher",
    "SCANNER": "Market Scanner",
    "AI DEPLOYED": "AI Deployed",
}
PAGE_ICONS = {
    "MARKET": "◈  Market",
    "AI": "✦  AI Workspace",
    "RESEARCHER": "⌕  Researcher",
    "SCANNER": "▦  Scanner",
    "AI DEPLOYED": "◎  AI Deployed",
}

with st.sidebar:
    st.markdown('<div class="rail-brand"><div class="rail-brand-mark">◈</div><div><div class="rail-brand-name">OMNITRIX</div><div class="rail-brand-sub">TRADING INTELLIGENCE</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="rail-section-label">WORKSPACES</div>', unsafe_allow_html=True)
    st.radio(
        "Workspace",
        options=list(PAGE_TITLES),
        format_func=lambda value: PAGE_ICONS[value],
        key="page",
        label_visibility="collapsed",
    )
    st.markdown('<div class="rail-status"><div class="rail-status-title">EXECUTION MODE</div><div class="rail-status-mode">● PAPER ONLY</div></div>', unsafe_allow_html=True)
    st.caption(f"Local model · {LOCAL_LLM_MODEL}")
    st.caption("Live orders and F&O are disabled.")

def render_pipeline_connector(active_step=1):
    steps = [
        ("1. Market Data", "Groww / YFinance Feed", "Feed"),
        ("2. Technical Matrix", "RSI, MACD, ADX, VWAP", "Indicators"),
        ("3. Pattern Engine", "Breakout & Trend Analysis", "Patterns"),
        ("4. AI Intelligence", "Local Synthesis & News", "AI Core"),
        ("5. Risk & Execution", "Sizing, Stop Loss, Ledger", "Paper Mode")
    ]
    html = '<div class="pipeline-wrapper"><div class="pipeline-title"><span>◈ OMNITRIX TRADING PIPELINE CONNECTORS</span> <span class="pulse-dot"></span></div><div class="pipeline-flow">'
    for idx, (title, desc, badge) in enumerate(steps, 1):
        is_active = (idx == active_step)
        active_style = 'border-color: var(--neon-cyan) !important; box-shadow: 0 0 16px rgba(54,199,255,0.25) !important; background: linear-gradient(145deg, rgba(16,40,64,0.95), rgba(10,25,40,0.95)) !important;' if is_active else ''
        badge_style = 'color: #38bdf8 !important; background: rgba(56, 189, 248, 0.2) !important;' if is_active else ''
        html += f'''
        <div class="pipeline-step" style="{active_style}">
            <div class="step-badge" style="{badge_style}">{badge}</div>
            <div class="step-name">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        '''
        if idx < len(steps):
            html += '<div class="pipeline-arrow">➔</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

page_title = PAGE_TITLES[st.session_state.page]
st.markdown(
    f'<div class="terminal-topbar"><div><div class="terminal-eyebrow">OMNITRIX / INDIAN EQUITIES</div><div class="terminal-page-title">{page_title}</div></div><div class="terminal-top-meta"><span class="top-pill">NSE CASH MARKET</span><span class="top-pill paper"><span class="pulse-dot" style="margin-right:6px;"></span>PAPER MODE</span><span class="terminal-muted">{datetime.now().strftime("%d %b · %H:%M")}</span></div></div>',
    unsafe_allow_html=True,
)

if st.session_state.page=="MARKET":
    render_pipeline_connector(1)
    nifty=get_nifty_price(); account=get_account()
    metric_cols=st.columns(4,gap="medium")
    cards=[
        ("NIFTY 50",f"₹{nifty:,.2f}" if nifty else "—","Index · delayed snapshot"),
        ("PAPER CASH",f"₹{account['cash']:,.0f}","Simulated account"),
        ("REALIZED P&L",f"₹{account['realized_pnl']:,.0f}","Paper ledger"),
        ("COVERAGE",f"{len(STOCKS)}","Tracked NSE equities"),
    ]
    for col,(label,value,detail) in zip(metric_cols,cards):
        col.markdown(f'<div class="bento"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{detail}</div></div>',unsafe_allow_html=True)

    section_col,refresh_col=st.columns([2.5,1],vertical_alignment="bottom")
    with section_col:
        st.markdown('<div class="section">Market universe</div>',unsafe_allow_html=True)
        st.caption("A compact view of available quotes across the tracked universe.")
    with refresh_col:
        if st.button("REFRESH SNAPSHOT",width="stretch",key="market_refresh"):
            st.cache_data.clear(); st.rerun()

    snap=market_snapshot(list(STOCKS)[:50])
    market_col,watch_col=st.columns([1.8,1],gap="large")
    with market_col:
        with st.container(border=True):
            st.markdown("**Universe quotes**")
            if not snap.empty:
                display=snap.copy()
                display.insert(1,"company",display["symbol"].map(STOCKS))
                st.dataframe(display,width="stretch",hide_index=True,height=560)
            else:
                st.info("No quotes are available right now. Check the configured market-data providers and refresh.")
    with watch_col:
        with st.container(border=True):
            st.markdown("**Watchlist focus**")
            st.caption("Latest available snapshots · source shown per symbol")
            if not snap.empty:
                watch=snap[snap["symbol"].isin(st.session_state.market_watchlist)]
                if watch.empty:
                    st.info("No watchlist quotes returned in this snapshot.")
                else:
                    for _,row in watch.iterrows():
                        symbol=str(row["symbol"])
                        feed=str(row.get("feed",""))
                        price=float(row["price"])
                        st.markdown(
                            f'<div class="watch-row"><div><div class="watch-symbol">{symbol.replace(".NS","")}</div><div class="watch-name">{STOCKS.get(symbol,symbol)}</div></div><div><div class="watch-price">₹{price:,.2f}</div><div class="watch-feed">{feed}</div></div></div>',
                            unsafe_allow_html=True,
                        )
                feeds=snap["feed"].value_counts().to_dict() if "feed" in snap else {}
                groww=int(feeds.get("GROWW",0))
                yahoo=int(feeds.get("YFINANCE",0))
                st.markdown('<div class="section">Feed coverage</div>',unsafe_allow_html=True)
                st.metric("Quotes returned",f"{len(snap)} / 50")
                st.caption(f"Groww {groww} · Yahoo Finance fallback {yahoo}")
            else:
                st.info("Feed coverage will appear after quotes are available.")
    st.caption("Market data may be delayed. This screen is for research and paper mode; it does not send broker orders.")

elif st.session_state.page=="AI":
    render_pipeline_connector(4)
    st.caption(f"Local model · {LOCAL_LLM_MODEL} · Questions run only when submitted")
    left,right=st.columns([1.7,1],gap="large")
    with left:
        with st.container(border=True):
            st.markdown("**Research conversation**")
            st.caption("Use the supplied market evidence for stock-specific analysis. OMNITRIX does not place orders.")
            if not st.session_state.chat:
                with st.chat_message("assistant"):
                    st.markdown("I can help compare setups, chart patterns, news reactions and exit rules. Ask a question to begin.")
            for message in st.session_state.chat[-12:]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            prompt=st.chat_input("Ask about a setup, pattern, news reaction, exit rule or research question")
            if prompt:
                st.session_state.chat.append({"role":"user","content":prompt})
                prior="\n".join(f'{m["role"]}: {m["content"]}' for m in st.session_state.chat[-8:])
                try:
                    with st.spinner("Local model is preparing a research response…"):
                        ans=ai_call(prior+"\nAnswer as an evidence-first Indian equity research assistant. Separate supplied facts from interpretation, state missing data, and do not place orders.",provider="LOCAL")
                except Exception as e:
                    ans="Local AI is unavailable: "+str(e)
                st.session_state.chat.append({"role":"assistant","content":ans})
                st.rerun()
    with right:
        st.markdown('<div class="bento"><div class="label">PATTERN MEMORY</div><div class="value">Human → Rule</div><div class="sub">Describe your trading pattern and convert it into testable conditions.</div></div>',unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**Rule draft**")
            st.caption("A draft is for review. Saving it does not activate paper or live execution.")
            p=st.text_area("Pattern description","Example: breakout + volume expansion + positive news + EMA trend.",key="ai_pattern_description")
            if st.button("CONVERT TO RULE",type="primary",width="stretch",key="convert_pattern_rule"):
                try:
                    with st.spinner("Local model is structuring the rule…"):
                        rule=ai_call("Convert this idea into deterministic entry conditions, confirmation, invalidation, exit and risk rules. Return a concise checklist. Do not create a trade or claim the rule is validated.\n"+p,provider="LOCAL")
                    st.session_state.ai_rule_draft=rule
                except Exception as e:
                    st.error(str(e))
            if st.session_state.get("ai_rule_draft"):
                st.markdown(st.session_state.ai_rule_draft)

elif st.session_state.page=="RESEARCHER":
    render_pipeline_connector(2)
    st.caption("Price action, fundamentals, technical state, historical patterns and source-linked news in one research view.")
    selector_col,action_col=st.columns([3,1],vertical_alignment="bottom")
    with selector_col:
        symbols=list(STOCKS)
        selected=st.selectbox("Security",symbols,index=symbols.index(st.session_state.selected),format_func=lambda s:f"{STOCKS[s]}  •  {s}",key="research_security")
    st.session_state.selected=selected
    with action_col:
        load_package=st.button("LOAD RESEARCH PACKAGE",type="primary",width="stretch",key="load_research_package")
    if load_package:
        try:
            with st.spinner("Loading price history, intraday data, indicators, patterns and news…"):
                st.session_state.pkg=research_stock(selected)
                st.session_state.report=""
        except Exception as error:
            st.error(f"Research package could not be loaded: {error}")

    package=st.session_state.pkg
    if not package or package.get("symbol")!=selected:
        st.info("Choose a security and load its research package to populate this page from the configured data sources.")
    else:
        technical=package.get("technical",{}) or {}
        fundamentals=package.get("fundamentals",{}) or {}
        patterns=package.get("patterns",[]) or []
        news=package.get("news",[]) or []
        quality="HIGH" if technical.get("close") is not None and news and not fundamentals.get("error") else "PARTIAL"
        st.caption(f"{STOCKS[selected]} · {selected.replace('.NS','')} · Quality: {quality} · Quote may be delayed")
        metric_cols=st.columns(5)
        metrics=[("LAST PRICE",technical.get("close")),("RSI · 14",technical.get("rsi")),("ADX · 14",technical.get("adx")),("VOLUME RATIO",technical.get("volume_ratio")),("PATTERN",patterns[0].get("pattern") if patterns else "NO CLEAR SETUP")]
        for col,(label,value) in zip(metric_cols,metrics):
            shown=value if isinstance(value,str) else f"{float(value):,.2f}" if value is not None else "DATA"
            col.metric(label,shown)

        chart_col,detail_col=st.columns([1.75,1],gap="large")
        chart_frame=package.get("intraday")
        if chart_frame is None or chart_frame.empty:
            chart_frame=package.get("history")
        with chart_col:
            with st.container(border=True):
                st.markdown("**Price & volume**")
                st.caption("Intraday candles when available, with daily history as fallback.")
                if chart_frame is not None and not chart_frame.empty:
                    st.plotly_chart(candlestick_chart(chart_frame,selected),width="stretch",config={"displayModeBar":False},key="research_candles_"+selected)
                    st.plotly_chart(volume_chart(chart_frame),width="stretch",config={"displayModeBar":False},key="research_volume_"+selected)
                else:
                    st.info("Price history is unavailable for this security.")
        with detail_col:
            with st.container(border=True):
                st.markdown("**Technical state**")
                technical_rows=[
                    ("EMA 9 / 21", "Bullish" if technical.get("ema9") is not None and technical.get("ema21") is not None and technical["ema9"]>technical["ema21"] else "Mixed / unavailable"),
                    ("RSI", f"{float(technical['rsi']):.1f}" if technical.get("rsi") is not None else "Unavailable"),
                    ("MACD", "Positive" if technical.get("macd") is not None and technical.get("macd_signal") is not None and technical["macd"]>technical["macd_signal"] else "Mixed / unavailable"),
                    ("Volume", f"{float(technical['volume_ratio']):.2f}× avg" if technical.get("volume_ratio") is not None else "Unavailable"),
                    ("ATR", f"{float(technical['atr']):.2f}" if technical.get("atr") is not None else "Unavailable"),
                ]
                st.dataframe(pd.DataFrame(technical_rows,columns=["Indicator","Reading"]),width="stretch",hide_index=True)
            with st.container(border=True):
                st.markdown("**Risk register**")
                levels=package.get("levels",{}) or {}
                for key,label in [("s1","Support 1"),("pivot","Pivot"),("r1","Resistance 1")]:
                    value=levels.get(key)
                    st.caption(f"{label} · ₹{float(value):,.2f}" if isinstance(value,(int,float)) else f"{label} · unavailable")
                st.caption(f"Sector · {fundamentals.get('sector') or 'unavailable'}")
                st.caption(f"Debt / equity · {fundamentals.get('debtToEquity') if fundamentals.get('debtToEquity') is not None else 'unavailable'}")

        with st.container(border=True):
            st.markdown("**Evidence matrix · news, price and chart**")
            match=package.get("news_match",{}) or {}
            evidence=st.columns(3)
            evidence[0].markdown(f'<div class="signal"><div class="head">NEWS</div><div class="body">{match.get("bias","NEUTRAL")} · score {match.get("score",0)}<br>{match.get("headline","No recent headline")}</div></div>',unsafe_allow_html=True)
            evidence[1].markdown(f'<div class="signal"><div class="head">PRICE</div><div class="body">₹{technical.get("close",0):,.2f}<br>RSI {technical.get("rsi",0):.1f} · Volume {technical.get("volume_ratio",0):.2f}×</div></div>',unsafe_allow_html=True)
            evidence[2].markdown(f'<div class="signal"><div class="head">PATTERN</div><div class="body">{", ".join(p.get("pattern","") for p in patterns[:3]) or "No clear pattern"}<br>Historical sample: {len(package.get("pattern_history",[]))}</div></div>',unsafe_allow_html=True)

        lower_left,lower_right=st.columns([1.35,1],gap="large")
        with lower_left:
            with st.container(border=True):
                st.markdown("**Historical pattern behaviour**")
                history_table=package.get("pattern_history",pd.DataFrame())
                if isinstance(history_table,pd.DataFrame) and not history_table.empty:
                    st.dataframe(history_table,width="stretch",hide_index=True)
                else:
                    st.caption("No comparable historical pattern sample was returned.")
            with st.container(border=True):
                st.markdown("**Recent news & sources**")
                if news:
                    for item in news[:6]:
                        title=item.get("title","Headline unavailable")
                        link=item.get("url")
                        st.markdown(f"**[{title}]({link})**" if link else f"**{title}**")
                        st.caption(" · ".join(x for x in [item.get("publisher","News"),item.get("published","")] if x))
                else:
                    st.caption("No recent headlines were returned.")
        with lower_right:
            with st.container(border=True):
                st.markdown("**Fundamentals**")
                rows=[("Industry",fundamentals.get("industry")),("Trailing P/E",fundamentals.get("trailingPE")),("Revenue growth",fundamentals.get("revenueGrowth")),("Profit margin",fundamentals.get("profitMargins")),("Return on equity",fundamentals.get("returnOnEquity"))]
                st.dataframe(pd.DataFrame([(k,v if v is not None else "Unavailable") for k,v in rows],columns=["Metric","Value"]),width="stretch",hide_index=True)

        if st.button("AI DEEP RESEARCH",type="primary",width="stretch",key="research_ai_deep"):
            try:
                with st.spinner("Local model is comparing news, price, chart and pattern evidence…"):
                    st.session_state.report=autonomous_research(package,provider="LOCAL")
            except Exception as error:
                st.error(f"Deep research failed: {error}")
        if st.session_state.get("report"):
            with st.container(border=True):
                st.markdown("**Local AI research note**")
                st.markdown(st.session_state.report)

elif st.session_state.page=="SCANNER":
    render_pipeline_connector(3)
    st.caption("Filter first, review transparent indicator scores and send only a small shortlist to local AI.")
    filter_cols=st.columns([1.15,1,1,1],gap="medium")
    universe=filter_cols[0].selectbox("Universe",["NIFTY focus list","Full coverage"],key="scanner_universe")
    universe_symbols=list(STOCKS)[:50] if universe=="NIFTY focus list" else list(STOCKS)
    max_size=min(80,len(universe_symbols))
    default_size=min(50,max_size)
    scan_size=filter_cols[1].slider("Scan size",min(20,max_size),max_size,default_size,step=5,key="scanner_size")
    min_score=filter_cols[2].slider("Minimum score",-10,110,30,step=5,key="scanner_score_floor")
    setup_filter=filter_cols[3].selectbox("Setup filter",["All setups","Breakout","Trend","Pullback","Other"],key="scanner_pattern_filter")
    if st.button("SCAN UNIVERSE",type="primary",width="stretch",key="scanner_run"):
        with st.spinner(f"Parallel scan across {scan_size} securities…"):
            st.session_state.scan=scan_universe(universe_symbols,scan_size)
        st.session_state.scan_runs=st.session_state.get("scan_runs",0)+1

    result=st.session_state.get("scan",pd.DataFrame())
    if not result.empty:
        filtered=result.copy()
        if "score" in filtered:
            filtered=filtered[filtered["score"]>=min_score]
        if "pattern" in filtered:
            if setup_filter=="Breakout":
                filtered=filtered[filtered["pattern"].astype(str).str.contains("BREAKOUT",case=False,na=False)]
            elif setup_filter=="Trend":
                filtered=filtered[filtered["pattern"].astype(str).str.contains("TREND|EMA_CROSS_UP",case=False,regex=True,na=False)]
            elif setup_filter=="Pullback":
                filtered=filtered[filtered["pattern"].astype(str).str.contains("PULLBACK",case=False,na=False)]
            elif setup_filter=="Other":
                filtered=filtered[~filtered["pattern"].astype(str).str.contains("BREAKOUT|TREND|EMA_CROSS_UP|PULLBACK",case=False,regex=True,na=False)]

        stats=st.columns(4)
        stats[0].metric("SHORTLIST",len(filtered))
        stats[1].metric("AVG SCORE",f"{filtered['score'].mean():.0f}/110" if not filtered.empty and "score" in filtered else "—")
        stats[2].metric("BREAKOUTS",int(filtered["pattern"].astype(str).str.contains("BREAKOUT",case=False,na=False).sum()) if not filtered.empty and "pattern" in filtered else 0)
        stats[3].metric("SCAN RUNS",st.session_state.get("scan_runs",0))

        result_col,chart_col=st.columns([1.7,1],gap="large")
        with result_col:
            with st.container(border=True):
                st.markdown("**Shortlist results**")
                st.caption("Scores combine indicator checks and the detected pattern. Candidates require review.")
                shown=[c for c in ["symbol","price","score","pattern","rsi","volume_ratio","adx"] if c in filtered.columns]
                st.dataframe(filtered[shown],width="stretch",hide_index=True,height=390)
        with chart_col:
            with st.container(border=True):
                st.markdown("**Score distribution**")
                if not filtered.empty and "score" in filtered and "symbol" in filtered:
                    top=filtered.head(12).iloc[::-1]
                    figure=go.Figure(go.Bar(x=top["score"],y=top["symbol"].astype(str).str.replace(".NS","",regex=False),orientation="h",marker={"color":top["score"],"colorscale":[[0,"#21425e"],[.65,"#1677ff"],[1,"#36d9a0"]],"cmin":-10,"cmax":110,"showscale":False},hovertemplate="%{y}<br>Score %{x}/110<extra></extra>"))
                    figure.update_layout(height=360,margin={"l":4,"r":8,"t":8,"b":8},template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis={"range":[-10,110],"title":"Technical + pattern score"},yaxis={"autorange":"reversed"})
                    st.plotly_chart(figure,width="stretch",config={"displayModeBar":False},key="scanner_score_distribution")
                else:
                    st.info("No securities match these filters. Lower the score threshold or change the setup filter.")
                st.caption("Historical technical evidence is not a price forecast.")
        if not filtered.empty and st.button("SEND TOP 5 TO LOCAL AI",type="primary",width="stretch",key="scanner_ai_shortlist"):
            symbols=filtered.head(5)["symbol"].tolist()
            package_map={}
            with st.spinner("Collecting the shortlist in parallel for one local AI comparison…"):
                with ThreadPoolExecutor(max_workers=min(4,len(symbols))) as pool:
                    futures={pool.submit(research_stock,s):s for s in symbols}
                    for future in as_completed(futures):
                        symbol=futures[future]
                        try:
                            package_map[symbol]=future.result()
                        except Exception as error:
                            package_map[symbol]={"symbol":symbol,"technical":{},"fundamentals":{},"levels":{},"news":[],"patterns":[],"error":str(error)}
                try:
                    ordered=[package_map[s] for s in symbols if s in package_map]
                    st.session_state.scan_ai=autonomous_multi_research(ordered,provider="LOCAL")
                except Exception as error:
                    st.session_state.scan_ai=f"Local shortlist analysis failed: {error}"
        if st.session_state.get("scan_ai"):
            with st.container(border=True):
                st.markdown("**Local shortlist analysis**")
                st.markdown(st.session_state.scan_ai)
    else:
        st.info("Choose a universe and run a scan to see candidates ranked by price, trend, momentum, volume and chart pattern.")

elif st.session_state.page=="AI DEPLOYED":
    render_pipeline_connector(5)
    st.markdown('<div class="warn">PAPER RESEARCH ONLY. The pipeline reads market evidence and runs local AI analysis. It does not send broker orders or provide external notifications.</div>',unsafe_allow_html=True)
    status_cols=st.columns(4)
    for col,label,value,detail in zip(status_cols,["NEWS","PRICE","CHART","RISK"],["Headlines","Quote snapshot","Trend + pattern","Hard gate"],["stock-linked feed","provider may be delayed","technical context","live orders disabled"]):
        col.markdown(f'<div class="bento"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{detail}</div></div>',unsafe_allow_html=True)

    selected=st.multiselect("AI focus list · up to 6 stocks",list(STOCKS),default=st.session_state.market_watchlist[:6],max_selections=6,format_func=lambda s:f"{STOCKS[s]} • {s}",key="deploy_stocks")
    if selected!=st.session_state.get("deploy_symbols",[]):
        st.session_state.deploy_packages=[]
        st.session_state.deploy_report=""
        st.session_state.deploy_symbols=list(selected)

    if st.button("COLLECT MULTI-STOCK SNAPSHOT",width="stretch",disabled=not selected):
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
        st.dataframe(pd.DataFrame(rows),width="stretch",hide_index=True)
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
                    if chart is not None: st.plotly_chart(chart,width="stretch",config={"displayModeBar":False},key="deploy_chart_"+symbol)
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

        if st.button("RUN LOCAL OLLAMA COMPARISON",width="stretch"):
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
    st.dataframe(mistakes_by_reason(),width="stretch",hide_index=True)
    st.caption("OMNITRIX learns by measuring paper-trade outcomes and updating the research record. It will not silently rewrite its own strategy or risk controls.")

st.markdown("---")
st.caption(f"OMNITRIX v{APP_VERSION} • Local LLaMA • YFinance research/news • Groww feed reserved for later • Cash equities only")
