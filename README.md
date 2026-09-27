# OMNITRIX — Indian Equities Trading Terminal

OMNITRIX is a Streamlit-based trading dashboard for Indian (NSE) equities. It combines live market data, technical analysis, an AI research workspace, and a paper-trading simulator in a single terminal-style interface — built for tracking ideas and testing strategies without risking real money.

## Features

- **Command Center (Market)** — Live snapshot of NIFTY 50, paper account balance, realized P&L, and a watchlist across 80+ NSE-listed stocks.
- **AI Workspace** — Ask a local AI model to research stocks, synthesize news, and generate trade ideas.
- **Security Researcher** — Deep-dive research on a single stock: charts, indicators, and AI-assisted analysis.
- **Market Scanner** — Scan the full stock universe for signals and setups.
- **AI Deployed** — Autonomous multi-stock research runs.
- **Paper Trading Only** — All trades are simulated. No live orders, no F&O, no real money at risk.

## Tech Stack

- [Streamlit](https://streamlit.io/) — UI framework
- [Plotly](https://plotly.com/python/) — Candlestick, oscillator, and volume charts
- [Pandas](https://pandas.pydata.org/) — Data handling
- A local LLM for AI-assisted research (see `config.py` for model settings)

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app — UI, layout, and page routing |
| `config.py` | App version and local LLM model settings |
| `market_data.py` | Fetches live/delayed market quotes |
| `research_engine.py` | Single-stock research logic |
| `scanner.py` | Scans the stock universe for signals |
| `ai_engine.py` | AI call handling and autonomous research |
| `charts.py` | Candlestick, oscillator, and volume chart builders |
| `paper_trading.py` | Simulated trading account and position monitoring |
| `learning_engine.py` | Tracks and reports on past trade outcomes |

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Disclaimer

This project is for educational and research purposes only. It trades on a **simulated paper account** — no real orders are placed. Nothing in this app constitutes financial advice. Always do your own research before making real investment decisions.
