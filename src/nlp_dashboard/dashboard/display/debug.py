import streamlit as st


@classmethod
def display_debug(self) -> None:
    st.write("Displaying objects stored in the `session_state` property.")
    ss = sorted(st.session_state)
    artifacts = sorted(st.session_state.artifacts)
    config = sorted(st.session_state.config)
    types = (str, int, float, bool)

    st.subheader("Parameters")
    with st.expander("Show parameters"):
        st.write({k: st.session_state[k] for k in ss if type(st.session_state[k]) in types})

    st.subheader("Configuration")
    with st.expander("Show configuration"):
        st.write({k: st.session_state.config[k] for k in config})

    st.subheader("Artifacts")
    artifacts = sorted(st.session_state.artifacts)
    for key in artifacts:
        with st.expander(f"Show `{key}` object of type `{type(st.session_state.artifacts[key])}`"):
            st.write(st.session_state.artifacts[key])

    st.subheader("Other objects")
    for key in ss:
        if key != "artifacts"\
        and type(st.session_state[key]) not in types:
            with st.expander(f"Show `{key}` object of type `{type(st.session_state[key])}`"):
                st.write(st.session_state[key])
