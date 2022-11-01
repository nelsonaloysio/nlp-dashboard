import streamlit as st

import pandas as pd

from .reader import SUPPORTED_EXTENSIONS


@classmethod
def uploader(self) -> list:
    with st.form("uploader_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Please select one or more files to upload below.",
            accept_multiple_files=True,
            # on_change=self._uploader_callback,  # Disabled in forms
        )

        st.caption("Supported file extensions: %s." %
                   ", ".join(f"`.{extension.upper()}`" for extension in SUPPORTED_EXTENSIONS))

        c1, c2, c3 = st.columns([2, 8, 20])

        with c1:
            submit = st.form_submit_button(
                "Upload",
                type="primary" if "data" not in st.session_state else "secondary",
            )

    with c2:
        st.checkbox(
            "Consider uploaded files as single data points.",
            key="single_data_points",
            value=st.session_state.get("single_data_points", False)
        )

    with c3:
        st.checkbox(
            "Merge newly uploaded files with existing data.",
            disabled="data" not in st.session_state,
            key="merge_uploaded",
            value=st.session_state.get("merge_uploaded", False)
        )

    st.caption("Click on the 'Upload' button to upload selected files and optionally discard existing data.")

    if submit:
        if uploaded_files:
            data = [
                self
                .reader(uploaded_file)
                .map(lambda x: None if type(x) == str and x.strip() == "" else x)\
                .dropna(axis=0, how="all")\
                .fillna("")\
                for uploaded_file in uploaded_files
            ]

            st.session_state.files = st.session_state.get("files", 0) + len(data)

            if st.session_state.get("single_data_points"):
                data = pd.DataFrame(
                    [
                        pd
                        .DataFrame(data)
                        .astype(str)
                        .apply(" ".join, axis=1)
                        .to_frame()
                        .apply(" ".join, axis=0)
                        for data in data
                    ],
                    index=[data.index[0].rsplit("(", 1)[-1][:-1] for data in data]
                )
            else:
                data = pd.concat(data)

            if len(data):

                if data.shape[1] == 1 and data.columns[0] == 0:
                    data.columns = ["text"]

                if "data" in st.session_state and st.session_state.get("merge_uploaded"):
                    data = pd.concat([st.session_state.data, data])

                st.session_state.data = data

    elif not any(_ in st.session_state for _ in ("data", "series")):
        self.info("Please upload at least one file to proceed.")
