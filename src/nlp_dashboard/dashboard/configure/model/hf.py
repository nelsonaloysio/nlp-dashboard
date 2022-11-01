import streamlit as st
import transformers
from transformers import AutoModel, AutoTokenizer

from .hf_models import MODEL_DESCRIPTION, MODEL_LANGUAGE, MODELS_AVAILABLE

DEFAULT_MODEL_LANGUAGE = "English"


@classmethod
def configure_model_hf(self) -> None:
    self.title("Clustering model", h=5)

    c1, c2, c3 = st.columns([2, 3, 0.5])

    # Adjust height.
    c3.caption("")
    c3.caption("")

    model_hf = st.session_state.get("model_hf")
    model_hf_language = st.session_state.get("model_hf_language", DEFAULT_MODEL_LANGUAGE)

    # NOTE: `st.checkbox(...)` resulted in buggy behavior with `key=...`.
    # Workaround: `st.session_state... = st.checkbox(...)` + `st.rerun()`.
    st.session_state.model_hf_language = c1.selectbox(
        "Please select a language below.",
        index=list(MODEL_LANGUAGE).index(model_hf_language),
        # key="model_hf_language",
        options=MODEL_LANGUAGE,
    )

    if model_hf_language != st.session_state.model_hf_language:
        st.rerun()

    if MODEL_LANGUAGE[st.session_state.model_hf_language] == "zz":
        st.session_state.model_hf = c2.text_input(
            "Please enter the model to use for semantic analysis.",
            # key="model_hf",
            value=st.session_state.config.get("model_hf") if MODEL_LANGUAGE[model_hf_language] == "zz" else "",
        )

    else:
        st.session_state.model_hf = c2.selectbox(
            "Please select the model to use for semantic analysis.",
            index=(
                MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_hf_language]].index(model_hf)
                if
                    model_hf in MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_hf_language]]
                else
                    0
            ),
            # key="model_hf",
            options=MODELS_AVAILABLE[MODEL_LANGUAGE[st.session_state.model_hf_language]],
            format_func=lambda x: x.split("/", 1)[-1],
        )
    if model_hf != st.session_state.model_hf:
        st.rerun()

    model_hf_loaded = st.session_state.model_hf == st.session_state.config.get("model_hf")

    button = {
        "label": "Load model",
        "type": "primary",
        "key": "load_model_hf",
        "disabled": model_hf_loaded,
    }

    if (c3.button(**button) or model_hf_loaded):

        if not model_hf_loaded:
            st.session_state.config.pop("model_hf_", None)

            try:
                self.cache_resource(load_model_hf, model_hf)

            except Exception as e:
                self.error(f"Failed to obtain the selected `{e}` model from hf {transformers.__version__}.")

            else:
                st.session_state.config["model_hf"] = model_hf

        if model_hf_loaded != True:
            st.rerun()
        self.success(f"Loaded model `{st.session_state.model_hf}`.")

    elif not model_hf_loaded:
        st.session_state.config["model_hf"] = None
        st.session_state.pop("model_hf_", None)

    elif MODEL_LANGUAGE[st.session_state.model_hf_language] != "zz":
        self.info(MODEL_DESCRIPTION.get(st.session_state.model_hf, "Model description not available."))

    st.caption("For details on available pretrained models, please check the "
               "[official library documentation](https://huggingface.co/models).")


@staticmethod
def load_model_hf(model):
    try:
        AutoModel.from_pretrained(model)
        AutoTokenizer.from_pretrained(model)
        return model

    except OSError:
        raise ModuleNotFoundError(model)
