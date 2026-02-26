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


# --- CNV Lookup Section ---
st.markdown("---")
st.markdown("### CNV Lookup")

try:
    cnv_df = pd.read_excel(EXCEL_FILE, sheet_name="CNV", usecols="A:C")
    cnv_df.columns = ['Disease', 'Region', 'Comment']

    # Disease dropdown
    disease_options = [""] + sorted(cnv_df['Disease'].dropna().unique().tolist())
    selected_disease = st.selectbox("Select Disease:", disease_options)

    # Filter regions based on selected disease
    if selected_disease:
        filtered_regions = cnv_df[cnv_df['Disease'] == selected_disease]['Region'].dropna().unique().tolist()
        region_options = [""] + sorted(filtered_regions)
    else:
        region_options = [""]

    selected_region = st.selectbox("Select Region:", region_options)

    # Lookup only when both selected
    if selected_disease and selected_region:
        result = cnv_df[
            (cnv_df['Disease'] == selected_disease) &
            (cnv_df['Region'] == selected_region)
        ]

        if not result.empty:
            st.success("Comment found:")
            st.write(result.iloc[0]['Comment'])
        else:
            st.warning("No matching comment found.")

except Exception as e:
    st.error(f"Error loading CNV data: {e}")


# --- CNV Lookup Section ---
st.markdown("---")
st.markdown("### CNV Lookup")

try:
    # Read columns A, B, C
    cnv_df = pd.read_excel(EXCEL_FILE, sheet_name="CNV", usecols="A:C")
    cnv_df.columns = ['Disease', 'Region', 'Comment']

    # Get unique values for dropdowns
    disease_options = [""] + cnv_df['Disease'].dropna().unique().tolist()
    region_options = [""] + cnv_df['Region'].dropna().unique().tolist()

    # Dropdowns for Disease and Region
    selected_disease = st.selectbox("Select Disease:", disease_options)
    selected_region = st.selectbox("Select Region:", region_options)

    # Only search if both selections are made
    if selected_disease and selected_region:
        # Filter DataFrame based on selections
        result = cnv_df[
            (cnv_df['Disease'] == selected_disease) &
            (cnv_df['Region'] == selected_region)
        ]

        if not result.empty:
            st.success("Comment found:")
            st.write(result.iloc[0]['Comment'])
        else:
            st.warning("No matching comment found.")
except Exception as e:
    st.error(f"Error loading CNV data: {e}")



