import json
import pandas as pd

from pathlib import Path
from datetime import datetime

from config import (
    DATA_DIR,
    TRADE_DIR,
    LOG_DIR,
    CACHE_DIR
)


PAPER_ACCOUNT_FILE = TRADE_DIR / "paper_account.json"
ORDERS_FILE = TRADE_DIR / "paper_orders.csv"
JOURNAL_FILE = TRADE_DIR / "journal.csv"
LOG_FILE = LOG_DIR / "terminal.log"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_json(path, default=None):
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def log(message):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"[{timestamp}] {message}\n"
        )


def save_orders(rows):
    if not rows:
        return

    df = pd.DataFrame(rows)

    TRADE_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        ORDERS_FILE,
        index=False
    )


def load_orders():

    if not ORDERS_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(ORDERS_FILE)
    except Exception:
        return pd.DataFrame()


def save_journal(rows):

    if not rows:
        return

    df = pd.DataFrame(rows)

    df.to_csv(
        JOURNAL_FILE,
        index=False
    )


def load_journal():

    if not JOURNAL_FILE.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(JOURNAL_FILE)
    except Exception:
        return pd.DataFrame()


def save_paper_account(account):

    write_json(
        PAPER_ACCOUNT_FILE,
        account
    )


def load_paper_account():

    return read_json(
        PAPER_ACCOUNT_FILE,
        None
    )
