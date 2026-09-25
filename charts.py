import plotly.graph_objects as go


def candlestick_chart(
    df,
    symbol
):

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=symbol
        )
    )

    for column, name in [
        ("ema9", "EMA 9"),
        ("ema21", "EMA 21"),
        ("sma20", "SMA 20"),
        ("sma50", "SMA 50"),
        ("sma200", "SMA 200"),
        ("vwap", "VWAP")
    ]:

        if column in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df["datetime"],
                    y=df[column],
                    mode="lines",
                    name=name
                )
            )

    fig.update_layout(
        height=600,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        )
    )

    return fig


def oscillator_chart(
    df,
    columns,
    title
):

    fig = go.Figure()

    for column in columns:

        if column in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df["datetime"],
                    y=df[column],
                    mode="lines",
                    name=column.upper()
                )
            )

    fig.update_layout(
        title=title,
        height=300,
        template="plotly_dark",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig


def volume_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["datetime"],
            y=df["volume"],
            name="Volume"
        )
    )

    fig.update_layout(
        title="Volume",
        height=280,
        template="plotly_dark"
    )

    return fig
