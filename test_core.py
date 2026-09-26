import unittest
import pandas as pd
import numpy as np
from indicators import add_indicators, rsi, macd
from paper_trading import buy, sell, get_account
from scanner import score_stock

class TestOmnitrixCore(unittest.TestCase):
    def test_indicators(self):
        dates = pd.date_range("2026-01-01", periods=50, freq="D")
        df = pd.DataFrame({
            "datetime": dates,
            "open": np.linspace(100, 150, 50),
            "high": np.linspace(102, 152, 50),
            "low": np.linspace(98, 148, 50),
            "close": np.linspace(101, 151, 50),
            "volume": np.random.randint(1000, 5000, 50)
        })
        res = add_indicators(df)
        self.assertIn("rsi", res.columns)
        self.assertIn("macd", res.columns)
        self.assertIn("sma20", res.columns)

    def test_paper_trading(self):
        account = get_account()
        self.assertIn("cash", account)
        success, msg = buy("RELIANCE.NS", 1, 100.0)
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
