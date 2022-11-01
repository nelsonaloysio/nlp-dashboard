import streamlit as st

PAGES = {
    # "configure": "Configuration",
    "overview": "Overview",
    "bigrams": "Bigrams",
    "ents_loc": "Entities: Locations",
    # "ents_org": "Entities: Organizations",
    "ents_person": "Entities: Persons",
    "ents_gpe": "Geopolitical Entities",
    "hashtags": "Hashtags",
    "mentions": "Mentions",
    "noun_chunks": "Noun features",
    "pos_adj": "Parts-of-Speech: Adjectives",
    "pos_noun": "Parts-of-Speech: Nouns",
    "pos_verb": "Parts-of-Speech: Verbs",
    "trigrams": "Trigrams",
    "tokens": "Unigrams",
}

REQUIRES_NLP = (
    "ents_loc",
    "ents_person",
    "ents_gpe",
    "noun_chunks",
    "pos_adj",
    "pos_noun",
    "pos_verb",
)

FOOTNOTE = """
    A <a href="https://culturehack.io" style="text-decoration: none">Culture Hack Labs</a> project.
    © 2022-2023.
    """


class Sidebar():

    def sidebar(self):
        st.title("Navigation")

        st.radio(
            " ",
            key="page",
            index=0,
            options=list(page for page in PAGES if self.__is_enabled(page)),
            label_visibility="collapsed",
            disabled="artifacts" not in st.session_state,
            format_func=lambda x: PAGES[x],
        )

        st.write("") #  Adjust height

        if "artifacts" in st.session_state:
            if st.button("Reconfigure settings"):
                st.session_state.pop("artifacts", None)
                self.rerun()

        elif st.button("Reset app", disabled="config" not in st.session_state):
            list(st.session_state.pop(x) for x in st.session_state)
            self.rerun()

        st.write("")  # Adjust height
        st.caption(FOOTNOTE, unsafe_allow_html=True)

    @staticmethod
    def __is_enabled(page=None):
        if page in REQUIRES_NLP and st.session_state.get("model_disabled"):
            return False
        return True
