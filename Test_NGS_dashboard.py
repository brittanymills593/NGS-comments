import streamlit as st

st.set_page_config(layout="wide")


version = st.radio(
    "Select dashboard version:",
    [
        "Original version",
        "Updated version"
    ],
    horizontal=True
)


if version == "Original version":

    from old_dashboard import run_old_dashboard
    run_old_dashboard()


else:

    from new_dashboard import run_new_dashboard
    run_new_dashboard()
