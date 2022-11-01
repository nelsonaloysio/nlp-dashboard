from datetime import datetime
from typing import Union

import numpy
import pandas as pd
import spacy
import streamlit as st
from streamlit.errors import StreamlitAPIException

from .models import (
    MODEL_GENRE,
    MODEL_LANGUAGE,
    MODEL_SIZE,
    MODEL_TYPE,
    MODELS_AVAILABLE
)

DEFAULT_MODEL_LANGUAGE = "English"
MAX_SLIDER = 100000

class Configure():

    def __init__(self) -> None:
        """ Initializes class. """

    def configure(self) -> None:
        st.subheader("Configuration")
        st.session_state.config = st.session_state.get("config", {})

        t1, t2 = st.tabs(["Required settings", "Optional settings"])

        with t2:
            if "data" in st.session_state:
                self.__config_columns()
                self.__config_dates()
                self.__config_rows()
                self.__config_filter_text()
                self.__config_filter_interval()
                self.__config_filter_dates()
                self.__config_stopwords()

            else:
                self.info("Please upload at least one file in the previous tab before proceeding to optional settings.")

        with t1:
            self.__config_data()
            self.__config_model()
            self.__config_analyze()

    def __config_analyze(self) -> bool:
        if "data" not in st.session_state:
            return

        self.title("Analyze data", h=4)
        st.write("Parse data set with the selected parameter settings.")

        disabled = st.session_state.config.get("model") is None and not st.session_state.model_disabled

        if disabled:
            self.warning("Please choose and load a model or disable natural language processing before proceeding.")

        else:
            if not st.session_state.config["dates"] or type(st.session_state.get("dates")) == type(None):
                self.info("Date field unavailable or unselected in optional settings. Time series analysis will be skipped.")

            # with st.expander("Review parameters"):
            #     st.write(st.session_state.config)

        container = st.empty()

        if container.button("Process", type="primary", disabled=disabled):
            container.empty()

            with container:
                try:
                    with st.spinner("Processing..."):
                        self.generate_artifacts()

                except Exception as e:
                    self.error(
                        f"Exception **{e}**: failed to process data.\n\n"
                        "Please try to refresh the page by pressing [`R`] or submit an issue containing the information below.\n\n"
                    )
                    st.write(e)

            if "artifacts" in st.session_state:
                st.session_state.pop("data", None)

            else:
                self.warning(f"Resulting series is empty (`{st.session_state.series.shape[0]}` rows). Please review the selected parameters and try again.")
                st.session_state.pop("series", None)

        st.caption(
                "Press the button above to commence analysis considering `%s` column(s)." % (
                    len(st.session_state.config.get("columns") or st.session_state.data.columns)
                )
            )

    def __config_columns(self) -> bool:
        self.title("Data selection", h=4, spacing=False)
        self.title("Column fields", h=5)

        options = st.session_state.data.columns.tolist()

        columns = st.multiselect(
            "Please select one or more fields below to consider for analysis.",
            default=[option for option in options if type(option) == str and any(_ in option.lower() for _ in ["text", "title", "sentence"])] or options,
            options=options,
        )

        if not columns:
            self.info("No column field selected. All uploaded data will be considered.")

        st.caption("Columns containing `text`, `title` or `sentence` in their names are selected by default if found.")
        st.session_state.config["columns"] = columns or None

    def __config_data(self) -> bool:
        self.title("File uploader", h=4, spacing=False)
        uploaded_files = self.uploader()

        if uploaded_files is not None:
            data = self.load_uploaded_files(uploaded_files)

            if len(data):
                st.session_state.data = data

            else:
                self.warning(f"Uploaded data seems to be empty: file unsupported or text unidentified.")

        if len(st.session_state.get("data", [])):
            self.success(f"Loaded `{st.session_state.data.shape[0]}` rows and `{st.session_state.data.shape[1]}` columns.")

            with st.expander("Preview sample"):
                # Using .astype(str) as a workaround to [apache/arrow#18854].
                st.dataframe(st.session_state.data.astype(str)[:50], use_container_width=True)

        if uploaded_files == False:
            self.warning("Please choose at least one file before uploading.")

        elif not uploaded_files and not "data" in st.session_state:
            self.info("Please upload at least one file before proceeding.")

    def __config_dates(self) -> bool:
        self.title("Date field", h=5)
        options = [False] + st.session_state.data.columns.tolist()
        default = [option for option in options if type(option) == str and any(_ in option.lower() for _ in ["date", "datetime", "time", "timestamp"])]
        disabled = 2 >= len(options)

        column = st.selectbox(
            "Please select the date field to consider for analysis. Allows timestamps.",
            disabled=disabled,
            index=options.index(default[0]) if default else 0,
            options=options,
            format_func=lambda x: "Choose an option" if x == False else x,
        )

        if column == options[0]:
            getattr(self, "info" if disabled else "warning")("No %s. Time series analysis will be skipped." % ("other columns available" if disabled else "column selected"))
            st.session_state.pop("dates", None)
            disabled = True

        elif st.session_state.data[column].shape[0] != self.__drop_empty(st.session_state.data[column]).shape[0]:
            self.error(f"Error: column contains empty values.")
            st.session_state.pop("dates", None)
            disabled = True

        elif len(dates := self.__to_datetime(st.session_state.data[column])):
            self.info(f"Selected date range goes from [`{dates.min()}`] to [`{dates.max()}`].")
            st.session_state.dates = dates

        st.session_state.config["dates"] = None if disabled else column
        st.caption("The first column named `date`, `datetime`, `time` or `timestamp` is selected by default if found.")

    def __config_filter_dates(self) -> bool:
        self.title("Date interval", h=5, spacing=1)
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
        options = [False] + st.session_state.data.columns.tolist()

        column = c1.selectbox(
            "Please select the field to filter dates from.",
            disabled=len(options) < 3,
            index=0,
            options=options,
            format_func=lambda x: "Choose an option" if x == False else x,
        )

        disabled = column == options[0]

        if not disabled:

            if not self.__drop_empty(st.session_state.data[column]).shape[0]:
                self.error(f"Error: column contains empty values only.")
                disabled = True

            elif st.session_state.data[column].shape[0] != self.__drop_empty(st.session_state.data[column]).shape[0]:
                self.error(f"Error: column contains empty values.")
                disabled = True

            elif not len(dates := self.__to_datetime(st.session_state.data[column])):
                disabled = True

        min_date = c2.date_input(
            "Please enter the minimum date/time.",
            disabled=disabled,
            value=None if disabled else dates.min(),
        )

        min_time = c3.time_input(
            " ",
            disabled=disabled,
            value=datetime.strptime("00:00:00", "%H:%M:%S"),
        )

        max_date = c4.date_input(
            "Please enter the maximum date/time.",
            disabled=disabled,
            value=None if disabled else dates.max(),
        )

        max_time = c5.time_input(
            "  ",
            disabled=disabled,
            value=datetime.strptime("23:59:59", "%H:%M:%S"),
        )

        st.session_state.config["filter_dates"] = {
            "column": None if disabled else column,
            "minimum": None if disabled else (min_date, min_time),
            "maximum": None if disabled else (max_date, max_time),
        }

        if not disabled and len(dates):
            index = self.filter_dates(dates, min_date, min_time, max_date, max_time)

            if not len(index):
                self.warning(f"No rows matched within the selected interval.")

            else:
                st.session_state.filter_dates = index
                self.info(f"Matching `{len(index)}` out of `{st.session_state.data.shape[0]}` rows ({float(len(index)/st.session_state.data.shape[0]*100):.2f}%).")

    def __config_filter_interval(self) -> bool:
        self.title("Numeric interval", h=5)
        c1, c2 = st.columns([1, 2])
        options = [False] + st.session_state.data.columns.tolist()

        column = c1.selectbox(
            "Please select the field to filter interval from.",
            disabled=len(options) < 3,
            index=0,
            options=options,
            format_func=lambda x: "Choose an option" if x == False else x,
        )

        disabled = column == options[0]
        min_value, max_value = (-1, 1)

        if not disabled:

            if not self.__drop_empty(st.session_state.data[column]).shape[0]:
                self.error(f"Error: column contains empty values only.")
                disabled = True

            elif st.session_state.data[column].shape[0] != self.__drop_empty(st.session_state.data[column]).shape[0]:
                self.error(f"Error: column contains empty values.")
                disabled = True

            elif min_max := self.__get_min_max(st.session_state.data[column]):
                min_value, max_value = min_max

            else:
                disabled = True

        with c2:
            # Avoids StreamlitAPIException caused by exceeding MAX_SLIDER.
            if not disabled and (max_value - min_value > MAX_SLIDER):
                c2a, c2b = st.columns(2)
                min_value = self.__number(c2a.text_input("Please enter the minimum value.", min_value))
                max_value = self.__number(c2b.text_input("Please enter the maximum value.", max_value))

            else:
                try:
                    min_value, max_value = st.slider(
                        "Please enter the range to filter.",
                        disabled=disabled,
                        min_value=min_value,
                        max_value=max_value,
                        value=(min_value, max_value),
                    )
                except StreamlitAPIException as e:
                    self.error(f"Maximum supported value exceeded: {e}.")

        st.session_state.config["filter_interval"] = {
            "column": None if disabled else column,
            "value": None if disabled else min_value,
            "maximum": None if disabled else max_value,
        }

        if not disabled:
            index = self.filter_interval(st.session_state.data[column], min_value, max_value)

            if not len(index):
                self.warning(f"No rows matched within the selected interval.")

            else:
                self.info(f"Matching `{len(index)}` out of `{st.session_state.data.shape[0]}` rows ({float(len(index)/st.session_state.data.shape[0]*100):.2f}%).")
                st.session_state.filter_interval = index

    def __config_filter_text(self) -> bool:
        self.title("Data filtering", h=4)
        self.title("Words in text", h=5)
        c1, c2 = st.columns([1, 2])
        c3, c4 = st.columns([1, 4])

        columns = c1.multiselect(
            "Please select the field(s) to filter text from.",
            options=st.session_state.data.columns.tolist(),
        )

        value = c2.text_input(
            "Please enter the tags to match below (comma-separated, example: `tag, another tag`).",
            disabled=columns == [],
            value="",
        )

        case_sensitive = c3.checkbox(
            "Consider case accents (AaBbCc).",
            disabled=columns == [],
            value=False,
        )

        partial_matches = c4.checkbox(
            "Consider partial matches ('book' => 'books').",
            disabled=columns == [],
            value=False,
        )

        if columns and value:
            value = [x.strip() for x in value.split(",")]
            index = self.filter_text(st.session_state.data[columns], value, case_sensitive=case_sensitive, whole_words=not partial_matches)

            if len(index):
                self.info(f"Matching `{len(index)}` out of `{st.session_state.data.shape[0]}` rows ({float(len(index)/st.session_state.data.shape[0]*100):.2f}%).")
                st.session_state.filter_text = index

            else:
                self.warning(f"No rows matched with the selected tags.")

        st.session_state.config["filter_text"] = {
            "columns": columns or None,
            "value": value or None,
        }

    def __config_model(self) -> bool:
        if "data" not in st.session_state:
            return

        self.title("Model selection", h=4)
        c1, c2, c3, c4 = st.columns([1.9, 2, 0.5, 1.25])
        c3.caption(""); c3.caption(""); c4.caption(""); c4.caption("")  # Adjust heights

        model = st.session_state.get("model")
        model_disabled = st.session_state.get("model_disabled", False)
        model_language = st.session_state.get("model_language", DEFAULT_MODEL_LANGUAGE)

        # Using `st.checkbox(...)` alone resulted in buggy behavior.
        # Workaround: `st.checkbox(...)` + `st.rerun()`.
        st.session_state.model_disabled = c4.checkbox(
            "Disable natural language processing.",
            # key="model_disabled",
            value=model_disabled
        )
        self.rerun(model_disabled != st.session_state.model_disabled)

        st.session_state.model_language = c1.selectbox(
            "Please select a language below.",
            disabled=st.session_state.model_disabled,
            index=list(MODEL_LANGUAGE).index(model_language),
            # key="model_language",
            options=MODEL_LANGUAGE,
        )
        self.rerun(model_language != st.session_state.model_language)

        if MODEL_LANGUAGE[st.session_state.model_language] == "zz":
            st.session_state.model = c2.text_input(
                "Please enter the model to use for NLP.",
                disabled=st.session_state.model_disabled,
                # key="model",
                value=st.session_state.config.get("model") if MODEL_LANGUAGE[model_language] == "zz" else "",
            )

        else:
            st.session_state.model = c2.selectbox(
                "Please select the model to use for NLP.",
                disabled=st.session_state.model_disabled,
                index=(
                    MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_language]].index(model)
                    if
                        model in MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_language]]
                    else
                        0
                ),
                # key="model",
                options=MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_language]],
            )
        self.rerun(model != st.session_state.model)

        model_loaded = (
            st.session_state.model == st.session_state.config.get("model")
            and not st.session_state.model_disabled
        )

        button = {
            "label": "Load model",
            "type": "primary",
            "disabled": (model_loaded or st.session_state.model_disabled or st.session_state.model == ""),
        }

        if (c3.button(**button) or model_loaded) and (model_loaded or self.__load_model(model)):
            self.rerun(model_loaded != True)
            self.success(f"Loaded model `{st.session_state.model}`.")

        elif st.session_state.model_disabled:
            self.info("No model selected. Not all analysis results will be available.")
            st.session_state.config["model"] = None
            st.session_state.pop("model_", None)

        elif MODEL_LANGUAGE[st.session_state.model_language] != "zz":
            model_type, model_genre, model_size = st.session_state.model.split("_")[1:]
            self.info("%s %s trained on %s." % (MODEL_SIZE.get(model_size, "").capitalize(),
                                                MODEL_TYPE.get(model_type, ""),
                                                MODEL_GENRE.get(model_genre, "")))

        st.caption("For details on available spaCy models and its usage, please check the [official library documentation](https://spacy.io/usage/models),")

    def __config_rows(self) -> bool:
        self.title("Number of rows", h=5)
        c = st.empty()
        c1, c2 = st.columns([1, 5])

        unique = c1.checkbox(
            "Consider only unique rows.",
            value=st.session_state.get("unique", False),
        )

        max_value = (
            st.session_state.data.drop_duplicates().shape[0]
            if
                unique
            else
                st.session_state.data.shape[0]
        )

        disabled = max_value < 2

        value = c.slider(
            "Please select the number of rows below to consider for analysis.",
            disabled=disabled,
            max_value=max_value,
            min_value=0 if disabled else 1,
            value=1 if disabled else max_value,
        )

        random = c2.checkbox(
            "Randomize rows for analysis.",
            disabled=value == max_value,
        )

        if disabled:
            value == st.session_state.data.shape[0]

        st.session_state.config["rows"] = {
            "value": value,
            "unique": unique,
            "random": None if value == max_value else random,
        }

    def __config_stopwords(self) -> bool:
        self.title("Stopwords", h=4)
        c1, c2 = st.columns([1, 2])
        options = [True, False, "catalan", "chinese", "english", "french", "german", "italian", "japanese", "portuguese", "russian", "spanish"]

        stopwords = c1.selectbox(
            "Please choose the language to consider for stopwords below.",
            options,
            index=0,
            format_func=lambda x: "All languages" if x == True else "Disable stopwords" if x == False else x.capitalize(),
        )

        c1.caption("By default, all available languages are considered.")

        custom_stopwords = c2.text_input(
            "Please enter any additional terms to block below (comma-separated).",
            value="",
        )

        c2.caption(
            'Example: `USA, United States of America`.'
        )

        st.session_state.config["stopwords"] = {
            "language": stopwords,
            "custom": [x.strip() for x in custom_stopwords.split()] or None,
        }

    def __drop_empty(self, series: pd.Series) -> bool:
        return series.apply(lambda x: None if str(x).strip() == "" else x).dropna()

    def __get_min_max(self, series: pd.Series) -> tuple:
        dtype = series.dtype.type

        if dtype == numpy.float64:
            dtype = float

        elif dtype == numpy.int64:
            dtype = int

        else:
            self.error(f"Error: column values do not have an expected type (`int`, `float`).")
            return

        try:
            return (dtype(series.min()), dtype(series.max()))

        except:
            self.error("Error: unable to obtain minimum and maximum values from column.")

    def __load_model(self, model) -> bool:
        st.session_state.config.pop("model_", None)

        try:
            try:
                self.cache_resource(spacy.load, model)

            except OSError:
                try:
                    with st.spinner("Downloading model..."):
                        spacy.cli.download(model)

                    self.cache_resource(spacy.load, model)

                except:
                    raise ModuleNotFoundError(model)

                else:
                    st.session_state.config["model"] = model

            else:
                st.session_state.config["model"] = model

        except Exception as e:
            self.error(f"Failed to obtain the selected `{e}` model from spaCy v{spacy.__version__}.")
            return False

        return True

    def __number(self, number: str) -> Union[float, int]:
        if any(_ in number for _ in (",", ".")):
            return float(number.replace(".", ","))
        return int(number)

    def __to_datetime(self, series: pd.Series) -> pd.Series:
        try:
            try:
                dates = pd.to_datetime(series, unit="s")
                # dates = series.apply(lambda x: datetime.utcfromtimestamp(x))

            except:
                dates = pd.to_datetime(series, infer_datetime_format=True)

        except:
            dates = []

        if not len(dates) or not len(dates.dropna()):
            self.error("Error: unable to infer date information from selected column.")
            dates = []

        return dates
