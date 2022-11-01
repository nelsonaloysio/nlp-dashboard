import altair as alt
import pandas as pd

from ...pipeline.base.time import fill_time_series


@staticmethod
def altair_chart(
    series: pd.Series,
    fill_with: pd.Index = None,
    height=600,
    interpolate=None,
    kind="bar",
    mark_opacity=1.0,
    scale_x=False,
    scale_y=False,
    sort="x",
    to_datetime=False,
    transpose=False,
    x="Index",
    y="Value",
):
    if series is None:
        return alt.Chart(None).properties(height=height).mark_bar()

    if fill_with is not None:
        series = fill_time_series(series, index=fill_with)

    if to_datetime:
        series.index = pd.to_datetime(series.index)

    if scale_y == True:
        scale_y = [min(0, series.min()), series.max()]

    chart = (
        getattr(
            alt
            .Chart(
                pd.DataFrame(
                    {x: v, y: k} if transpose else {x: k, y: v}
                    for k, v in series.items()
                )
            )
            .properties(height=height),
            f"mark_{kind}"
        )()
        .encode(
            x=alt.X(
                x,
                scale=alt.Scale(nice=False, domain=scale_x) if scale_x else alt.Scale(nice=True),
                sort=sort,
                title="",
            ),
            y=alt.Y(
                y,
                axis=alt.Axis(tickMinStep=1),
                scale=alt.Scale(nice=True, domain=scale_y) if scale_y else alt.Scale(nice=True),
                sort=sort,
                title="",
            ),
            tooltip=[x, y],
        )
        .configure_mark(
            opacity=mark_opacity,
        )
        .interactive()
    )

    if interpolate:
        chart = chart.mark_area(interpolate=interpolate)

    return chart


@staticmethod
def altair_groupchart(
    df: pd.DataFrame,
    fill_with: pd.Index = None,
    kind="bar",
    height=600,
    interpolate=None,
    mark_opacity=1.0,
    scale_x=False,
    scale_y=False,
    sort=None,
    stack=True,
    to_datetime=False,
    x="index",
    y="value",
    c="category",
):
    if df is None:
        return alt.Chart(None).properties(height=height).mark_bar()

    if sort:
        df = df[df[c].isin(sort)].copy()
        key = {v: i for i, v in enumerate(sort)}
        df[f"{c}_Sort"] = df[c].apply(key.get)
        df.sort_values([f"{c}_Sort", x], ascending=[True, True], inplace=True)

    if fill_with is not None:
        df = fill_time_series(df, index=fill_with)

    if to_datetime:
        df[x] = pd.to_datetime(df[x])

    chart = (
        getattr(
            alt
            .Chart(df)
            .properties(height=height),
            f"mark_{kind}"
        )()
        .encode(
            x=alt.X(
                x,
                scale=alt.Scale(nice=False, domain=scale_x) if scale_x else alt.Scale(nice=True),
                sort=None,
                title="",
            ),
            y=alt.Y(
                y,
                axis=alt.Axis(tickMinStep=0.1 if stack == "normalize" else 1),
                scale=alt.Scale(nice=True, domain=scale_y) if scale_y else alt.Scale(nice=True),
                sort=None,
                stack=stack,
                title="",
            ),
            color=alt.Color(c, sort=sort),
            order=alt.Order(field="color", sort="descending"),
            tooltip=[c, x, y],
        )
        .configure_mark(
            opacity=mark_opacity,
        )
        .interactive()
    )

    if interpolate:
        chart = chart.mark_area(interpolate=interpolate)

    return chart