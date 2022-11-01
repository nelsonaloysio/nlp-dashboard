from urllib.error import URLError

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

from ..base.altair import altair_chart, altair_groupchart
from ...pipeline.base.wordcloud import wordcloud, wordcloud_html

capitalizer = lambda x: " ".join([_.capitalize() for _ in x.split()])


@classmethod
def display_overview(self) -> None:
    themes = list(st.session_state.artifacts.get("themes", []))

    # NOTE: Streamlit does not support tab interaction,
    # so we render all tabs and hide the unselected ones.
    tabs = st.tabs([f"All results"] + [f"Theme {t}" for t in themes]) if themes else [st.container()]

    for t, tab in enumerate(tabs):
        if not t: # 0
            artifact = st.session_state.artifacts["tokens"]
            artifact_over_time = st.session_state.artifacts.get("time_series")

        if t and themes:
            artifact = st.session_state.artifacts["themes"][t]["tokens"]
            artifact_over_time = st.session_state.artifacts["themes"][t].get("time_series")

        with tab:
            containers = [st.container(), st.container()]

            with containers[1]:
                kwic, keywords = self.display_kwic(artifact, theme=t)

            with containers[0]:
                st.write(message_overview() if not t else message_theme(t))
                st.write("")
                columns = st.columns([2, 3])

                with columns[0]:
                    # Time series and most frequent objects.
                    display_overview_left(artifact, artifact_over_time, kwic, keywords, t)

                with columns[1]:
                    # Word cloud.
                    display_overview_right(artifact, kwic, keywords, t)


@staticmethod
def display_overview_left(artifact, artifact_over_time, kwic, keywords, theme):
    has_time = "time_series" in st.session_state.artifacts and len(st.session_state.artifacts["time_series"])
    themes = list(st.session_state.artifacts.get("themes", []))

    if has_time:
        st.write(f"<p align='center'><b>Time series</b></p>", unsafe_allow_html=True)
        chart = altair_chart(None)

        if keywords:
            chart = altair_groupchart(
                get_keywords_over_time(kwic, keywords, theme),
                # fill_with=st.session_state.artifacts["time_series"].index,
                height=350,
                # interpolate="linear",
                kind="bar",
                # scale_y=True,
                # stack="zero",
                to_datetime=True,
            )

        elif themes and not theme:
            chart = altair_groupchart(
                get_themes_over_time(),
                fill_with=st.session_state.artifacts["time_series"].index,
                height=350,
                # interpolate="linear",
                kind="bar",
                # scale_y=True,
                # stack="zero",
                to_datetime=True,
            )

        else:
            chart = altair_chart(
                artifact_over_time,
                fill_with=st.session_state.artifacts["time_series"].index,
                height=350,
                # interpolate="linear",
                kind="line",
                to_datetime=True,
            )

        st.altair_chart(chart, use_container_width=True)

    st.write(f"<p align='center'><b>Most frequent {'keywords' if keywords else 'objeects'}</b></p>", unsafe_allow_html=True)
    chart = altair_chart(None)

    if has_time and themes and not theme:
        chart = altair_groupchart(
            get_tokens_over_themes(themes, theme, kwic, keywords, n_tokens=15 if has_time else 30),
            height=400 if has_time else 815,
            # scale_y=True,
            # transpose=True,
        )

    elif len(artifact):
        chart = altair_chart(
            get_tokens(artifact, kwic, keywords, theme, n_tokens=15 if has_time else 30),
            height=400 if has_time else 815,
            sort="-x",
            transpose=True,
        )

    elif len(all_objects := get_all_objects(theme)):
        chart = altair_chart(
            all_objects[:15 if has_time else 30],
            height=400 if has_time else 815,
            sort="-x",
            transpose=True,
        )

    else:
        st.info("No objects to display.")

    st.altair_chart(chart, use_container_width=True)

    st.caption("Objects displayed in this chart (unigrams) do not consider stopwords or words of length `< 2`.")


@staticmethod
def display_overview_right(artifact, kwic, keywords, theme):
    st.write(f"<p align='center'><b>Word cloud</b></p>", unsafe_allow_html=True)

    cloud = st.session_state.artifacts["themes"][theme]["wordcloud"]\
            if theme else\
            st.session_state.artifacts["wordcloud"]

    # NOTE: Word clouds are not always generated for custom keywords.
    if keywords:
        cloud = wordcloud(
            artifact.loc[
                artifact.index.intersection(
                    st.session_state.series
                    .loc[kwic.index]
                    .to_frame()
                    .apply(" ".join, axis=0)
                    .apply(lambda x: [_.capitalize() for _ in set(x.split())])
                    .explode()
                )
            ]
        )

    if cloud:
        try:
            html(wordcloud_html(cloud), width=900, height=815, scrolling=False)

        except URLError as e:
            st.warning(
                """
                **This content requires internet access.**
                Connection error: %s
                """
                % e.reason
            )
    else:
        st.info("No word cloud to display.")

    st.caption(message_wordcloud())


def get_all_objects(theme):
    return pd.concat([
        st.session_state.artifacts["themes"][theme][key]
        for key in ("hashtags", "mentions")
    ])


def get_keywords_over_time(kwic, keywords, theme):
    if keywords and not len(kwic):
        return None

    if st.session_state.get(f"kwic_multiselect{theme}"):
        df = st.session_state.artifacts["themes"][theme]["tokens_over_time"]\
             if theme else\
             st.session_state.artifacts["tokens_over_time"]

        df = df[df["category"].isin(keywords)]

        df = pd.concat([
            df.query(f"index == '{index}'").query(f"category == '{keyword}'")
            for index in df["index"].unique()
            for keyword in keywords
        ])

    else:
        kwic["Keyword"] = kwic["Keyword"].map(capitalizer)

        df = pd.concat([
            st.session_state.dates.loc[kwic[kwic["Keyword"] == keyword].index]
                                  .value_counts()
                                  .to_frame()
                                  .reset_index(names="index")
                                  .assign(category=keyword).iloc[:, [0, 2, 1]]
                                  .rename(columns={"count": "value"})
            for keyword in kwic["Keyword"].unique()
        ])

    return df


def get_themes_over_time():
    df = st.session_state.artifacts["themes_over_time"].copy()
    df["category"] = df["category"].map(lambda x: f"Theme {x}")
    return df


def get_tokens(artifact, kwic, keywords, theme, n_tokens=None):
    if keywords and not len(kwic):
        return None
    elif keywords and st.session_state.get(f"kwic_multiselect{theme}"):
        artifact = artifact[artifact.index.isin(keywords)]
    elif kwic is not None:
        artifact = kwic.loc[:, "Keyword"].map(capitalizer).value_counts()
    return artifact[:n_tokens]


def get_tokens_over_themes(themes, theme, kwic, keywords, n_tokens=None):
    if keywords and not len(kwic):
        return None

    concat = []

    if st.session_state.get(f"kwic_multiselect{theme}"):
        for t in themes:
            df = st.session_state.artifacts["themes"][t]["tokens"].to_frame()
            df.columns = ["value"]
            df.loc[:, "index"] = df.index
            df["category"] = str(t)
            concat.append(df)

        df = pd.concat(concat, axis=0)[["index", "category", "value"]]
        df["category"] = df["category"].map(lambda x: f"Theme {x}")

        df = df.loc[
            df.loc[:, ["index", "value"]]
            .groupby("index")
            .sum()
            .sort_values("value", ascending=False)
            [:n_tokens]
            .index
        ]

        if keywords:
            df = pd.concat([
                df[df["index"] == keyword]
                for keyword in keywords
                # for keyword in kwic["Keyword"].map(capitalizer).unique()
            ])

    else:
        cluster = pd.Series(
            st.session_state.artifacts["cluster"],
            index=st.session_state.series.index
        )\
        .map(lambda x: f"Theme {x}")

        kwic["Keyword"] = kwic["Keyword"].map(capitalizer)
        kwic["cluster"] = cluster.loc[cluster.index.intersection(kwic.index)]
        kwic = kwic.reset_index(drop=True)
        value_counts = kwic["Keyword"].value_counts().index

        df = pd.concat([
            kwic[kwic["Keyword"] == keyword]
                [kwic["cluster"] == cluster]
                [["Keyword", "cluster"]]
                .value_counts()
                .reset_index(name="value")
                .rename({"Keyword": "index", "cluster": "category"}, axis=1)
                .sort_values(["category", "index"])
            for keyword in value_counts
            for cluster in sorted(kwic["cluster"].unique())
        ])


    return df


def message_overview() -> str:
    time_series = st.session_state.get("dates")

    rows = st.session_state.series.shape[0]
    unique = st.session_state.config.get("rows", {}).get("unique", None)
    random = st.session_state.config.get("rows", {}).get("random", None)

    start = time_series.min() if time_series is not None else None
    end = time_series.max() if time_series is not None else None

    spacy_model = st.session_state.config.get("model_spacy", None)
    hf_model = (st.session_state.config.get("model_hf", None) or "").split("/")[-1]
    k = len(st.session_state.artifacts.get("themes", []))
    k = f"{k} automatically determined" if st.session_state.config.get("n_clusters") == "auto" else k

    filter_text = st.session_state.config.get("filter_text", {})
    filter_text = f"filtering text from columns `{filter_text['columns']}` for `{filter_text['value']}`"\
                  if filter_text.get('column') else ""

    filter_numeric = st.session_state.config.get("filter_numeric", {})
    filter_numeric = f"filtering interval from column `{filter_numeric['column']}` between `{filter_numeric['minimum']}` and `{filter_numeric['maximum']}`"\
                     if filter_numeric.get('column') else ""

    return f"Analysis performed considering `{rows}`"\
           f"{' unique' if unique else ''}"\
           f"{' random' if random else ''}"\
           f" row(s) from `{st.session_state.files}` files"\
           f"{f', from start date `{start}` to end date `{end}`' if time_series is not None else ''}"\
           f"{f', using the `{spacy_model}` model for natural language processing' if spacy_model else ''}"\
           f"{f', using the `{hf_model}` model for clustering embeddings' if hf_model else ''}"\
           f"{f', considering `{k}` themes determined by semantic similarity ' if hf_model else ''}"\
           f"{f', {filter_text}' if filter_text else ''}"\
           f"{f', {filter_numeric}' if filter_numeric else ''}"\
           "."


def message_theme(theme) -> str:
    time_series = st.session_state.artifacts["themes"][theme].get("time_series", None)

    rows = len(st.session_state.artifacts["themes"][theme]["index"])
    start = time_series.index.max() if time_series is not None else None
    end = time_series.index.max() if time_series is not None else None

    return f"**Theme {theme}** aggregates `{rows}` row(s) based on semantic similarity " \
           f"{f'from start date `{start}` to end date `{end}`.' if time_series is not None else '.'}"


def message_wordcloud() -> str:
    return "Number of words in cloud limited to `100` with highest frequences."\
           " Layout by Jason Davies"\
           " [[1](https://www.jasondavies.com/wordcloud/)]"\
           " and algorithm due to Jonathan Feinberg"\
           " [[2](https://web.archive.org/web/20210417162014/http://static.mrfeinberg.com/bv_ch03.pdf)]."
