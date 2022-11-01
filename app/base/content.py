import io
import zipfile

import pandas as pd
# import pydeck as pdk
import plotly.express as px
import plotly.io as pio
import streamlit as st
from streamlit.components.v1 import html

from .sidebar import PAGES

pio.templates.default = "none"

FOOTNOTE_SHORT = """
    A <a href='https://culturehack.io' style='text-decoration: none'>Culture Hack Labs</a> project. Copyright © 2022.
    """

ADD_MORE_CONTEXT_IF_PDF_ROWS = 3
CONTEXT_SIZE = 10
HEIGHT = 700
LEGEND = "<p align='center'><b>{}</b></p>"
MAX_OBJECTS = 10
MAX_ROWS = 100



class Content():

    def init__(self):
        pio.templates.default = "none"

    def content(self) -> None:
        self.title(PAGES[st.session_state.page], h=1, spacing=False)

        # Reset previously applied settings on page change.
        if st.session_state.page != st.session_state.get("last_shown"):
            st.session_state.last_shown = st.session_state.page
            st.session_state.pagination = 0
            st.session_state.scale_y = 0

        # Content containers.
        a1, a2 = st.container(), st.container()

        with a2:
            self.__content_kwic()
            self.__content_download()

        # Display main content area, depending on selected page.
        with a1:

            if st.session_state.page == "overview":
                self.__content_overview()

            elif st.session_state.page not in st.session_state.artifacts:
                self.warning(f"Artifact missing or not implemented.")
                return

            elif not len(st.session_state.artifacts[st.session_state.page]):
                self.info(f"No objects of this type identified.")
                return

            else:
                self.__content_artifact()

    def __content_artifact(self) -> None:
        artifact = st.session_state.artifacts[st.session_state.page]
        artifact_over_time = st.session_state.artifacts.get(f"{st.session_state.page}_over_time")

        st.write(
            "Displaying `%s` out of `%s` most occurring objects identified in `%s` rows%s%s%s.\n#" % (
                min(artifact.shape[0], MAX_OBJECTS),
                artifact.shape[0],
                st.session_state.series.shape[0],
                ", being the highest frequent term: **%s** (`%s` occurrences)" % (
                    artifact.index[0], artifact[0]) if len(artifact.index) else "",
                ", followed by **%s** (`%s`)" % (
                    artifact.index[1], artifact[1]) if len(artifact.index) > 1 else "",
                " and **%s** (`%s`)" % (
                    artifact.index[2], artifact[2]) if len(artifact.index) > 2 else "",
            )
        )

        # Left and right top-most content areas.
        columns = st.columns([1, 4])

        with columns[0]:
            self._chart_title("Most frequent keywords" if st.session_state.kwic_keywords else "Most frequent objects")

            # Some columns defined below are only used to adjust width,
            # as Streamlit has not yet implemented centered alignment.
            c1_content = st.container()
            c1_pagination = st.columns([0.02, 0.1, 0.1, 0.1, 0.1, 0.02])
            c1_checkbox = st.columns([0.15, 1])

            # Adjust height and display checkbox.
            with c1_checkbox[1]:
                st.write("###")
                st.checkbox("Normalize frequencies.", key="normalize")

            # Handle simple pagination through displayed results.
            pagination = st.session_state.pagination
            pagination_max = int(artifact.shape[0] / MAX_OBJECTS) + (1 if (artifact.shape[0] % MAX_OBJECTS) > 0 else 0)
            pagination_disabled = True if st.session_state.kwic_keywords else False

            if c1_pagination[1].button("⟨⟨", disabled=(pagination == 0) or pagination_disabled):
                st.session_state.pagination = 0

            if c1_pagination[2].button("⟨", disabled=(pagination == 0) or pagination_disabled):
                st.session_state.pagination -= (1 if st.session_state.pagination > 0 else 0)

            if c1_pagination[3].button("⟩", disabled=(pagination == pagination_max - 1) or pagination_disabled):
                st.session_state.pagination += (1 if st.session_state.pagination + 1 < pagination_max else 0)

            if c1_pagination[4].button("⟩⟩", disabled=(pagination == pagination_max - 1) or pagination_disabled):
                st.session_state.pagination = pagination_max - 1

            self.rerun(pagination != st.session_state.pagination)
            pagination_range = self._get_pagination_range(artifact.shape[0], pagination_max)

            # Display left data frame filtered by keywords.
            if st.session_state.kwic_keywords and type(artifact_over_time) != type(None):
                c1_content.table(
                    pd
                    .DataFrame(
                        [[i, v] for i, v in (
                            zip(
                                artifact[artifact.index.isin(st.session_state.keywords_)].index,
                                artifact[artifact.index.isin(st.session_state.keywords_)].values
                            )
                        )],
                        columns=["", "Hits (%)" if st.session_state.normalize else "Hits"],
                        index=[x + 1 for x in artifact.index.get_indexer(
                               artifact[artifact.index.isin(st.session_state.keywords_)].index)],
                    )
                    .map(
                        lambda x: f"{float(100*x/st.session_state.series.shape[0]):.2f}"
                                if st.session_state.normalize and type(x) == int else x
                    )
                )

            # Display left data frame with pagination.
            else:
                c1_content.table(
                    pd
                    .DataFrame(
                        [[i, v] for i, v in (
                            zip(
                                artifact[pagination_range[0]:pagination_range[1]].index,
                                artifact[pagination_range[0]:pagination_range[1]].values
                            )
                        )],
                        columns=["", "Hits (%)" if st.session_state.normalize else "Hits"],
                        index=list(range(pagination_range[0]+1, pagination_range[1]+1))
                            [:artifact[pagination_range[0]:pagination_range[1]].shape[0]],
                    )
                    .map(
                        lambda x: f"{float(100*x/st.session_state.series.shape[0]):.2f}"
                                  if st.session_state.normalize and type(x) == int else x
                    )
                )

        with columns[1]:
            if type(artifact_over_time) == type(None):
                self._chart_title("Most frequent objects")

                # Display right chart.
                st.altair_chart(
                    self.altair_chart(
                        artifact[pagination_range[0]:pagination_range[1]],
                        height=550,
                        kind="bar",
                        scale_y=[0, int(artifact.max())],
                        sort="-y",
                    ),
                    use_container_width=True,
                )

            elif st.session_state.kwic_keywords:
                self._chart_title("Keywords over time")

                # Display right chart.
                st.altair_chart(
                    self.altair_groupchart(
                        artifact_over_time[
                            artifact_over_time["category"]
                            .isin(st.session_state.keywords_)
                        ]
                        .sort_values(
                            by="category",
                            key=lambda x: x.map(lambda e: artifact.index.tolist().index(e))
                            # key=lambda x: x.map(lambda e: st.session_state.keywords_.index(e))
                        )
                        ,
                        height=550,
                        kind="bar",
                        normalize=st.session_state.normalize,
                    ),
                    use_container_width=True,
                )

            else:
                self._chart_title("Objects over time")

                # Get Y axis scale for time series.
                if not st.session_state.scale_y:
                    st.session_state.scale_y = max(
                        [
                        artifact_over_time
                            [artifact_over_time["category"].isin(
                                artifact.index.tolist()[i * MAX_OBJECTS:(i + 1) * MAX_OBJECTS]
                            )]
                            [["value", "index"]]
                            .groupby("index").sum().max()["value"]
                        for i in range(pagination_max)
                        ]
                    )

                # Display right chart.
                st.altair_chart(
                    self.altair_groupchart(
                        artifact_over_time,
                        height=550,
                        kind="bar",
                        normalize=st.session_state.normalize,
                        scale_y=False if st.session_state.normalize else [0, st.session_state.scale_y],
                        sort=artifact.index.tolist()[pagination_range[0]:pagination_range[1]],
                    ),
                    use_container_width=True,
                )

        st.caption(
            ("Displaying keyword frequency only, please **reset** for full results. " if st.session_state.kwic_keywords else "") +
            "Hits count total number of rows in which an occurrence was found (normalize for percentages)." +
            (" Only non-zero intervals are shown in time series." if type(artifact_over_time) != type(None) else "")
        )

    def __content_download(self) -> None:
        self.title("Download analysis", h=3)
        st.write("Please press the button below to and download all resulting analysis files.")

        e = st.empty()
        disabled = st.session_state.get("download") is not None

        if e.button(
            "Thanks for downloading! 🎉" if disabled else "Compress",
            type="primary",
            disabled=disabled
        ):
            e.empty()

            with st.spinner(f"Compressing artifacts..."):
                # Create in-memory buffer to write and store zipped contents.
                with io.BytesIO() as buffer:
                    with zipfile.ZipFile(buffer, "w") as z:
                        for file_name, file_content in self._prepare_artifacts_for_download(st.session_state.artifacts).items():
                            z.writestr(file_name, file_content)
                    buffer.seek(0)
                    # Replace button widget.
                    e.download_button(
                        data=buffer,
                        file_name="CHL NLP Dashboard Analysis.zip",
                        key="download",
                        label="Download"
                    )

        st.caption(f"Total artifacts generated during analysis: `{len(st.session_state.artifacts)}`.")

    def __content_kwic(self) -> None:
        self.title("Keywords in context", h=3)

        # Spacing tested on 1920x1080 with sidebar.
        kwic_container = st.columns([10.4, 0.9, 0.7])
        kwic_checkbox = st.columns([2, 1.7, 1.3, 1.1, 1.2, 1])

        # Display options as checkbox widgets.
        with kwic_checkbox[0]:
            st.checkbox(
                "Wrap keywords ('a book' ≠ 'a great book').",
                key="kwic_wrap_keywords",
                value=True,
            )
        with kwic_checkbox[1]:
            st.checkbox(
                "Partial matching ('book' → 'books').",
                key="kwic_partial_matches",
                value=False,
            )
        with kwic_checkbox[2]:
            st.checkbox(
                "Case sensitive (AaBbCc).",
                key="kwic_case_sensitive",
                value=False,
            )
        with kwic_checkbox[3]:
            st.checkbox(
                "Count occurrences.",
                key="kwic_value_counts",
                value=False,
            )
        with kwic_checkbox[4]:
            st.checkbox(
                "Display whole context.",
                key="kwic_whole_context",
                value=False,
            )
        with kwic_checkbox[5]:
            if st.session_state.page != "overview":
                st.checkbox(
                    "Multi-selector.",
                    key="kwic_multiselect",
                    value=True,
                )

        # Reset button widget.
        with kwic_container[2]:
            st.write("#")  # Adjust height.
            if st.button("Reset", disabled=(not st.session_state.get("kwic_keywords"))):
                st.session_state.kwic_keywords = (
                    ""
                    if
                        st.session_state.page == "overview"
                    else
                        []
                    if
                        st.session_state.get("kwic_multiselect")
                    else
                        False
                )
                # st.session_state.pop("kwic_keywords")
                self.rerun(True)

        # Keyword selector widget.
        with kwic_container[0]:
            if st.session_state.page == "overview":
                st.text_input(
                    "Please enter one or more keywords below for context analysis (comma separated).",
                    "",
                    key="kwic_keywords",
                )

            elif st.session_state.kwic_multiselect:
                st.multiselect(
                    "Please select one or more keywords below for context analysis.",
                    options=st.session_state.artifacts[st.session_state.page].index.tolist()[:100],
                    default=[],
                    key="kwic_keywords",
                    format_func=lambda x:
                        f"{x} ({st.session_state.artifacts[st.session_state.page][x]})",
                    # When reaching 10 keywords, colors from default scheme start looping, so
                    # this selector would ideally be disabled based on this threshold; however,
                    # the selector widget still allows interaction if opened when disabled.
                    # disabled=len(st.session_state.get("kwic_keywords") or []) > 10,
                )

            else:
                st.selectbox(
                    "Please select a keyword below for context analysis.",
                    options=[False] + st.session_state.artifacts[st.session_state.page].index.tolist()[:100],
                    index=0,
                    key="kwic_keywords",
                    format_func=lambda x:
                        "Choose an option" if x == False else
                        f"{st.session_state.artifacts[st.session_state.page].index.tolist().index(x)+1}. "
                        f"{x} ({st.session_state.artifacts[st.session_state.page][x]})",
                )

        if st.session_state.kwic_keywords:
            # Construct keywords in context data frame.
            kwic = pd.concat([
                self._build_kwic(
                    st.session_state.series,
                    # Caches returned data from self.kwic() for each keyword.
                    self.cache_data(
                        self.kwic,
                        series=st.session_state.series,
                        keywords=(keyword if st.session_state.kwic_case_sensitive else keyword.lower()).strip(),
                        case_sensitive=st.session_state.kwic_case_sensitive,
                        whole_words=False if st.session_state.kwic_partial_matches else True,
                        wrap_keywords=st.session_state.kwic_wrap_keywords,
                    ),
                    add_more_context_if_pdf_rows=ADD_MORE_CONTEXT_IF_PDF_ROWS,
                    context_size=None if st.session_state.kwic_whole_context else CONTEXT_SIZE,
                    value_counts=st.session_state.kwic_value_counts,
                )
                for keyword in self._prepare_keywords(st.session_state.kwic_keywords)
            ])

            # Sort and reindex data frame.
            if st.session_state.kwic_value_counts:
                kwic.sort_values(by="Occurrences", ascending=False, inplace=True)
                kwic.index = range(kwic.shape[0])

            # Display preview of first MAX_ROWS rows.
            with st.expander(
                f"Preview matches ({kwic['Occurrences'].sum() if st.session_state.kwic_value_counts else len(kwic)})",
                expanded=True,
            ):
                st.table(kwic[:MAX_ROWS])

            # Store proper keywords in a list.
            st.session_state.keywords_ = [
                keyword.strip() for keyword in (
                    st.session_state.kwic_keywords.split(",") if isinstance(st.session_state.kwic_keywords, str) else st.session_state.kwic_keywords
                )
            ]

        with kwic_container[1]:
            st.write("#")  # Adjust height.
            e = st.empty()

            if e.button(
                "Download" if st.session_state.get("kwic_download") else "Compress",
                key="kwic_button",
                disabled=(st.session_state.get("kwic_download") is not None or not st.session_state.kwic_keywords),
            ):
                e.empty()

                # Create in-memory buffer to write and store zipped contents.
                with st.spinner(f"Preparing `{len(st.session_state.artifacts)}` download..."):
                    with io.BytesIO() as buffer:
                        with zipfile.ZipFile(buffer, "w") as z:
                            z.writestr(
                                "Keywords in Context.csv",
                                kwic.to_csv().encode("utf-8")
                            )
                        buffer.seek(0)
                        # Replace button widget.
                        e.download_button(
                            data=buffer,
                            file_name="Keywords in Context.zip",
                            key="kwic_download",
                            label="Download",
                        )

        st.caption(
            f"Total occurrences might differ due to keyword matching rules."
            f" Preview limited to a maximum of `{MAX_ROWS}` top results and"
            f" `{CONTEXT_SIZE}` tokens to the left and right, unless whole context is displayed."
        )

    def __content_overview(self) -> None:
        st.write(
            "The analysis was performed considering `%s`%s%s row(s)%s and finished in `%ss` %s." % (
                st.session_state.series.shape[0],
                " unique" if st.session_state.config["rows"]["unique"] else "",
                " random" if st.session_state.config["rows"]["random"] else "",
                " using the `%s` model for natural language processing" % st.session_state.config["model"] if st.session_state.config["model"] else "",
                st.session_state.time_elapsed,
                ", ".join([
                    "with %s filtered by %s" % (
                        k.split("_")[1],
                        " and ".join([f"{k} `{v}`" for k, v in st.session_state.config.get(k).items()]).rstrip()
                    )
                    for k in list(
                        k
                        for k in st.session_state.config.keys()
                        if k.startswith("filter_")
                        and any(st.session_state.config[k].get(j) for j in st.session_state.config[k])
                    )
                ]).rstrip(",") or ""
            )
        )

        st.write("#")
        columns = st.columns([2, 3])

        with columns[0]:

            if "time_series" in st.session_state.artifacts:
                self._chart_title("Time series")

                st.altair_chart(
                    self.altair_chart(
                        st.session_state.artifacts["time_series"],
                        height=350,
                        interpolate="linear",
                        kind="line",
                        # scale_y=True,
                    ),
                    use_container_width=True,
                )

            self._chart_title("Most frequent words")

            st.altair_chart(
                self.altair_chart(
                    st.session_state.artifacts["tokens"][:15 if "time_series" in st.session_state.artifacts else 30],
                    height=400 if "time_series" in st.session_state.artifacts else 815,
                    transpose=True,
                    sort="-x",
                ),
                use_container_width=True,
            )

            st.caption(
                "Objects displayed in this chart (unigrams) do not consider stopwords or words of length `< 2`."
            )

        with columns[1]:
            self._chart_title("Word cloud")

            # Requires internet connection.
            html(
                st.session_state.artifacts["wordcloud"],
                width=900,
                height=815,
                scrolling=False
            )

            st.caption(
                "Number of words in cloud limited to `100` with highest frequences."
                " Layout by Jason Davies [[1](https://www.jasondavies.com/wordcloud/)]"
                " and algorithm due to Jonathan Feinberg [[2](https://web.archive.org/web/20210417162014/http://static.mrfeinberg.com/bv_ch03.pdf)]."
            )

    @staticmethod
    def _chart_title(title) -> None:
        st.write(LEGEND.format(title), unsafe_allow_html=True)

    @staticmethod
    def _get_pagination_range(shape, maximum) -> list:
        ranged = [
            st.session_state.pagination * MAX_OBJECTS,
            min(shape, MAX_OBJECTS * (st.session_state.pagination + 1))
        ]
        if maximum == st.session_state.pagination:
            ranged[0] += (shape - ranged[1])
        return ranged

    @staticmethod
    def _prepare_artifacts_for_download(artifacts):
        output = {}

        for name, artifact in artifacts.items():
            title = PAGES\
                    .get(name.replace("_over_time", ""), name.capitalize())\
                    .replace(":", " -")\
                    .replace("_", " ")\
                    + (" over time" if "over_time" in name else "")

            if name == "wordcloud":
                output[f"{title}.html"] = artifact

            else:
                index = False

                if type(artifact) == pd.Series:
                    artifact.name = "value"
                    artifact.index.name = "index"
                    index = True

                try:
                    output[f"{title}.csv"] = artifact.to_csv(index=index).encode("utf-8")
                except:
                    output[f"{title}.csv"] = artifact.to_csv(index=index).encode("utf-16")

                # Export image with Plotly.
                # To-do: replace with Altair.
                # if "over_time" in name:
                #     plot = px.bar(
                #         pd.DataFrame({
                #             "x": [x[0] for x in artifact.index],
                #             "y": artifact.values,
                #             "Category": [x[1] for x in artifact.index]
                #         }),
                #         x="x",
                #         y="y",
                #         color="Category",
                #         title=title,
                #     )
                #     title += " Over Time"
                # else:
                #     plot = px.bar(
                #         artifact,
                #         title=title,
                #         orientation="v" if name == "time_series" else "h"
                #     )
                # output[f"{title}.html"] = plot.to_html()
                # output[f"{title}.png"] = plot.to_image()

        return output
