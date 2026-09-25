import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent
load_dotenv(BASE_DIR/".env")
DATA_DIR=BASE_DIR/"data"; TRADE_DIR=DATA_DIR/"trades"; LOG_DIR=DATA_DIR/"logs"; CACHE_DIR=DATA_DIR/"cache"
for d in (DATA_DIR,TRADE_DIR,LOG_DIR,CACHE_DIR): d.mkdir(parents=True,exist_ok=True)
GROWW_ACCESS_TOKEN=os.getenv("GROWW_ACCESS_TOKEN","").strip()
GROQ_API_KEY=os.getenv("GROQ_API_KEY","").strip()
LOCAL_LLM_BASE_URL=os.getenv("LOCAL_LLM_BASE_URL","http://localhost:11434/v1").strip()
LOCAL_LLM_API_KEY=os.getenv("LOCAL_LLM_API_KEY","local").strip()
LOCAL_LLM_MODEL=os.getenv("LOCAL_LLM_MODEL","llama3.1").strip()
AI_PROVIDER=os.getenv("AI_PROVIDER","LOCAL").strip().upper()
try: PAPER_INITIAL_CAPITAL=float(os.getenv("PAPER_INITIAL_CAPITAL","1000000"))
except ValueError: PAPER_INITIAL_CAPITAL=1000000.0
NIFTY_SYMBOL="^NSEI"; MARKET_TIMEZONE="Asia/Kolkata"
MARKET_OPEN_HOUR=9; MARKET_OPEN_MINUTE=15; MARKET_CLOSE_HOUR=15; MARKET_CLOSE_MINUTE=30
MAX_DAILY_LOSS=10000.0; MAX_POSITION_VALUE=200000.0
DEFAULT_STOP_LOSS_PERCENT=1.0; DEFAULT_TARGET_PERCENT=2.0
APP_NAME="OMNITRIX"; APP_VERSION="4.1"
BG="#050b12"; PANEL="#0b1420"; PANEL_2="#101c2a"; BLUE="#1677ff"; BLUE_LIGHT="#55a4ff"; WHITE="#f4f8fc"; BLACK="#07101a"; GREY="#91a1b4"; GREEN="#20c997"; RED="#ff5c69"; AMBER="#eab84b"
