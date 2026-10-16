import streamlit as st

SIDEBAR = {
    "overview": "Overview",
    "bigrams": "Bigrams",
    "ents_gpe": "Entities: Geopolitical",
    "ents_loc": "Entities: Locations",
    # "ents_org": "Entities: Organizations",
    "ents_person": "Entities: Persons",
    "hashtags": "Hashtags",
    "mentions": "Mentions",
    "network": "Network",
    "noun_chunks": "Noun features",
    "pos_adj": "Parts-of-Speech: Adjectives",
    "pos_noun": "Parts-of-Speech: Nouns",
    "pos_verb": "Parts-of-Speech: Verbs",
    "power": "Power",
    "themes": "Themes",
    "trigrams": "Trigrams",
    "tokens": "Unigrams",
    "debug": "Debug",
}

REQUIRES_SPACY = (
    "ents_loc",
    "ents_person",
    "ents_gpe",
    "ents_org",
    "noun_chunks",
    "pos_adj",
    "pos_noun",
    "pos_verb",
)

FOOTNOTE = """
"""

DEBUG_ENABLED = True


@classmethod
def sidebar(self):
    st.title("Navigation")

    options = list(page for page in SIDEBAR if is_enabled(page))\
               if "artifacts" in st.session_state else []

    st.radio(
        " ",
        key="page",
        index=0,
        options=options,
        label_visibility="collapsed",
        disabled="artifacts" not in st.session_state,
        format_func=SIDEBAR.get
    )

    st.write("") #  Adjust height

    if "artifacts" in st.session_state:
        if st.button("Reconfigure settings"):
            st.session_state.pop("artifacts", None)
            st.rerun()

    elif st.button("Reset app", disabled="config" not in st.session_state):
        list(st.session_state.pop(x) for x in st.session_state)
        st.rerun()

    st.write("")  # Adjust height
    st.caption(FOOTNOTE, unsafe_allow_html=True)


@staticmethod
def is_enabled(page=None):
    if page in REQUIRES_SPACY and st.session_state.config.get("model_spacy") is None:
        return False
    if page == "network" and st.session_state.artifacts.get("network") is None:
        return False
    if page in ("power", "themes") and st.session_state.config.get("model_hf") is None:
        return False
    if page == "debug" and not DEBUG_ENABLED:
        return False
    return True
