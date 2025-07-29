import streamlit as st
import pandas as pd
import os

# Path to your Excel file
EXCEL_FILE = "NGS_comments_automation.xlsx"

# List of disease sheet names (must match the sheet names in the Excel file)
DISEASE_SHEETS = ['AML', 'ALL', 'MDS', 'MPN', 'B lymphoid', 'T lymphoid', 'CLL', 'Myeloma', 'Histiocytic disorders', 'Other', 'CHIP']

# Streamlit app
st.title("Haem NGS Comments")
st.markdown("Search for relevant gene comments, panels and caveats.")

# --- Gene Comments Section ---
selected_disease = st.selectbox("Select Disease Type", DISEASE_SHEETS)
gene_input = st.text_input("Enter one or more gene symbols (comma-separated, e.g. TP53, NRAS, FLT3):")

if selected_disease and gene_input:
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=selected_disease, usecols="A:B")
        df.columns = ['Gene', 'Relevant_comments']

        input_genes = [gene.strip().upper() for gene in gene_input.split(",") if gene.strip()]
        filtered_df = df[df['Gene'].str.upper().isin(input_genes)]

        if not filtered_df.empty:
            st.success(f"Found {len(filtered_df)} matching comment(s):")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No comments found for the entered genes in the selected disease.")
    except Exception as e:
        st.error(f"Error loading gene comments: {e}")

# --- Panel Lookup Section ---
st.markdown("---")
st.markdown("### Panel Lookup")

try:
    panel_df = pd.read_excel(EXCEL_FILE, sheet_name="Panel")  # Load all columns

    # Make sure expected columns exist
    if 'Panel' in panel_df.columns and 'Genes' in panel_df.columns:
        panel_names = panel_df['Panel'].dropna().unique().tolist()
        selected_panel = st.selectbox("Select Panel Name:", [""] + panel_names)

        if selected_panel:
            result = panel_df[panel_df['Panel'] == selected_panel]
            if not result.empty:
                st.success("Panel genes found:")
                st.write(result.iloc[0]['Genes'])
            else:
                st.warning("No matching panel found.")
    else:
        st.error("Expected columns 'Panel' and/or 'Genes' not found in the sheet.")
except Exception as e:
    st.error(f"Error loading Panel data: {e}")


# --- Caveats Lookup Section ---
st.markdown("---")
st.markdown("### Caveats Lookup")

try:
    caveat_df = pd.read_excel(EXCEL_FILE, sheet_name="Caveats", usecols="A:B")
    caveat_df.columns = ['Caveat', 'Comment']  # Adjust to your actual headers

    caveat_terms = caveat_df['Caveat'].dropna().unique().tolist()
    selected_caveat = st.selectbox("Select Caveat Term:", [""] + caveat_terms)

    if selected_caveat:
        result = caveat_df[caveat_df['Caveat'] == selected_caveat]

        if not result.empty:
            st.success("Caveat comment found:")
            st.write(result.iloc[0]['Comment'])
        else:
            st.warning("No matching caveat found.")
except Exception as e:
    st.error(f"Error loading Caveats data: {e}")

