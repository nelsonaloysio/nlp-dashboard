import streamlit as st

PREVIEW_ROWS = 50


@classmethod
def configure_preview(self):
    if len(st.session_state.get("data", [])):

        with st.expander("Preview sample"):
            # Using .astype(str) as a workaround to [apache/arrow#18854].
            st.dataframe(st.session_state.data.astype(str)[:PREVIEW_ROWS],
                            use_container_width=True)

        self.success(f"Loaded `{st.session_state.data.shape[0]}` rows "
                    f"and `{st.session_state.data.shape[1]}` columns "
                    f"from `{st.session_state.files}` files.")