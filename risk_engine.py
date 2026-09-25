import math

from config import (
    DEFAULT_STOP_LOSS_PERCENT,
    DEFAULT_TARGET_PERCENT,
    MAX_DAILY_LOSS,
    MAX_POSITION_VALUE,
)


BULLISH_PATTERNS = {
    "BREAKOUT",
    "EMA_CROSS_UP",
    "TREND_PULLBACK",
}
BLOCKING_PATTERNS = {
    "BREAKDOWN",
    "EMA_CROSS_DOWN",
    "BEAR_PULLBACK",
    "RSI_OVERBOUGHT",
}


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _blocked(symbol, reason, price=None):
    return {
        "allowed": False,
        "symbol": symbol,
        "price": price,
        "quantity": 0,
        "reason": reason,
    }


def build_paper_trade_plan(package, account, current_price=None):
    """Build a deterministic long-only paper plan from a research package."""
    if not isinstance(package, dict):
        return _blocked("", "Research package is unavailable.")

    symbol = str(package.get("symbol", "")).strip().upper()
    if not symbol:
        return _blocked("", "Symbol is missing from the research package.")

    technical = package.get("technical") or {}
    price = _finite_number(current_price)
    if price is None:
        price = _finite_number(technical.get("close"))
    if price is None or price <= 0:
        return _blocked(symbol, "A valid positive price is required.")

    patterns = package.get("patterns") or []
    pattern_names = {
        str(item.get("pattern", "")).upper()
        for item in patterns
        if isinstance(item, dict)
    }
    bullish = sorted(pattern_names & BULLISH_PATTERNS)
    blocking = sorted(pattern_names & BLOCKING_PATTERNS)

    if not bullish:
        return _blocked(symbol, "No supported bullish pattern is present.", price)
    if blocking:
        return _blocked(
            symbol,
            "Conflicting or overbought pattern: " + ", ".join(blocking),
            price,
        )

    if not isinstance(account, dict):
        return _blocked(symbol, "Paper account is unavailable.", price)
    if account.get("trading_locked"):
        return _blocked(symbol, "Paper account is locked by its risk controls.", price)

    positions = account.get("positions") or {}
    if symbol in positions:
        return _blocked(symbol, "A paper position for this symbol is already open.", price)

    cash = _finite_number(account.get("cash"))
    if cash is None or cash <= 0:
        return _blocked(symbol, "Paper cash is unavailable or insufficient.", price)

    equity = cash
    try:
        for position in positions.values():
            quantity = _finite_number(position.get("quantity"))
            average_price = _finite_number(position.get("average_price"))
            if quantity is None or average_price is None or quantity < 0 or average_price < 0:
                return _blocked(symbol, "An existing paper position has invalid values.", price)
            equity += quantity * average_price
    except (AttributeError, TypeError):
        return _blocked(symbol, "Existing paper positions could not be valued.", price)

    if not math.isfinite(equity) or equity <= 0:
        return _blocked(symbol, "Paper account equity is invalid.", price)

    stop_loss = price * (1 - DEFAULT_STOP_LOSS_PERCENT / 100)
    target = price * (1 + DEFAULT_TARGET_PERCENT / 100)
    risk_per_share = price - stop_loss
    risk_budget = min(equity * 0.0025, MAX_DAILY_LOSS * 0.20)

    if (
        not math.isfinite(stop_loss)
        or not math.isfinite(target)
        or risk_per_share <= 0
        or risk_budget <= 0
    ):
        return _blocked(symbol, "Configured risk limits do not allow an entry.", price)

    sizing_ratios = (
        risk_budget / risk_per_share,
        MAX_POSITION_VALUE / price,
        cash / price,
    )
    if not all(math.isfinite(ratio) for ratio in sizing_ratios):
        return _blocked(symbol, "Risk sizing is outside the supported numeric range.", price)

    quantity_by_risk = math.floor(sizing_ratios[0])
    quantity_by_position_cap = math.floor(sizing_ratios[1])
    quantity_by_cash = math.floor(sizing_ratios[2])
    quantity = min(quantity_by_risk, quantity_by_position_cap, quantity_by_cash)

    if quantity < 1:
        return _blocked(symbol, "Risk, position cap, or paper cash is too small for one share.", price)

    notional = quantity * price
    risk_amount = quantity * risk_per_share

    return {
        "allowed": True,
        "symbol": symbol,
        "price": round(price, 2),
        "quantity": quantity,
        "stop_loss": round(stop_loss, 2),
        "target": round(target, 2),
        "notional": round(notional, 2),
        "risk_amount": round(risk_amount, 2),
        "risk_budget": round(risk_budget, 2),
        "signal_patterns": bullish,
        "reason": "Bullish pattern passed deterministic paper risk checks.",
    }
