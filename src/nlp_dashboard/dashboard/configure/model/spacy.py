import spacy
import streamlit as st

from .spacy_models import (
    MODEL_GENRE,
    MODEL_LANGUAGE,
    MODEL_SIZE,
    MODEL_TYPE,
    MODELS_AVAILABLE
)

DEFAULT_MODEL_LANGUAGE = "English"


@classmethod
def configure_model_spacy(self) -> None:
    self.title("Language model", h=5)

    c1, c2, c3 = st.columns([2, 3, 0.5])

    # Adjust height.
    c3.caption("")
    c3.caption("")

    model_spacy = st.session_state.get("model_spacy")
    model_spacy_language = st.session_state.get("model_spacy_language", DEFAULT_MODEL_LANGUAGE)

    # NOTE: `st.checkbox(...)` resulted in buggy behavior with `key=...`.
    # Workaround: `st.session_state... = st.checkbox(...)` + `st.rerun()`.
    st.session_state.model_spacy_language = c1.selectbox(
        "Please select a language below.",
        index=list(MODEL_LANGUAGE).index(model_spacy_language),
        # key="model_spacy_language",
        options=MODEL_LANGUAGE,
    )

    if model_spacy_language != st.session_state.model_spacy_language:
        st.rerun()

    if MODEL_LANGUAGE[st.session_state.model_spacy_language] == "zz":
        st.session_state.model_spacy = c2.text_input(
            "Please enter the model to use for natural language processing.",
            # key="model_spacy",
            value=st.session_state.config.get("model_spacy") if MODEL_LANGUAGE[model_spacy_language] == "zz" else "",
        )

    else:
        st.session_state.model_spacy = c2.selectbox(
            "Please select the model to use for natural language processing.",
            index=(
                MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_spacy_language]].index(model_spacy)
                if
                    model_spacy in MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_spacy_language]]
                else
                    0
            ),
            # key="model_spacy",
            options=MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_spacy_language]],
        )

    if model_spacy != st.session_state.model_spacy:
        st.rerun()

    model_spacy_loaded = st.session_state.model_spacy == st.session_state.config.get("model_spacy")

    button = {
        "label": "Load model",
        "type": "primary",
        "key": "load_model_spacy",
        "disabled": model_spacy_loaded,
    }

    if (c3.button(**button) or model_spacy_loaded):

        if not model_spacy_loaded:
            st.session_state.config.pop("model_spacy_", None)

            try:
                model_spacy_ = self.cache_resource(load_model_spacy, model_spacy)

            except Exception as e:
                self.error(f"Failed to obtain the selected `{e}` model from spaCy {spacy.__version__}.")

            else:
                st.session_state.config["model_spacy"] = model_spacy
                st.session_state.model_spacy_ = model_spacy_

        if model_spacy_loaded != True:
            st.rerun()
        self.success(f"Loaded model `{st.session_state.model_spacy}`.")

    elif not model_spacy_loaded:
        st.session_state.config["model_spacy"] = None
        st.session_state.pop("model_spacy_", None)

    elif MODEL_LANGUAGE[st.session_state.model_spacy_language] != "zz":
        model_spacy_type, model_spacy_genre, model_spacy_size = st.session_state.model_spacy.split("_")[1:]
        self.info("%s %s trained on %s." % (MODEL_SIZE.get(model_spacy_size, "").capitalize(),
                                            MODEL_TYPE.get(model_spacy_type, ""),
                                            MODEL_GENRE.get(model_spacy_genre, "")))

    st.caption("For details on available language models, please check the "
               "[official library documentation](https://spacy.io/usage/models).")


@staticmethod
def load_model_spacy(model):
    try:
        model_ = spacy.load(model)

    except OSError:
        try:
            with st.spinner("Downloading model..."):
                spacy.cli.download(model)

            model_ = spacy.load(model)

        except:
            raise ModuleNotFoundError(model)

    return model_
