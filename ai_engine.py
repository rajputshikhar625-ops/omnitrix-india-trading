import json
import time

from openai import OpenAI

from config import (
    AI_PROVIDER,
    LOCAL_LLM_BASE_URL,
    LOCAL_LLM_API_KEY,
    LOCAL_LLM_MODEL,
    GROQ_API_KEY
)


SYSTEM_PROMPT = """
You are OMNITRIX RESEARCH AI.

You are an institutional-style equity research assistant.

Your job is to analyze supplied market data, technical indicators,
fundamental data and news.

IMPORTANT RULES:

1. Never invent missing information.
2. Clearly distinguish observed data from interpretation.
3. If information is missing write DATA UNAVAILABLE.
4. Do not claim to have accessed a website unless the supplied tools
   actually supplied the information.
5. Do not place real orders.
6. Do not control a broker.
7. Do not guarantee profits.
8. Highlight uncertainty.
9. Explain conflicting signals.
10. Focus on Indian cash equities.

Produce structured research rather than emotional commentary.
"""


def get_client(
    provider=None,
    base_url=None,
    api_key=None
):

    provider = (
        provider or
        AI_PROVIDER
    ).upper()

    if provider == "GROQ":

        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY not configured."
            )

        return OpenAI(
            api_key=GROQ_API_KEY,
            base_url=(
                "https://api.groq.com/openai/v1"
            )
        )

    return OpenAI(
        api_key=(
            api_key or
            LOCAL_LLM_API_KEY
        ),
        base_url=(
            base_url or
            LOCAL_LLM_BASE_URL
        )
    )


def get_model(provider=None):

    provider = (
        provider or
        AI_PROVIDER
    ).upper()

    if provider == "GROQ":
        return "openai/gpt-oss-20b"

    return LOCAL_LLM_MODEL


def ai_call(
    prompt,
    provider=None,
    base_url=None,
    api_key=None,
    temperature=0.1
):

    client = get_client(
        provider=provider,
        base_url=base_url,
        api_key=api_key
    )

    model = get_model(
        provider
    )

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[
        0
    ].message.content


def build_research_prompt(package):
    safe_package={
        "symbol":package.get("symbol"),
        "technical":package.get("technical",{}),
        "fundamentals":package.get("fundamentals",{}),
        "levels":package.get("levels",{}),
        "news":package.get("news",[])[:20],
        "news_match":package.get("news_match",{}),
        "patterns":package.get("patterns",[]),
        "pattern_history":package.get("pattern_history",{}).to_dict("records") if hasattr(package.get("pattern_history"),"to_dict") else package.get("pattern_history",[])
    }
    data=json.dumps(safe_package,indent=2,default=str)
    return f"""Research the following Indian cash-equity stock using ONLY the supplied evidence.

DATA:
{data}

Return these sections:

## RESEARCH TABLE
| Area | Observation | Interpretation | Confidence |
|---|---|---|---|
| Market Regime | | | |
| Price Trend | | | |
| Momentum | | | |
| Volume | | | |
| Volatility | | | |
| Technical Levels | | | |
| Fundamentals | | | |
| News | | | |
| Current Chart Pattern | | | |
| Historical Pattern Behaviour | | | |
| Risks | | | |
| Data Gaps | | | |

## THREE-SIGNAL CHECK
Compare independently:
1. NEWS — recency, relevance, positive/negative/mixed evidence.
2. PRICE — current movement, momentum and volume.
3. CHART — EMA/SMA/VWAP/RSI/MACD/ADX and detected pattern.

Explain agreement and conflict between the three.

## HISTORICAL PATTERN CHECK
Use the supplied historical pattern statistics. State sample size and average/win-rate evidence when available. Never treat historical frequency as a guarantee.

## EXIT / INVALIDATION LOGIC
Describe objective conditions that would invalidate the research thesis and objective paper-trading exit conditions. Do not place a real order.

## UNCERTAINTY
State the largest missing or unreliable information.

## RESEARCH STATUS
Research completeness: X/100
Data quality: HIGH/MEDIUM/LOW
What should be monitored next:
"""\ndef autonomous_research(
    package,
    provider=None
):

    prompt = build_research_prompt(
        package
    )

    return ai_call(
        prompt,
        provider=provider,
        temperature=0.1
    )



def autonomous_multi_research(packages, provider="LOCAL"):
    """Compare up to six collected stock packages using the configured local model."""
    safe=[]
    for package in packages[:6]:
        if not package: continue
        history=package.get("pattern_history",[])
        if hasattr(history,"to_dict"):
            history=history.tail(5).to_dict("records")
        match=package.get("news_match",{}) or {}
        safe.append({
            "symbol":package.get("symbol"),
            "technical":package.get("technical",{}),
            "fundamentals":package.get("fundamentals",{}),
            "levels":package.get("levels",{}),
            "news":package.get("news",[])[:5],
            "news_match":{"bias":match.get("bias"),"score":match.get("score"),"headline":match.get("headline")},
            "patterns":package.get("patterns",[])[:5],
            "pattern_history":history,
        })
    if not safe: raise ValueError("No stock research evidence was available.")
    data=json.dumps(safe,indent=2,default=str)
    prompt=f"""Compare these Indian cash-equity research packages using only the supplied evidence.\n\nDATA:\n{data}\n\nFor each symbol, summarize observed price/technical structure, relevant fundamentals, recent headlines, historical pattern evidence, risks, and missing data. Include a concise comparison table with one row per stock. Separate measured facts from interpretation and explain conflicting signals.\n\nDo not issue buy/sell instructions, predict guaranteed outcomes, provide position sizes, or initiate broker actions. Finish with the main uncertainties to monitor. This is research, not a trade order."""
    return ai_call(prompt,provider=provider,temperature=0.1)

def test_ai(
    provider=None,
    base_url=None,
    api_key=None
):

    return ai_call(
        "Respond with exactly: OMNITRIX AI ONLINE",
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        temperature=0
    )
