import pandas as pd
import streamlit as st

from ..base.altair import altair_chart, altair_groupchart

MAX_OBJECTS = 10

capitalizer = lambda x: " ".join([_.capitalize() for _ in x.split()])


@classmethod
def display_artifact(self) -> None:
    artifact = st.session_state.artifacts[st.session_state.page]
    artifact_over_time = st.session_state.artifacts.get(f"{st.session_state.page}_over_time")
    themes = list(st.session_state.artifacts.get("themes", []))

    # NOTE: Streamlit does not support tab interaction,
    # so we render all tabs and hide the unselected ones.
    tabs = st.tabs([f"All results"] + [f"Theme {t}" for t in themes]) if themes else [st.container()]

    for t, tab in enumerate(tabs):
        if t and themes:
            artifact = st.session_state.artifacts["themes"][t][st.session_state.page]
            artifact_over_time = st.session_state.artifacts["themes"][t].get(f"{st.session_state.page}_over_time")

        with tab:
            if not len(artifact):
                st.info(f"No objects of this type identified.")
                continue

            containers = [st.container(), st.container()]

            with containers[1]:
                kwic, keywords = self.display_kwic(artifact, theme=t)

            with containers[0]:
                st.write(message_artifact(artifact, t))
                st.write()

                # Left: Most frequent objects.
                # Right: Time series or keywords over time.
                columns = st.columns([1, 4])

                with columns[0]:
                    pagination_range, pagination_max = display_artifact_left(artifact, kwic, keywords, artifact_over_time, t)

                with columns[1]:
                    chart = display_artifact_right(artifact, artifact_over_time, kwic, keywords, pagination_range, pagination_max, t)
                    st.altair_chart(chart, use_container_width=True)

                st.caption(message_caption(artifact_over_time, keywords))


def display_artifact_left(artifact, kwic, keywords, artifact_over_time, theme):
    st.write(f"<p align='center'><b>Most frequent {'keywords' if keywords else 'objects'}</b></p>",
            unsafe_allow_html=True)

    # Some columns defined below are only used to adjust width,
    # as Streamlit has not yet implemented centered alignment.
    c1_content = st.container()
    c1_pagination = st.columns([0.02, 0.1, 0.1, 0.1, 0.1, 0.02])
    c1_checkbox = st.columns([0.15, 1])

    # Adjust height and display checkbox.
    with c1_checkbox[1]:
        st.write("")
        st.checkbox("Normalize frequencies.", key=f"normalize_{theme}")
        if artifact_over_time is not None:
            st.checkbox("Expand time series.", key=f"empty_intervals", value=True)

    # Handle simple pagination through displayed results.
    pagination = st.session_state.pagination.get(theme, 0)
    pagination_max = int(artifact.shape[0] / MAX_OBJECTS) + (1 if (artifact.shape[0] % MAX_OBJECTS) > 0 else 0)
    pagination_disabled = True if keywords else False

    if c1_pagination[1].button("⟨⟨", key=f"b1{theme}", disabled=(pagination == 0) or pagination_disabled):
        st.session_state.pagination[theme] = 0

    if c1_pagination[2].button("⟨", key=f"b2{theme}", disabled=(pagination == 0) or pagination_disabled):
        st.session_state.pagination[theme] = pagination - (1 if pagination > 0 else 0)

    if c1_pagination[3].button("⟩", key=f"b3{theme}", disabled=(pagination == pagination_max - 1) or pagination_disabled):
        st.session_state.pagination[theme] = pagination + (1 if pagination + 1 < pagination_max else 0)

    if c1_pagination[4].button("⟩⟩", key=f"b4{theme}", disabled=(pagination == pagination_max - 1) or pagination_disabled):
        st.session_state.pagination[theme] = pagination_max - 1

    st.rerun() if pagination != st.session_state.pagination.get(theme, 0) else None
    pagination_range = get_pagination_range(pagination, artifact.shape[0], pagination_max)

    # Left table with custom keywords.
    if keywords and len(kwic):
        table = kwic["Keyword"].map(capitalizer).value_counts().reset_index(name="Hits").rename(columns={"Keyword": ""})
        # table = pd.DataFrame(
        #     kwic["Keyword"].value_counts(),
        #     columns=["", "Hits (%)" if st.session_state.get(f"normalize_{theme}") else "Hits"],
        # )

    # Left table filtered by keywords.
    elif keywords and artifact_over_time is None:
        table = pd.DataFrame(
            [[i, v] for i, v in (
                zip(
                    artifact[artifact.index.isin(keywords)].index,
                    artifact[artifact.index.isin(keywords)].values
                )
            )],
            columns=["", "Hits (%)" if st.session_state.get(f"normalize_{theme}") else "Hits"],
            index=[x + 1 for x in artifact.index.get_indexer(artifact[artifact.index.isin(keywords)].index)],
        )

    # Left table with pagination.
    else:
        table = pd.DataFrame(
            [[i, v] for i, v in (
                zip(
                    artifact[pagination_range[0]:pagination_range[1]].index,
                    artifact[pagination_range[0]:pagination_range[1]].values
                )
            )],
            columns=["", "Hits (%)" if st.session_state.get(f"normalize_{theme}") else "Hits"],
            index=list(range(pagination_range[0]+1, pagination_range[1]+1))[:artifact[pagination_range[0]:pagination_range[1]].shape[0]],
        )

    if st.session_state.get(f"normalize_{theme}"):
        table = table.map(lambda x: f"{float(100*x/st.session_state.series.shape[0]):.2f}" if type(x) == int else x)

    with c1_content:
        st.table(table)

    return pagination_range, pagination_max


def display_artifact_right(artifact, artifact_over_time, kwic, keywords, pagination_range, pagination_max, theme):
    if len(artifact) and (artifact_over_time is None or len(artifact_over_time) < 2):
        st.write(f"<p align='center'><b>Most frequent objects</b></p>", unsafe_allow_html=True)

        # Right chart without time information.
        chart = altair_chart(
            artifact[artifact.index.isin(keywords)]
            if keywords else artifact[pagination_range[0]:pagination_range[1]],
            # fill_with=st.session_state.artifacts["time_series"].index if "time_series" in st.session_state.artifacts else None,
            height=550,
            kind="bar",
            scale_y=[0, int(artifact.max())],
            sort="-y",
        )

    elif keywords:
        st.write(f"<p align='center'><b>Keywords over time</b></p>", unsafe_allow_html=True)

        # Right chart filtered by keywords.
        chart = altair_groupchart(
            get_keywords_over_time(artifact_over_time, kwic, keywords, theme),
            # fill_with=st.session_state.artifacts["time_series"].index if "time_series" in st.session_state.artifacts else None,
            height=550,
            kind="bar",
            stack="normalize" if st.session_state.get(f"normalize_{theme}") else True,
            to_datetime=st.session_state.get("empty_intervals"),
        )

    else:
        st.write(f"<p align='center'><b>Objects over time</b></p>", unsafe_allow_html=True)

        # TODO: Get max Y axis value for time series.
        '''
        scale_y = ...
        max([
            artifact_over_time[
                artifact_over_time["category"].isin(
                    artifact.index.tolist()[i * MAX_OBJECTS:(i + 1) * MAX_OBJECTS]
                )]
                [["value", "index"]]
                .groupby("index")
                .sum()
                .max()
                ["value"]
            for i in range(pagination_max)
        ])\
        if artifact_over_time is not None and pagination_max else None
        '''

        # Right chart with time information.
        chart = altair_groupchart(
            artifact_over_time,
            # fill_with=st.session_state.artifacts["time_series"].index if "time_series" in st.session_state.artifacts else None,
            height=550,
            isin=result.index.tolist()[pagination_range[0]:pagination_range[1]],
            kind="bar",
            stack="normalize" if st.session_state.get(f"normalize_{theme}") else True,
            scale_y=None,  # False if st.session_state.get(f"normalize_{theme}") else [0, scale_y],
            # sort=artifact.index.tolist()[pagination_range[0]:pagination_range[1]],
            sort_x="x",
            to_datetime=st.session_state.get("empty_intervals"),
        )

    return chart


def get_keywords_over_time(artifact_over_time, kwic, keywords, theme):
    if keywords and not len(kwic):
        return None

    if st.session_state.get(f"kwic_multiselect{theme}"):
        df = artifact_over_time

        df = df[df["category"].isin(keywords)]

        df = pd.concat([
            df[df["index"] == index][df["category"] == keyword]
            for index in df["index"].unique()
            for keyword in keywords
        ])

    else:
        df = pd.concat([
            st.session_state.dates.loc[kwic[kwic["Keyword"].map(capitalizer) == keyword].index]
                                  .value_counts()
                                  .to_frame()
                                  .reset_index(names="index")
                                  .assign(category=keyword).iloc[:, [0, 2, 1]]
                                  .rename(columns={"count": "value"})
            for keyword in kwic["Keyword"].map(capitalizer).unique()
        ])

    return df


def get_pagination_range(pagination, shape, maximum) -> list:
    ranged = [
        pagination * MAX_OBJECTS,
        min(shape, MAX_OBJECTS * (pagination + 1))
    ]
    if maximum == pagination:
        ranged[0] += (shape - ranged[1])
    return ranged


def message_artifact(artifact, theme) -> str:
    return "Displaying `%s` out of `%s` most occurring objects%s identified in `%s` rows%s%s%s." % (
        min(artifact.shape[0], MAX_OBJECTS),
        artifact.shape[0],
        f" from **Theme {theme}**" if theme else "",
        st.session_state.series.shape[0] if not theme else len(st.session_state.artifacts["themes"][theme]["index"]),
        ", being the highest frequent term: **%s** (`%s` occurrences)" % (
            artifact.index[0], artifact.iloc[0]) if len(artifact.index) else "",
        ", followed by **%s** (`%s`)" % (
            artifact.index[1], artifact.iloc[1]) if len(artifact.index) > 1 else "",
        " and **%s** (`%s`)" % (
            artifact.index[2], artifact.iloc[2]) if len(artifact.index) > 2 else "",
    )


def message_caption(artifact_over_time, keywords) -> str:
    return ("Displaying keywords in context only. " if keywords else "")+\
           "Hits count total number of rows in which an occurrence was found, or its percentages when normalized."+\
           (" Only non-zero time intervals are shown in the plot." if artifact_over_time is not None else "")


