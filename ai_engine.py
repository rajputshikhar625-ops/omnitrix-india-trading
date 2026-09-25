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


def build_research_prompt(
    package
):

    safe_package = {
        "symbol": package.get(
            "symbol"
        ),
        "technical": package.get(
            "technical",
            {}
        ),
        "fundamentals": package.get(
            "fundamentals",
            {}
        ),
        "levels": package.get(
            "levels",
            {}
        ),
        "news": package.get(
            "news",
            []
        )[:20]
    }

    data = json.dumps(
        safe_package,
        indent=2,
        default=str
    )

    return f"""
Research the following Indian stock.

DATA:
{data}

Return exactly these sections:

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
| Catalysts | | | |
| Risks | | | |
| Data Gaps | | | |

## TECHNICAL STRUCTURE

Explain:
- EMA structure
- SMA structure
- RSI
- MACD
- VWAP
- Bollinger Bands
- ATR
- ADX
- Stochastic
- CCI
- MFI
- OBV
- ROC

## MARKET CONTEXT

Explain whether the evidence indicates:
- bullish evidence
- bearish evidence
- mixed evidence
- insufficient evidence

Do not convert this into certainty.

## LEVELS

Discuss:
- support
- resistance
- pivot
- Fibonacci levels

## NEWS INTELLIGENCE

Identify:
- important recent developments
- possible catalysts
- possible risks
- conflicting news

## RESEARCH STATUS

End with:

Research completeness: X/100
Data quality: HIGH/MEDIUM/LOW
Major uncertainty:
What should be monitored next:
"""


def autonomous_research(
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
