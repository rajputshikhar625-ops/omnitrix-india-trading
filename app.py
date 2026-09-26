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

@keyframes omniPageEnter {
  from { opacity: 0; transform: translateY(10px); filter: blur(2px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}
@keyframes omniCardEnter {
  from { opacity: 0; transform: translateY(8px) scale(.992); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.block-container { animation: omniPageEnter 420ms cubic-bezier(.2,.7,.2,1) both; }
.hero { animation: omniCardEnter 480ms cubic-bezier(.2,.7,.2,1) both; }
.bento,.signal,[data-testid="stMetric"],[data-testid="stDataFrame"] {
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
  animation: omniCardEnter 460ms cubic-bezier(.2,.7,.2,1) both;
}
.bento:hover,.signal:hover,[data-testid="stMetric"]:hover {
  transform: translateY(-2px);
  border-color: #2c6687;
  box-shadow: 0 12px 28px rgba(0,0,0,.22);
}
.stButton>button {
  transition: transform 160ms ease, background 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}
.stButton>button:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 22px rgba(54,199,255,.13);
}
[data-testid="stPlotlyChart"] { animation: omniCardEnter 520ms ease both; }
@media (prefers-reduced-motion: reduce) {
  *,*::before,*::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}

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
    if nav[i].button(name+active,width="stretch",key="nav_"+name):
        st.session_state.page=name; st.rerun()

if st.session_state.page=="MARKET":
    nifty=get_nifty_price(); a=get_account()
    st.markdown('<div class="section">Command Center</div>',unsafe_allow_html=True)
    c=st.columns(5)
    cards=[("NIFTY 50",f"₹{nifty:,.2f}" if nifty else "DATA","market pulse"),("PAPER CASH",f"₹{a['cash']:,.0f}","test capital"),("REALIZED P&L",f"₹{a['realized_pnl']:,.0f}","paper ledger"),("UNIVERSE",f"{len(STOCKS)}","Indian equities"),("AI STATUS","ONLINE","local LLaMA")]
    for col,(l,v,s) in zip(c,cards):
        col.markdown(f'<div class="bento"><div class="label">{l}</div><div class="value">{v}</div><div class="sub">{s}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">Market Pulse</div>',unsafe_allow_html=True)
    if st.button("REFRESH MARKET SNAPSHOT",width="stretch"):
        st.cache_data.clear(); st.rerun()
    snap=market_snapshot(list(STOCKS)[:50])
    if not snap.empty: st.dataframe(snap,width="stretch",hide_index=True)
    st.caption("Price source: Groww LTP when configured; otherwise YFinance fallback. Exchange-grade live feed will be added only after deliberate activation.")

elif st.session_state.page=="AI":
    st.markdown('<div class="section">AI Workspace</div>',unsafe_allow_html=True)
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
    st.markdown('<div class="section">Security Researcher</div>',unsafe_allow_html=True)
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
    st.markdown('<div class="section">Market Scanner</div>',unsafe_allow_html=True)
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
