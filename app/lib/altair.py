import altair as alt
import pandas as pd


class Altair():

    @staticmethod
    def altair_chart(
        series: pd.Series,
        height=600,
        interpolate=None,
        kind="bar",
        mark_opacity=1.0,
        scale_x=False,
        scale_y=False,
        sort="x",
        transpose=False,
        x="Index",
        y="Value",
    ):
        if type(series) == type(None):
            return alt.Chart(None).properties(height=height).mark_bar()

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
        kind="bar",
        height=600,
        mark_opacity=1.0,
        normalize=False,
        # scale_x=False,
        scale_y=False,
        sort=None,
        x="index",
        y="value",
        c="category",
    ):
        if type(df) == type(None):
            return alt.Chart(None).properties(height=height).mark_bar()

        if sort:
            key = {v: i for i, v in enumerate(sort)}
            df = df[df[c].isin(sort)].copy()
            df[f"{c}_Sort"] = df[c].apply(lambda x: key[x])
            df.sort_values([x, f"{c}_Sort"], ascending=[True, True], inplace=True)

        return (
            getattr(
                alt
                .Chart(df)
                .properties(height=height),
                f"mark_{kind}"
            )()
            .encode(
                x=alt.X(
                    x,
                    # scale=alt.Scale(nice=False, domain=scale_x) if scale_x else alt.Scale(nice=True),
                    sort=None,
                    title="",
                ),
                y=alt.Y(
                    y,
                    axis=alt.Axis(tickMinStep=0.1 if normalize else 1),
                    scale=alt.Scale(nice=True, domain=scale_y) if scale_y else alt.Scale(nice=True),
                    sort=None,
                    stack="normalize" if normalize else "zero",
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
