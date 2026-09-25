import json
from datetime import datetime
import pandas as pd
from config import TRADE_DIR,LOG_DIR
PAPER_ACCOUNT_FILE=TRADE_DIR/"paper_account.json";ORDERS_FILE=TRADE_DIR/"paper_orders.csv";JOURNAL_FILE=TRADE_DIR/"journal.csv";LOG_FILE=LOG_DIR/"terminal.log"
def write_json(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def read_json(p,default=None):
 if not p.exists():return default
 try:return json.loads(p.read_text(encoding="utf-8"))
 except Exception:return default
def log(msg):
 LOG_DIR.mkdir(parents=True,exist_ok=True);LOG_FILE.open("a",encoding="utf-8").write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")
def save_orders(rows):TRADE_DIR.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows or []).to_csv(ORDERS_FILE,index=False)
def load_orders():
 try:return pd.read_csv(ORDERS_FILE) if ORDERS_FILE.exists() else pd.DataFrame()
 except Exception:return pd.DataFrame()
def save_journal(rows):TRADE_DIR.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows or []).to_csv(JOURNAL_FILE,index=False)
def load_journal():
 try:return pd.read_csv(JOURNAL_FILE) if JOURNAL_FILE.exists() else pd.DataFrame()
 except Exception:return pd.DataFrame()
def save_paper_account(a):write_json(PAPER_ACCOUNT_FILE,a)
def load_paper_account():return read_json(PAPER_ACCOUNT_FILE)
