import uuid
import math

from datetime import datetime, timedelta, timezone

from config import (
    PAPER_INITIAL_CAPITAL,
    MAX_POSITION_VALUE,
    MAX_DAILY_LOSS,
)

from storage import (
    load_paper_account,
    save_paper_account,
    load_orders,
    save_orders,
    log
)


INDIA_TIMEZONE = timezone(timedelta(hours=5, minutes=30))


def create_account():

    return {
        "initial_capital": PAPER_INITIAL_CAPITAL,
        "cash": PAPER_INITIAL_CAPITAL,
        "realized_pnl": 0.0,
        "positions": {},
        "daily_start_equity": PAPER_INITIAL_CAPITAL,
        "trading_locked": False,
        "trading_day": datetime.now(INDIA_TIMEZONE).date().isoformat()
    }


def get_account():

    account = load_paper_account()
    today = datetime.now(INDIA_TIMEZONE).date().isoformat()

    if account is None:

        account = create_account()
        save_paper_account(account)

    elif not account.get("trading_day"):

        # Start daily-loss tracking from the migrated account's current equity.
        account["daily_start_equity"] = equity(account, {})
        account["trading_day"] = today
        save_paper_account(account)

    elif account["trading_day"] != today:

        account["daily_start_equity"] = equity(account, {})
        account["trading_locked"] = False
        account["trading_day"] = today
        save_paper_account(account)

    return account


def save_account(account):

    save_paper_account(
        account
    )


def position_value(
    position,
    price
):

    return (
        position["quantity"] *
        price
    )


def equity(account, prices):

    total = account["cash"]

    for symbol, position in account[
        "positions"
    ].items():

        price = prices.get(
            symbol,
            position["average_price"]
        )

        total += position_value(
            position,
            price
        )

    return total


def daily_pnl(
    account,
    prices
):

    current = equity(
        account,
        prices
    )

    return (
        current -
        account["daily_start_equity"]
    )


def buy(
    symbol,
    quantity,
    price,
    stop_loss=None,
    target=None
):

    try:
        symbol = str(symbol).strip().upper()
        raw_quantity = float(quantity)
        price = float(price)
        stop_loss = None if stop_loss is None else float(stop_loss)
        target = None if target is None else float(target)
    except (TypeError, ValueError, OverflowError):
        return False, "Invalid paper order values."

    if not symbol:
        return False, "Symbol is required."

    if not math.isfinite(raw_quantity) or not raw_quantity.is_integer():
        return False, "Quantity must be a whole number."

    quantity = int(raw_quantity)

    if quantity <= 0:
        return False, "Invalid quantity."

    if not math.isfinite(price) or price <= 0:
        return False, "Price must be a finite positive number."

    if stop_loss is not None and (
        not math.isfinite(stop_loss) or stop_loss <= 0 or stop_loss >= price
    ):
        return False, "Stop loss must be positive and below the entry price."

    if target is not None and (
        not math.isfinite(target) or target <= price
    ):
        return False, "Target must be above the entry price."

    account = get_account()

    value = (
        quantity *
        price
    )

    if not math.isfinite(value):
        return False, "Order value is outside the supported range."

    if account["trading_locked"]:
        return False, (
            "Paper trading is locked."
        )

    if value > account["cash"]:
        return False, (
            "Insufficient paper cash."
        )

    old = account[
        "positions"
    ].get(
        symbol
    )

    existing_value = (
        old["quantity"] * old["average_price"]
        if old
        else 0
    )

    if existing_value + value > MAX_POSITION_VALUE:
        return False, (
            "Position would exceed maximum "
            "paper position value."
        )

    if old:

        old_quantity = old[
            "quantity"
        ]

        old_average = old[
            "average_price"
        ]

        new_quantity = (
            old_quantity +
            quantity
        )

        new_average = (
            (
                old_quantity *
                old_average
            ) +
            (
                quantity *
                price
            )
        ) / new_quantity

        old["quantity"] = (
            new_quantity
        )

        old["average_price"] = (
            new_average
        )

        if stop_loss is not None:
            old["stop_loss"] = stop_loss

        if target is not None:
            old["target"] = target

    else:

        account[
            "positions"
        ][symbol] = {
            "quantity": quantity,
            "average_price": price,
            "stop_loss": stop_loss,
            "target": target,
            "opened_at": datetime.now().isoformat()
        }

    account["cash"] -= value

    order = {
        "id": str(uuid.uuid4()),
        "time": datetime.now().isoformat(),
        "symbol": symbol,
        "side": "BUY",
        "quantity": quantity,
        "price": price,
        "value": value,
        "reason": "PAPER"
    }

    orders = load_orders()

    rows = (
        orders.to_dict("records")
        if not orders.empty
        else []
    )

    rows.append(order)

    save_orders(rows)

    save_account(account)

    log(
        f"PAPER BUY {symbol} "
        f"{quantity} @ {price}"
    )

    return True, (
        f"BUY executed in paper account: "
        f"{symbol} x {quantity}"
    )


def sell(
    symbol,
    quantity,
    price,
    reason="MANUAL"
):

    try:
        symbol = str(symbol).strip().upper()
        raw_quantity = float(quantity)
        price = float(price)
    except (TypeError, ValueError, OverflowError):
        return False, "Invalid paper order values."

    if not symbol:
        return False, "Symbol is required."

    if not math.isfinite(raw_quantity) or not raw_quantity.is_integer():
        return False, "Quantity must be a whole number."

    quantity = int(raw_quantity)

    if quantity <= 0:
        return False, "Invalid quantity."

    if not math.isfinite(price) or price <= 0:
        return False, "Price must be a finite positive number."

    account = get_account()

    position = account[
        "positions"
    ].get(
        symbol
    )

    if not position:
        return False, (
            "No paper position exists."
        )

    if quantity > position[
        "quantity"
    ]:
        return False, (
            "Cannot sell more than "
            "current paper position."
        )

    average = position[
        "average_price"
    ]

    pnl = (
        price - average
    ) * quantity

    value = (
        price *
        quantity
    )

    account["cash"] += value

    account[
        "realized_pnl"
    ] += pnl

    position[
        "quantity"
    ] -= quantity

    if position["quantity"] <= 0:

        del account[
            "positions"
        ][symbol]

    order = {
        "id": str(uuid.uuid4()),
        "time": datetime.now().isoformat(),
        "symbol": symbol,
        "side": "SELL",
        "quantity": quantity,
        "price": price,
        "value": value,
        "realized_pnl": pnl,
        "reason": reason
    }

    orders = load_orders()

    rows = (
        orders.to_dict("records")
        if not orders.empty
        else []
    )

    rows.append(order)

    save_orders(rows)

    save_account(account)

    log(
        f"PAPER SELL {symbol} "
        f"{quantity} @ {price} "
        f"PnL={pnl}"
    )

    return True, (
        f"SELL executed: {symbol} "
        f"| P&L ₹{pnl:,.2f}"
    )


def monitor_positions(
    prices
):

    account = get_account()

    exits = []

    for symbol in list(
        account["positions"].keys()
    ):

        position = account[
            "positions"
        ][symbol]

        price = prices.get(
            symbol
        )

        try:
            price = float(price)
        except (TypeError, ValueError, OverflowError):
            continue

        if not math.isfinite(price) or price <= 0:
            continue

        stop = position.get(
            "stop_loss"
        )

        target = position.get(
            "target"
        )

        quantity = position[
            "quantity"
        ]

        if stop is not None:

            if price <= stop:

                exits.append(
                    sell(
                        symbol,
                        quantity,
                        price,
                        "STOP_LOSS"
                    )
                )

                continue

        if target is not None:

            if price >= target:

                exits.append(
                    sell(
                        symbol,
                        quantity,
                        price,
                        "TARGET"
                    )
                )

    return exits


def check_daily_lock(
    prices
):

    account = get_account()

    pnl = daily_pnl(
        account,
        prices
    )

    if pnl <= -MAX_DAILY_LOSS:

        account[
            "trading_locked"
        ] = True

        save_account(
            account
        )

        return True

    return False


def reset_daily_lock():

    account = get_account()

    account[
        "daily_start_equity"
    ] = equity(
        account,
        {}
    )

    account[
        "trading_locked"
    ] = False
    account["trading_day"] = datetime.now(INDIA_TIMEZONE).date().isoformat()

    save_account(
        account
    )
