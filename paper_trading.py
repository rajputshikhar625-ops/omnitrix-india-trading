import uuid

from datetime import datetime

from config import (
    PAPER_INITIAL_CAPITAL,
    MAX_POSITION_VALUE,
    MAX_DAILY_LOSS
)

from storage import (
    load_paper_account,
    save_paper_account,
    load_orders,
    save_orders,
    log
)


def create_account():

    return {
        "initial_capital": PAPER_INITIAL_CAPITAL,
        "cash": PAPER_INITIAL_CAPITAL,
        "realized_pnl": 0.0,
        "positions": {},
        "daily_start_equity": PAPER_INITIAL_CAPITAL,
        "trading_locked": False
    }


def get_account():

    account = load_paper_account()

    if account is None:

        account = create_account()

        save_paper_account(
            account
        )

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

    account = get_account()

    symbol = symbol.upper()

    quantity = int(
        quantity
    )

    price = float(
        price
    )

    value = (
        quantity *
        price
    )

    if quantity <= 0:
        return False, "Invalid quantity."

    if value > MAX_POSITION_VALUE:
        return False, (
            "Position exceeds maximum "
            "paper position value."
        )

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

    account = get_account()

    symbol = symbol.upper()

    quantity = int(
        quantity
    )

    price = float(
        price
    )

    position = account[
        "positions"
    ].get(
        symbol
    )

    if not position:
        return False, (
            "No paper position exists."
        )

    if quantity <= 0:
        return False, (
            "Invalid quantity."
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

        if price is None:
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

    save_account(
        account
    )
