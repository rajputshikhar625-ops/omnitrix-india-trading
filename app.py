import streamlit as st
import pandas as pd
import numpy as np

from config import (
    APP_NAME,
    APP_VERSION,
    PAPER_INITIAL_CAPITAL,
    BLUE,
    BLUE_LIGHT,
    WHITE,
    BLACK,
    GREY,
    GREEN,
    RED,
    AMBER
)

from market_data import (
    yahoo_history,
    market_snapshot,
    get_nifty_price
)

from indicators import (
    add_indicators,
    technical_snapshot
)

from research_engine import (
    research_stock
)

from news_engine import (
    fetch_news
)

from ai_engine import (
    autonomous_research,
    test_ai
)

from scanner import (
    scan_universe
)

from charts import (
    candlestick_chart,
    oscillator_chart,
    volume_chart
)

from paper_trading import (
    get_account,
    buy,
    sell,
    equity,
    daily_pnl,
    monitor_positions,
    check_daily_lock
)

from storage import (
    load_orders,
    log
)


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="OMNITRIX TERMINAL",
    page_icon="O",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family:
        Inter,
        Segoe UI,
        Arial,
        sans-serif;
}

.stApp {
    background:
        #050b12;
    color:
        #f4f8fc;
}

section[data-testid="stSidebar"] {
    background:
        #07101a;
    border-right:
        1px solid #223247;
}

section[data-testid="stSidebar"] * {
    color:
        #f4f8fc !important;
}

h1, h2, h3, h4 {
    color:
        #f4f8fc !important;
}

p, span, label {
    color:
        #dce6f0;
}

input,
textarea {
    background:
        #ffffff !important;

    color:
        #07101a !important;

    border:
        1px solid #718096 !important;
}

input::placeholder {
    color:
        #516274 !important;
}

div[data-baseweb="select"] > div {
    background:
        #ffffff !important;

    color:
        #07101a !important;

    border:
        1px solid #718096 !important;
}

div[data-baseweb="select"] span {
    color:
        #07101a !important;
}

button {
    border-radius:
        5px !important;
}

.stButton > button {
    background:
        #1677ff;

    color:
        #ffffff;

    border:
        1px solid #55a4ff;

    font-weight:
        600;
}

.stButton > button:hover {
    background:
        #0d5dcc;

    border-color:
        #7ab8ff;
}

[data-testid="stMetric"] {
    background:
        #0b1420;

    border:
        1px solid #223247;

    padding:
        15px;

    border-radius:
        6px;
}

[data-testid="stDataFrame"] {
    border:
        1px solid #223247;
}

.omni-header {
    background:
        #07101a;

    border:
        1px solid #223247;

    padding:
        14px 20px;

    border-radius:
        7px;

    margin-bottom:
        14px;
}

.omni-title {
    color:
        #ffffff;

    font-size:
        24px;

    font-weight:
        700;

    letter-spacing:
        1px;
}

.omni-subtitle {
    color:
        #91a1b4;

    font-size:
        12px;
}

.status-online {
    color:
        #20c997;

    font-weight:
        700;
}

.status-offline {
    color:
        #ff5c69;

    font-weight:
        700;
}

.panel {
    background:
        #0b1420;

    border:
        1px solid #223247;

    border-radius:
        6px;

    padding:
        14px;

    margin-bottom:
        12px;
}

.command {
    background:
        #101c2a;

    border:
        1px solid #1677ff;

    padding:
        8px 12px;

    border-radius:
        5px;

    color:
        #ffffff;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# STOCK UNIVERSE
# =========================================================

STOCKS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "ITC.NS": "ITC",
    "LT.NS": "Larsen & Toubro",
    "AXISBANK.NS": "Axis Bank",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "MARUTI.NS": "Maruti Suzuki",
    "M&M.NS": "Mahindra & Mahindra",
    "TATAMOTORS.NS": "Tata Motors",
    "SUNPHARMA.NS": "Sun Pharma",
    "ADANIENT.NS": "Adani Enterprises",
    "ADANIPORTS.NS": "Adani Ports",
    "NTPC.NS": "NTPC",
    "POWERGRID.NS": "Power Grid",
    "ONGC.NS": "ONGC",
    "COALINDIA.NS": "Coal India",
    "TATASTEEL.NS": "Tata Steel",
    "JSWSTEEL.NS": "JSW Steel",
    "HINDALCO.NS": "Hindalco",
    "WIPRO.NS": "Wipro",
    "HCLTECH.NS": "HCL Technologies",
    "TECHM.NS": "Tech Mahindra",
    "LTIM.NS": "LTIMindtree",
    "ASIANPAINT.NS": "Asian Paints",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "TITAN.NS": "Titan",
    "BAJFINANCE.NS": "Bajaj Finance",
    "BAJAJFINSV.NS": "Bajaj Finserv",
    "HDFCLIFE.NS": "HDFC Life",
    "SBILIFE.NS": "SBI Life",
    "DRREDDY.NS": "Dr Reddy's",
    "CIPLA.NS": "Cipla",
    "DIVISLAB.NS": "Divi's Laboratories",
    "EICHERMOT.NS": "Eicher Motors",
    "HEROMOTOCO.NS": "Hero MotoCorp",
    "BAJAJ-AUTO.NS": "Bajaj Auto",
    "GRASIM.NS": "Grasim",
    "BRITANNIA.NS": "Britannia",
    "NESTLEIND.NS": "Nestle India",
    "TRENT.NS": "Trent",
    "BEL.NS": "Bharat Electronics",
    "HAL.NS": "Hindustan Aeronautics",
    "IRCTC.NS": "IRCTC",
    "IOC.NS": "Indian Oil",
    "BPCL.NS": "BPCL",
    "GAIL.NS": "GAIL",
    "VEDL.NS": "Vedanta",
    "ZOMATO.NS": "Zomato",
    "DLF.NS": "DLF",
    "PIDILITIND.NS": "Pidilite",
    "SIEMENS.NS": "Siemens",
    "ABB.NS": "ABB India",
    "INDUSINDBK.NS": "IndusInd Bank",
    "BANKBARODA.NS": "Bank of Baroda",
    "PNB.NS": "Punjab National Bank",
    "CANBK.NS": "Canara Bank",
    "IDFCFIRSTB.NS": "IDFC First Bank",
    "MOTHERSON.NS": "Samvardhana Motherson",
    "ASHOKLEY.NS": "Ashok Leyland",
    "TVSMOTOR.NS": "TVS Motor",
    "APOLLOHOSP.NS": "Apollo Hospitals",
    "MAXHEALTH.NS": "Max Healthcare",
    "LUPIN.NS": "Lupin",
    "AUROPHARMA.NS": "Aurobindo Pharma",
    "DABUR.NS": "Dabur",
    "GODREJCP.NS": "Godrej Consumer",
    "TATACONSUM.NS": "Tata Consumer",
    "VOLTAS.NS": "Voltas",
    "HAVELLS.NS": "Havells",
    "DIXON.NS": "Dixon Technologies",
    "PERSISTENT.NS": "Persistent Systems",
    "COFORGE.NS": "Coforge",
    "POLYCAB.NS": "Polycab"
}


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "OVERVIEW"

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = (
        "RELIANCE.NS"
    )

if "ai_report" not in st.session_state:
    st.session_state.ai_report = ""

if "scanner_result" not in st.session_state:
    st.session_state.scanner_result = pd.DataFrame()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    f"""
<div class="omni-header">

<div class="omni-title">
OMNITRIX TERMINAL
</div>

<div class="omni-subtitle">
Indian Cash Equity Intelligence System
&nbsp; | &nbsp;
Version {APP_VERSION}
&nbsp; | &nbsp;
AI DIRECT ORDER AUTHORITY: NONE
</div>

</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# TOP SEARCH
# =========================================================

search = st.text_input(
    "GLOBAL SEARCH",
    placeholder=(
        "Search stock / company / NSE symbol..."
    ),
    key="global_search"
)

if search:

    query = search.lower().strip()

    matches = []

    for symbol, name in STOCKS.items():

        if (
            query in symbol.lower()
            or
            query in name.lower()
        ):
            matches.append(
                symbol
            )

    if matches:

        selected = st.selectbox(
            "Search results",
            matches
        )

        if st.button(
            "OPEN RESEARCH"
        ):

            st.session_state.selected_symbol = (
                selected
            )

            st.session_state.page = (
                "STOCK RESEARCH"
            )

            st.rerun()

    else:

        st.warning(
            "No matching stock found."
        )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    "### OMNITRIX"
)

pages = [
    "OVERVIEW",
    "MARKETS",
    "SCANNER",
    "STOCK RESEARCH",
    "WATCHLIST",
    "NEWS",
    "THEMES",
    "IPOs",
    "PORTFOLIO",
    "POSITIONS",
    "ORDERS",
    "AI DEPLOYMENT",
    "AI RESEARCH",
    "STRATEGY LAB",
    "BACKTESTING",
    "PAPER TRADING",
    "RISK",
    "TRADE JOURNAL",
    "SYSTEM LOGS",
    "SETTINGS"
]

for page in pages:

    if st.sidebar.button(
        page,
        key=f"nav_{page}"
    ):

        st.session_state.page = page

        st.rerun()


st.sidebar.divider()

st.sidebar.caption(
    "MARKET: NSE / BSE"
)

st.sidebar.caption(
    "MODE: CASH EQUITY"
)

st.sidebar.caption(
    "F&O: DISABLED"
)

st.sidebar.caption(
    "LIVE ORDERS: DISABLED"
)


# =========================================================
# MARKET STATUS
# =========================================================

nifty_price = get_nifty_price()

account = get_account()

prices = {}

if nifty_price:
    prices["^NSEI"] = nifty_price


# =========================================================
# OVERVIEW
# =========================================================

if st.session_state.page == "OVERVIEW":

    st.header(
        "Market Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "NIFTY",
        (
            f"₹{nifty_price:,.2f}"
            if nifty_price
            else "DATA"
        )
    )

    col2.metric(
        "Paper Cash",
        f"₹{account['cash']:,.0f}"
    )

    col3.metric(
        "Realized P&L",
        f"₹{account['realized_pnl']:,.2f}"
    )

    col4.metric(
        "Paper Status",
        (
            "LOCKED"
            if account["trading_locked"]
            else "ACTIVE"
        )
    )

    st.subheader(
        "Market Snapshot"
    )

    snapshot = market_snapshot(
        list(STOCKS.keys())[:20]
    )

    if not snapshot.empty:

        st.dataframe(
            snapshot,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# MARKETS
# =========================================================

elif st.session_state.page == "MARKETS":

    st.header(
        "Live Market"
    )

    symbols = list(
        STOCKS.keys()
    )

    snapshot = market_snapshot(
        symbols
    )

    if not snapshot.empty:

        st.dataframe(
            snapshot,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "Groww LTP is used when configured. "
        "Otherwise yfinance is used as fallback."
    )


# =========================================================
# SCANNER
# =========================================================

elif st.session_state.page == "SCANNER":

    st.header(
        "Market Scanner"
    )

    st.write(
        "Deterministic screening runs before AI research."
    )

    limit = st.slider(
        "Stocks to scan",
        20,
        len(STOCKS),
        min(50, len(STOCKS))
    )

    if st.button(
        "RUN MARKET SCAN"
    ):

        with st.spinner(
            "Scanning market..."
        ):

            result = scan_universe(
                list(STOCKS.keys()),
                limit=limit
            )

            st.session_state.scanner_result = (
                result
            )

    result = st.session_state.scanner_result

    if not result.empty:

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "The scanner ranks candidates "
            "using deterministic technical conditions. "
            "Llama is not called for every stock."
        )


# =========================================================
# STOCK RESEARCH
# =========================================================

elif st.session_state.page == "STOCK RESEARCH":

    st.header(
        "Stock Research"
    )

    symbols = list(
        STOCKS.keys()
    )

    selected = st.selectbox(
        "Select security",
        symbols,
        index=symbols.index(
            st.session_state.selected_symbol
        )
        if st.session_state.selected_symbol in symbols
        else 0
    )

    st.session_state.selected_symbol = selected

    company = STOCKS[
        selected
    ]

    st.caption(
        f"{company} | {selected}"
    )

    if st.button(
        "LOAD FULL RESEARCH"
    ):

        with st.spinner(
            "Collecting market, technical, fundamental and news data..."
        ):

            package = research_stock(
                selected
            )

            st.session_state[
                "research_package"
            ] = package

    package = st.session_state.get(
        "research_package"
    )

    if package:

        technical = package[
            "technical"
        ]

        fundamentals = package[
            "fundamentals"
        ]

        levels = package[
            "levels"
        ]

        news = package[
            "news"
        ]

        st.subheader(
            "Research Snapshot"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Price",
            (
                f"₹{technical.get('close', 0):,.2f}"
                if technical.get("close")
                else "N/A"
            )
        )

        col2.metric(
            "RSI",
            (
                f"{technical.get('rsi', 0):.2f}"
                if technical.get("rsi")
                else "N/A"
            )
        )

        col3.metric(
            "ADX",
            (
                f"{technical.get('adx', 0):.2f}"
                if technical.get("adx")
                else "N/A"
            )
        )

        col4.metric(
            "Volume Ratio",
            (
                f"{technical.get('volume_ratio', 0):.2f}x"
                if technical.get("volume_ratio")
                else "N/A"
            )
        )

        st.subheader(
            "Technical Chart"
        )

        df = package[
            "history"
        ]

        st.plotly_chart(
            candlestick_chart(
                df,
                selected
            ),
            use_container_width=True
        )

        st.plotly_chart(
            volume_chart(
                df
            ),
            use_container_width=True
        )

        c1, c2 = st.columns(2)

        with c1:

            st.plotly_chart(
                oscillator_chart(
                    df,
                    [
                        "rsi",
                        "stoch_k",
                        "stoch_d"
                    ],
                    "Momentum"
                ),
                use_container_width=True
            )

        with c2:

            st.plotly_chart(
                oscillator_chart(
                    df,
                    [
                        "macd",
                        "macd_signal",
                        "macd_hist"
                    ],
                    "MACD"
                ),
                use_container_width=True
            )

        st.subheader(
            "Technical Indicators"
        )

        st.dataframe(
            pd.DataFrame(
                [
                    technical
                ]
            ).T.rename(
                columns={0: "Value"}
            ),
            use_container_width=True
        )

        st.subheader(
            "Support / Resistance"
        )

        st.json(
            levels
        )

        st.subheader(
            "Fundamentals"
        )

        st.json(
            fundamentals
        )

        st.subheader(
            "Recent News"
        )

        for item in news:

            st.markdown(
                f"**{item['title']}**"
            )

            st.caption(
                f"{item['publisher']} | "
                f"{item['published']}"
            )

            if item["description"]:

                st.write(
                    item["description"]
                )

            if item["url"]:

                st.markdown(
                    f"[Open source]({item['url']})"
                )

        st.divider()

        st.subheader(
            "Autonomous Llama Research"
        )

        if st.button(
            "RUN AUTONOMOUS AI RESEARCH"
        ):

            with st.spinner(
                "Llama is analyzing supplied market evidence..."
            ):

                report = autonomous_research(
                    package
                )

                st.session_state.ai_report = (
                    report
                )

        if st.session_state.ai_report:

            st.markdown(
                st.session_state.ai_report
            )


# =========================================================
# NEWS
# =========================================================

elif st.session_state.page == "NEWS":

    st.header(
        "News Intelligence"
    )

    selected = st.selectbox(
        "Security",
        list(STOCKS.keys())
    )

    if st.button(
        "SCAN NEWS"
    ):

        news = fetch_news(
            selected,
            30
        )

        for item in news:

            st.markdown(
                f"### {item['title']}"
            )

            st.caption(
                f"{item['publisher']} | "
                f"{item['published']}"
            )

            st.write(
                item["description"]
            )

            if item["url"]:

                st.markdown(
                    f"[Source]({item['url']})"
                )


# =========================================================
# PAPER TRADING
# =========================================================

elif st.session_state.page == "PAPER TRADING":

    st.header(
        "Paper Trading"
    )

    st.warning(
        "TEST MONEY ONLY — NO BROKER ORDER IS SENT."
    )

    account = get_account()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Paper Capital",
        f"₹{PAPER_INITIAL_CAPITAL:,.0f}"
    )

    col2.metric(
        "Available Cash",
        f"₹{account['cash']:,.2f}"
    )

    col3.metric(
        "Realized P&L",
        f"₹{account['realized_pnl']:,.2f}"
    )

    st.divider()

    selected = st.selectbox(
        "Stock",
        list(STOCKS.keys())
    )

    current_df = yahoo_history(
        selected,
        period="1d",
        interval="1m"
    )

    current_price = None

    if not current_df.empty:

        current_price = float(
            current_df["close"].iloc[-1]
        )

        st.metric(
            "Current Paper Price",
            f"₹{current_price:,.2f}"
        )

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=10
    )

    stop_percent = st.number_input(
        "Stop Loss %",
        min_value=0.1,
        value=1.0,
        step=0.1
    )

    target_percent = st.number_input(
        "Target %",
        min_value=0.1,
        value=2.0,
        step=0.1
    )

    if current_price:

        stop = current_price * (
            1 - stop_percent / 100
        )

        target = current_price * (
            1 + target_percent / 100
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "PAPER BUY"
            ):

                success, message = buy(
                    selected,
                    quantity,
                    current_price,
                    stop_loss=stop,
                    target=target
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

        with c2:

            if st.button(
                "PAPER SELL"
            ):

                success, message = sell(
                    selected,
                    quantity,
                    current_price
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.subheader(
        "Open Positions"
    )

    account = get_account()

    if account["positions"]:

        rows = []

        for symbol, position in account[
            "positions"
        ].items():

            price = (
                get_nifty_price()
                if symbol == "^NSEI"
                else None
            )

            if price is None:

                df = yahoo_history(
                    symbol,
                    period="1d",
                    interval="1m"
                )

                if not df.empty:

                    price = float(
                        df["close"].iloc[-1]
                    )

            if price is None:
                price = position[
                    "average_price"
                ]

            pnl = (
                price -
                position["average_price"]
            ) * position["quantity"]

            rows.append({
                "Symbol": symbol,
                "Quantity": position[
                    "quantity"
                ],
                "Average": position[
                    "average_price"
                ],
                "Current": price,
                "Unrealized P&L": pnl,
                "Stop": position[
                    "stop_loss"
                ],
                "Target": position[
                    "target"
                ]
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No open paper positions."
        )


# =========================================================
# POSITIONS
# =========================================================

elif st.session_state.page == "POSITIONS":

    st.header(
        "Positions"
    )

    account = get_account()

    if account["positions"]:

        st.json(
            account["positions"]
        )

    else:

        st.info(
            "No positions."
        )


# =========================================================
# ORDERS
# =========================================================

elif st.session_state.page == "ORDERS":

    st.header(
        "Order Blotter"
    )

    orders = load_orders()

    if not orders.empty:

        st.dataframe(
            orders.sort_values(
                "time",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No paper orders yet."
        )


# =========================================================
# PORTFOLIO
# =========================================================

elif st.session_state.page == "PORTFOLIO":

    st.header(
        "Paper Portfolio"
    )

    account = get_account()

    st.metric(
        "Cash",
        f"₹{account['cash']:,.2f}"
    )

    st.metric(
        "Realized P&L",
        f"₹{account['realized_pnl']:,.2f}"
    )

    st.metric(
        "Open Positions",
        len(account["positions"])
    )


# =========================================================
# AI DEPLOYMENT
# =========================================================

elif st.session_state.page == "AI DEPLOYMENT":

    st.header(
        "AI Deployment Center"
    )

    st.info(
        "AI can research and analyze. "
        "AI cannot directly place broker orders."
    )

    provider = st.selectbox(
        "AI Provider",
        [
            "LOCAL",
            "GROQ"
        ]
    )

    if provider == "LOCAL":

        st.text_input(
            "Local Llama Endpoint",
            value="http://localhost:11434/v1"
        )

        st.text_input(
            "Local Model",
            value="llama3.1"
        )

    else:

        st.text_input(
            "Groq API Key",
            type="password"
        )

        st.text_input(
            "Groq Model",
            value="openai/gpt-oss-20b"
        )

    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        0.1
    )

    st.subheader(
        "Agent permissions"
    )

    st.checkbox(
        "Market data research",
        True
    )

    st.checkbox(
        "Technical analysis",
        True
    )

    st.checkbox(
        "News analysis",
        True
    )

    st.checkbox(
        "Fundamental research",
        True
    )

    st.checkbox(
        "Paper trading",
        True
    )

    st.checkbox(
        "Live broker orders",
        False,
        disabled=True
    )

    st.subheader(
        "Connection Test"
    )

    if st.button(
        "TEST AI CONNECTION"
    ):

        try:

            result = test_ai(
                provider=provider
            )

            st.success(
                result
            )

        except Exception as e:

            st.error(
                str(e)
            )


# =========================================================
# AI RESEARCH
# =========================================================

elif st.session_state.page == "AI RESEARCH":

    st.header(
        "Autonomous AI Research"
    )

    st.write(
        """
OMNITRIX first collects deterministic evidence:
market data → technicals → fundamentals → news.

Llama then interprets that evidence.

The AI does not directly control orders.
"""
    )

    selected = st.selectbox(
        "Security",
        list(STOCKS.keys())
    )

    if st.button(
        "START AUTONOMOUS RESEARCH"
    ):

        with st.spinner(
            "Collecting evidence and running Llama..."
        ):

            package = research_stock(
                selected
            )

            report = autonomous_research(
                package
            )

            st.markdown(
                report
            )


# =========================================================
# RISK
# =========================================================

elif st.session_state.page == "RISK":

    st.header(
        "Risk Control"
    )

    st.metric(
        "Maximum Daily Loss",
        "₹10,000"
    )

    st.metric(
        "Maximum Paper Position",
        "₹2,00,000"
    )

    st.warning(
        "F&O is disabled."
    )

    st.warning(
        "Live broker execution is disabled."
    )

    st.success(
        "AI direct order authority: NONE"
    )


# =========================================================
# WATCHLIST
# =========================================================

elif st.session_state.page == "WATCHLIST":

    st.header(
        "Watchlist"
    )

    selected = st.multiselect(
        "Add securities",
        list(STOCKS.keys())
    )

    if selected:

        snapshot = market_snapshot(
            selected
        )

        st.dataframe(
            snapshot,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# THEMES
# =========================================================

elif st.session_state.page == "THEMES":

    st.header(
        "Market Themes"
    )

    themes = {
        "Artificial Intelligence": [
            "AI",
            "data centers",
            "cloud",
            "semiconductor"
        ],
        "Defence": [
            "defence",
            "aerospace",
            "military"
        ],
        "EV": [
            "electric vehicle",
            "battery",
            "EV"
        ],
        "Railways": [
            "railway",
            "rail"
        ],
        "Renewables": [
            "solar",
            "renewable",
            "green energy"
        ],
        "Manufacturing": [
            "manufacturing",
            "industrial"
        ]
    }

    for theme, keywords in themes.items():

        st.markdown(
            f"### {theme}"
        )

        st.write(
            ", ".join(
                keywords
            )
        )


# =========================================================
# IPOs
# =========================================================

elif st.session_state.page == "IPOs":

    st.header(
        "IPO Intelligence"
    )

    st.info(
        "IPO module reserved for verified "
        "exchange/company filing data."
    )


# =========================================================
# STRATEGY LAB
# =========================================================

elif st.session_state.page == "STRATEGY LAB":

    st.header(
        "Strategy Lab"
    )

    st.write(
        "Build deterministic trading rules here."
    )

    st.checkbox(
        "EMA 9 > EMA 21"
    )

    st.checkbox(
        "RSI > 55"
    )

    st.checkbox(
        "Volume > 1.2x average"
    )

    st.checkbox(
        "MACD bullish"
    )

    st.checkbox(
        "Price above VWAP"
    )


# =========================================================
# BACKTESTING
# =========================================================

elif st.session_state.page == "BACKTESTING":

    st.header(
        "Backtesting"
    )

    st.info(
        "Backtesting engine will use historical "
        "OHLCV data and the same deterministic "
        "strategy rules used by the scanner."
    )


# =========================================================
# TRADE JOURNAL
# =========================================================

elif st.session_state.page == "TRADE JOURNAL":

    st.header(
        "Trade Journal"
    )

    orders = load_orders()

    if not orders.empty:

        st.dataframe(
            orders,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No trades recorded."
        )


# =========================================================
# SYSTEM LOGS
# =========================================================

elif st.session_state.page == "SYSTEM LOGS":

    st.header(
        "System Logs"
    )

    try:

        with open(
            "data/logs/terminal.log",
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        st.code(
            content[-15000:]
        )

    except Exception:

        st.info(
            "No system logs yet."
        )


# =========================================================
# SETTINGS
# =========================================================

elif st.session_state.page == "SETTINGS":

    st.header(
        "System Settings"
    )

    st.write(
        """
OMNITRIX operating configuration
"""
    )

    st.success(
        "Market: NSE / BSE"
    )

    st.success(
        "Asset class: Indian cash equities"
    )

    st.warning(
        "F&O: Disabled"
    )

    st.warning(
        "Live broker execution: Disabled"
    )

    st.success(
        "Paper trading: Enabled"
    )

    st.success(
        "AI research: Enabled"
    )

    st.success(
        "AI direct order authority: None"
    )

    st.caption(
        "OMNITRIX is a research and paper-trading "
        "terminal. Market data quality depends on "
        "the configured provider."
    )
