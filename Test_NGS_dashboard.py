import streamlit as st
import pandas as pd
import os

# Path to your Excel file
EXCEL_FILE = "NGS_comments_automation.xlsx"

# List of disease sheet names (must match the sheet names in the Excel file)
DISEASE_SHEETS = ['AML', 'ALL', 'MDS', 'MPN', 'B lymphoid', 'T lymphoid', 'CLL', 'Myeloma', 'Histiocytic disorders']

# Streamlit app
col1, col2 = st.columns([3.5, 1.5])

with col1:
    # Darker purple title
    st.markdown(
        "<h1 style='color:#2E004F;'>Haem NGS Comments</h1>",
        unsafe_allow_html=True
    )

with col2:
    st.image("Logo.jpg", width=250)

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
st.markdown("### Caveats Lookup (including CHIP and CNV)")

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


# --- CNV Lookup Section ---
st.markdown("---")
st.markdown("### CNV Lookup")

try:
    cnv_df = pd.read_excel(EXCEL_FILE, sheet_name="CNV", usecols="A:C")
    cnv_df.columns = ['Disease', 'Region', 'Comment']

    cnv_df["Disease"] = cnv_df["Disease"].astype(str).str.strip()
    cnv_df["Region"] = cnv_df["Region"].astype(str).str.strip()

    # Disease dropdown
    disease_options = [""] + sorted(cnv_df['Disease'].dropna().unique().tolist())
    selected_disease = st.selectbox("Select Disease (optional):", disease_options)

    # Region dropdown
    if selected_disease:
        region_options = [""] + sorted(
            cnv_df[cnv_df["Disease"] == selected_disease]["Region"].dropna().unique().tolist()
        )
    else:
        region_options = [""] + sorted(cnv_df["Region"].dropna().unique().tolist())

    selected_region = st.selectbox("Select Region:", region_options)

    # 🔎 Only search if region selected
    if selected_region:

        result = cnv_df.copy()

        if selected_disease:
            result = result[result["Disease"] == selected_disease]

        result = result[result["Region"] == selected_region]

        if not result.empty:
            st.success("Comment found:")
            st.write(result.iloc[0]["Comment"])
        else:
            st.warning("No matching comment found.")

except Exception as e:
    st.error(f"Error loading CNV data: {e}")


# --- Images Section (conditional on gene input) ---
if gene_input:  # only proceed if user has entered genes
    input_genes = [gene.strip().upper() for gene in gene_input.split(",") if gene.strip()]

    # Add a section header if at least one image will show
    if any(gene in ["DDX41", "RUNX1", "BCL2"] for gene in input_genes):
        st.markdown("---")
        st.markdown("### Figures from papers:")
        st.markdown("")  # spacing

    # --- DDX41 Images ---
if "DDX41" in input_genes:
    st.markdown("#### DDX41:")
    
    # Display images
    st.image("DDX41_1.png", use_container_width=True)
    st.image("DDX41_2.png", use_container_width=True)
    st.image("DDX41_3.png", use_container_width=True)
    
    # Display references below the images
    st.markdown(
        "[Reference 1: The genetic landscape of germline DDX41 variants](https://ashpublications.org/blood/article/140/7/716/485483/The-genetic-landscape-of-germline-DDX41-variants?guestAccessKey=)"
    )
    st.markdown(
        "[Reference 2: Germ-line DDX41 mutations define a unique subtype](https://ashpublications.org/blood/article/141/5/534/486974/Germ-line-DDX41-mutations-define-a-unique-subtype?guestAccessKey=)"
    )
    st.markdown(
        "[Reference 3: Prevalence and significance of DDX41 gene variants](https://ashpublications.org/blood/article/142/14/1185/497190/Prevalence-and-significance-of-DDX41-gene-variants?guestAccessKey=)"
    )
    
    st.markdown("")  # spacing after images and references

# --- RUNX1 Image ---
if "RUNX1" in input_genes:
    st.markdown("##### RUNX1:")
    st.image("RUNX1_image.png", use_container_width=True)
    # Add clickable reference below image
    st.markdown(
        "[Reference: RUNX1-mutated families phenotype](https://ashpublications.org/bloodadvances/article/4/6/1131/452758/RUNX1-mutated-families-show-phenotype)",
        unsafe_allow_html=True
    )
    st.markdown("")  # spacing after image and reference

    # --- BCL2 Image ---
    if "BCL2" in input_genes:
        st.markdown("##### BCL2:")
        st.image("BCL2_venetoclax.png", use_container_width=True)
        st.markdown("")  # spacing after image

  # --- CALR Image ---
if "CALR" in input_genes:
    st.markdown("#### CALR:")  # using #### to match other images
    st.image("CALR_image.jpg", use_container_width=True)
    # Reference below image
    st.markdown(
        "[Reference: CALR study](https://doi.org/10.1002/ajh.25065)"
    )
    st.markdown("")  # spacing after image and reference
