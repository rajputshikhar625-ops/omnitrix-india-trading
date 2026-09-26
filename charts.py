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
        height=520,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#94a3b8")),
        xaxis=dict(gridcolor="rgba(30, 58, 82, 0.4)", zerolinecolor="rgba(30, 58, 82, 0.4)"),
        yaxis=dict(gridcolor="rgba(30, 58, 82, 0.4)", zerolinecolor="rgba(30, 58, 82, 0.4)")
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
                    name=column.upper(),
                    line=dict(width=2)
                )
            )

    fig.update_layout(
        title=dict(text=title, font=dict(size=12, color="#38bdf8")),
        height=240,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(gridcolor="rgba(30, 58, 82, 0.4)", zerolinecolor="rgba(30, 58, 82, 0.4)"),
        yaxis=dict(gridcolor="rgba(30, 58, 82, 0.4)", zerolinecolor="rgba(30, 58, 82, 0.4)")
    )

    return fig


def volume_chart(df):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["datetime"],
            y=df["volume"],
            name="Volume",
            marker_color="rgba(56, 189, 248, 0.6)"
        )
    )

    fig.update_layout(
        title=dict(text="Volume Analysis", font=dict(size=12, color="#38bdf8")),
        height=220,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(gridcolor="rgba(30, 58, 82, 0.4)", zerolinecolor="rgba(30, 58, 82, 0.4)"),
        yaxis=dict(gridcolor="rgba(30, 58, 82, 0.4)", zerolinecolor="rgba(30, 58, 82, 0.4)")
    )

    return fig
