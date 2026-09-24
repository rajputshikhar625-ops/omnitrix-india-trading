import os
import streamlit as st
import yfinance as yf
from gnews import GNews
import litellm
from crewai import Agent, Task, Crew, LLM
import crewai.llms.cache as _crewai_cache

# ==========================================
# FIX GROQ & CREWAI COMPATIBILITY
# ==========================================
litellm.drop_params = True
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

# ==========================================
# 1. BEN 10 OMNITRIX SCI-FI STYLING (CSS)
# ==========================================
st.set_page_config(page_title="OMNITRIX AI - India Trading Terminal", layout="wide")

ben10_css = """

"""
st.markdown(ben10_css, unsafe_allow_html=True)

# ==========================================
# 2. UI HEADER & CONTROL PANEL
# ==========================================
st.title("👽 OMNITRIX AI: GROQ LLAMA TRADING TERMINAL")
st.caption("⚡ Powered by Groq Cloud Llama 3 | Indian Markets (NSE/BSE) | Multi-Agent Self-Research")

st.sidebar.header("⚙️ OMNITRIX CONTROL PANEL")

# Free Groq API Key Input
groq_api_key = st.sidebar.text_input(
    "Enter Free Groq API Key:",
    value=os.getenv("GROQ_API_KEY", ""),
    type="password",
    help="Get a free key instantly at https://console.groq.com/keys"
)

# Groq Model Selection Dropdown
selected_model = st.sidebar.selectbox(
    "Select Active Groq Model:",
    [
        "groq/llama-3.1-8b-instant",
        "groq/llama-3.3-70b-versatile",
        "groq/mixtral-8x7b-32768"
    ],
    index=0,
    help="If one model is undergoing maintenance or deprecated, switch to another option."
)

symbol = st.sidebar.text_input(
    "Enter Indian Ticker (.NS for NSE):", 
    value="RELIANCE.NS",
    help="Examples: RELIANCE.NS, TATAMOTORS.NS, INFY.NS, ZOMATO.NS, ^NSEI (Nifty 50)"
)

# User Strategy & Risk Parameters
st.sidebar.subheader("🛡️ Risk & Execution Rules")
max_loss_limit = st.sidebar.number_input("Stop Trading After Max Losses:", min_value=1, max_value=5, value=1)
win_target_limit = st.sidebar.number_input("Target Wins Goal:", min_value=1, max_value=5, value=2)
min_rr_ratio = st.sidebar.slider("Minimum Risk:Reward Ratio", 1.0, 3.0, 2.0, 0.5)

# ==========================================
# 3. LIVE MARKET DATA (INDIAN STOCKS)
# ==========================================
st.subheader(f"📊 LIVE MARKET FEED: {symbol}")
ticker = yf.Ticker(symbol)
hist = ticker.history(period="10d")

latest_price = 0.0
if not hist.empty:
    latest_price = hist['Close'].iloc[-1]
    prev_price = hist['Close'].iloc[-2]
    change = latest_price - prev_price
    pct_change = (change / prev_price) * 100
    
    col1, col2 = st.columns(2)
    col1.metric(label="Current Price (INR)", value=f"₹{latest_price:,.2f}", delta=f"{pct_change:+.2f}%")
    col2.metric(label="10-Day High / Low", value=f"₹{hist['High'].max():,.2f} / ₹{hist['Low'].min():,.2f}")
    
    st.line_chart(hist['Close'])
else:
    st.error("Invalid Ticker. For Indian stocks, add '.NS' (e.g., RELIANCE.NS, TCS.NS).")

# ==========================================
# 4. GOOGLE NEWS INDIA SCRAPER
# ==========================================
st.subheader("📰 REAL-TIME INDIAN MARKET NEWS SEARCH")
news_summary = ""
try:
    google_news = GNews(language='en', country='IN', period='7d', max_results=5)
    results = google_news.get_news(f"{symbol} stock news India Moneycontrol")
    
    if results:
        for item in results:
            title = item.get('title', 'No Title')
            url = item.get('url', '#')
            desc = item.get('description', '')
            publisher = item.get('publisher', {}).get('title', 'Indian News') if isinstance(item.get('publisher'), dict) else item.get('publisher', 'Indian News')
            
            st.markdown(f"- **[{title}]({url})** — *{publisher}*")
            if desc:
                st.caption(desc)
            news_summary += f"Headline: {title}\nPublisher: {publisher}\nSummary: {desc}\n\n"
    else:
        st.info("No recent Google News articles found for this ticker.")
except Exception as err:
    st.warning(f"Google News fetch error: {err}")

# ==========================================
# 5. GROQ LLAMA MULTI-AGENT ENGINE
# ==========================================
if st.button("🟢 INITIALIZE OMNITRIX AGENT SELF-RESEARCH"):
    if not groq_api_key:
        st.error("Please enter your free Groq API Key in the left sidebar (get one at console.groq.com/keys).")
    else:
        try:
            # Initialize chosen Groq Model
            groq_llm = LLM(
                model=selected_model,
                api_key=groq_api_key
            )

            tech_agent = Agent(
                role="NSE/BSE Technical Pattern Specialist",
                goal="Analyze price structures, volatility, support/resistance levels, and short-term trends.",
                backstory="You are a senior technical analyst on Dalal Street specializing in price action and volume trends.",
                llm=groq_llm,
                verbose=True
            )

            news_agent = Agent(
                role="Indian Market & News Analyst",
                goal="Extract key market drivers, earnings impacts, and sentiment from Indian media snippets.",
                backstory="You analyze Indian market sentiment from Moneycontrol, Economic Times, and Mint.",
                llm=groq_llm,
                verbose=True
            )

            filter_agent = Agent(
                role="Head Risk Manager & Trade Filter",
                goal="Apply strict risk filters to decide whether a trade SHOULD BE TAKEN or REJECTED/PASSED.",
                backstory="You are a conservative risk officer who rejects low-probability setups or bad risk-reward trades.",
                llm=groq_llm,
                verbose=True
            )

            if not news_summary:
                news_summary = "No live news available. Base analysis purely on price trends."

            task1 = Task(
                description=f"Analyze price history for {symbol} (Price: ₹{latest_price:,.2f}). Identify trend direction, support, and resistance.",
                expected_output="Technical trend analysis with support/resistance levels.",
                agent=tech_agent
            )

            task2 = Task(
                description=f"Analyze these Indian market news snippets for {symbol}:\n{news_summary}\nAssign a sentiment score (-10 to +10) and key drivers.",
                expected_output="News sentiment score and key market catalysts.",
                agent=news_agent
            )

            task3 = Task(
                description=f"""
Review technical and news research for {symbol}. Apply these strict rules:
1. Required Risk-to-Reward Ratio: At least 1:{min_rr_ratio}
2. Max Loss Rule: Stop trading if streak reached {max_loss_limit} loss. Target wins: {win_target_limit}.
3. NO-TRADE CONDITIONS: Reject trade if news is conflicting or risk is high.

Provide output in 3 clean sections:
- **RESEARCH SUMMARY**: Key findings.
- **TRADE VERDICT**: [EXECUTE TRADE] or [DO NOT TRADE / STAND ASIDE].
- **REASONING & RISK PLAN**: Detailed explanation for decision.
""",
                expected_output="Final Trade Verdict ([EXECUTE TRADE] or [DO NOT TRADE / STAND ASIDE]) with reasoning.",
                agent=filter_agent
            )

            with st.spinner(f"⚡ Omnitrix Crew running via {selected_model}..."):
                crew = Crew(
                    agents=[tech_agent, news_agent, filter_agent],
                    tasks=[task1, task2, task3],
                    verbose=True
                )
                result = crew.kickoff()
                
                st.subheader("🛸 OMNITRIX AUTONOMOUS RESEARCH REPORT")
                st.markdown(result.raw)

        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
