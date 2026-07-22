import streamlit as st

st.set_page_config(layout="wide")

from old_dashboard import run_old_dashboard
from test_updates_dashboard import run_new_dashboard


version = st.radio(
    "Select dashboard version:",
    [
        "Original version",
        "Updated version"
    ],
    horizontal=True
)


if version == "Original version":

    run_old_dashboard()

else:

    run_new_dashboard()
