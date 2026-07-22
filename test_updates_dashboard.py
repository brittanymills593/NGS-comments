import streamlit as st
import pandas as pd
import os
from difflib import SequenceMatcher


def run_new_dashboard():

    st.set_page_config(layout="wide")

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1050px;   /* adjust this value */
            padding-left: 3rem;
            padding-right: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Path to your Excel file
    EXCEL_FILE = "NGS_comments_automation.xlsx"

    # List of disease sheet names (must match the sheet names in the Excel file)
    DISEASE_SHEETS = [
        "AML",
        "ALL",
        "MDS",
        "MPN",
        "MPN limited",
        "B lymphoid",
        "T lymphoid",
        "CLL",
        "Myeloma",
        "Histiocytic disorders"
    ]

    # Automatically selected panel for each disease
    DISEASE_TO_PANEL = {
        "AML": "Myeloid panelv1.0",
        "MDS": "Myeloid panelv1.0",
        "MPN": "Myeloid panelv1.0",
        "MPN limited": "MPNlimitedv3.0",
        "B lymphoid": "ChronicBlymphoidv4.0",
        "T lymphoid": "chronicTlymphoidv4.0",
        "CLL": "CLLv3.0",
        "Myeloma": "Myelomav4.0",
        "ALL": "ALLv4.0",
        "Histiocytic disorders": "Histiocytosisv4.0"
    }

    # Streamlit app header with padding, no border/shadow
    col1, col2 = st.columns([3.5, 1.5])

    with col1:
        st.markdown(
            """
            <div style="
                background-color: white;   /* white background */
                padding: 10px 20px;         /* add padding around text */
                display: inline-block;      /* shrink box to text width */
            ">
                <h1 style='color:#2E004F; margin: 0; font-size: 2em;'>Haem NGS Comments</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.image("Logo.jpg", width=250)

    with st.sidebar:
        st.markdown("## 🧬 Report structure")
        st.write(
            """
            - Pathogenic/likely pathogenic variants >5% VAF
            - Low level (<5% VAF) pathogenic/likely pathogenic variants
            - Interpretation of variants >5% VAF only and TP53 + JAK2 at any level
            """
        )

    # AML reminder popup
    @st.dialog("AML sample reminder")
    def aml_reminder_popup():
        st.write(
            """
            Remember to manually check **UBTF** for partial tandem duplication.
            Instructions on iPassport:

            GEN-SOP 850: NGS analysis and Webserver Instructions (Version 2.0)

            Coordinates (GRCh38):
            **chr17:44,210,790-44,210,949**
            """
        )

        if st.button("Close"):
            st.session_state.aml_popup_closed = True
            st.rerun()
                   
    # -----------------------------------------
    # Reusable Caveat and CNV functions
    # -----------------------------------------

    def load_caveat_options():
        """
        Load caveat terms from the Caveats Excel sheet.
        Returns a sorted list of caveat options.
        """

        caveat_df = pd.read_excel(
            EXCEL_FILE,
            sheet_name="Caveats",
            usecols="A:B"
        )

        caveat_df.columns = [
            "Caveat",
            "Comment"
        ]

        # Ensure Caveat and Comment are always strings
        caveat_df["Caveat"] = (
            caveat_df["Caveat"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        caveat_df["Comment"] = (
            caveat_df["Comment"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        caveat_options = (
            [""]
            + sorted(
                caveat_df["Caveat"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        return caveat_df, caveat_options


    def display_caveat_box(key):
        """
        Display a Caveats dropdown and the corresponding
        comment from the Caveats Excel sheet.
        """

        try:

            caveat_df, caveat_options = load_caveat_options()

            selected_caveat = st.selectbox(
                "Caveats",
                caveat_options,
                key=key
            )

            if selected_caveat:

                caveat_result = caveat_df[
                    caveat_df["Caveat"]
                    == selected_caveat
                ]

                if not caveat_result.empty:

                    caveat_comment = caveat_result.iloc[0]["Comment"]

                    # Handle blank Excel cells
                    if pd.isna(caveat_comment):
                        caveat_comment = ""
                    else:
                        caveat_comment = str(caveat_comment)

                    # Handle [list genes] placeholder
                    if "[list genes]" in caveat_comment:

                        caveat_gene_input = st.text_input(
                            "Enter gene list for caveat "
                            "(comma separated):",
                            placeholder="e.g. KMT2A, ASXL1",
                            key=f"{key}_gene_input"
                        )

                        if caveat_gene_input:
                            caveat_comment = caveat_comment.replace(
                                "[list genes]",
                                caveat_gene_input
                            )

                    st.write(caveat_comment)

        except Exception as e:

            st.error(
                f"Error loading Caveats data: {e}"
            )


    def display_standardised_cnv_box(selected_disease, key):
        """
        Display a Standardised CNV dropdown using the CNV Excel sheet.
        CNV options are filtered based on the selected disease.
        """

        try:

            cnv_df = pd.read_excel(
                EXCEL_FILE,
                sheet_name="CNV",
                usecols="A:C"
            )

            cnv_df.columns = [
                "Disease",
                "Region",
                "Comment"
            ]

            # Ensure columns are always strings
            cnv_df["Disease"] = (
                cnv_df["Disease"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            cnv_df["Region"] = (
                cnv_df["Region"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            cnv_df["Comment"] = (
                cnv_df["Comment"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            # Filter CNV options based on selected disease
            cnv_for_disease = cnv_df[
                cnv_df["Disease"]
                == selected_disease
            ]

            standardised_cnv_options = (
                [""]
                + sorted(
                    cnv_for_disease["Region"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

            selected_standardised_cnv = st.selectbox(
                "Standardised CNV",
                standardised_cnv_options,
                key=key
            )

            # Display comment for selected CNV
            if selected_standardised_cnv:

                cnv_result = cnv_for_disease[
                    cnv_for_disease["Region"]
                    == selected_standardised_cnv
                ]

                if not cnv_result.empty:

                    cnv_comment = cnv_result.iloc[0]["Comment"]

                    if pd.isna(cnv_comment):
                        cnv_comment = ""
                    else:
                        cnv_comment = str(cnv_comment)

                    st.write(cnv_comment)

        except Exception as e:

            st.error(
                f"Error loading Standardised CNV data: {e}"
            )

  
    # --- Gene Comments Section ---
    selected_disease = st.selectbox("Select Disease Type", DISEASE_SHEETS)

    # Reset popup when disease changes
    if "previous_disease" not in st.session_state:
        st.session_state.previous_disease = selected_disease
        st.session_state.aml_popup_closed = False

    if selected_disease != st.session_state.previous_disease:
        st.session_state.previous_disease = selected_disease
        st.session_state.aml_popup_closed = False

    # Show AML reminder when AML is selected
    if selected_disease == "AML" and not st.session_state.aml_popup_closed:
        aml_reminder_popup()

    gene_input = st.text_input(
        "Enter one or more gene symbols (comma-separated, e.g. TP53, NRAS, FLT3):"
    )

    # -----------------------------
    # Clear confidence gene inputs when disease or genes change
    # -----------------------------

    if "previous_selected_disease" not in st.session_state:
        st.session_state.previous_selected_disease = selected_disease

    if "previous_gene_input" not in st.session_state:
        st.session_state.previous_gene_input = gene_input

    # Detect changes
    if (
        selected_disease != st.session_state.previous_selected_disease
        or gene_input != st.session_state.previous_gene_input
    ):
        st.session_state.medium_gene_input = ""
        st.session_state.low_gene_input = ""

        st.session_state.previous_selected_disease = selected_disease
        st.session_state.previous_gene_input = gene_input


    # -----------------------------------------
    # Medium and low confidence input boxes
    # -----------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        medium_gene_input = st.text_input(
            "Medium confidence genes",
            placeholder="e.g. ASXL1, DNMT3A",
            key="medium_gene_input"
        )

    with col2:
        low_gene_input = st.text_input(
            "Low confidence genes",
            placeholder="e.g. TP53",
            key="low_gene_input"
        )


    # -----------------------------------------
    # Disease-specific additional input boxes
    # -----------------------------------------

    # =========================================
    # AML
    # =========================================
    if selected_disease == "AML":

        # Focal CNV / SV detected
        col1, col2 = st.columns(2)

        with col1:
            focal_cnv_input = st.text_input(
                "Focal CNV",
                placeholder="Enter focal CNV",
                key="aml_focal_cnv"
            )

        with col2:
            sv_detected_input = st.text_input(
                "SV detected",
                placeholder="Enter SV detected",
                key="aml_sv_detected"
            )


        # Fusions / Germline significance
        col1, col2 = st.columns(2)

        with col1:
            fusion_rt_pcr_input = st.text_input(
                "Fusions detected by RT-PCR",
                placeholder="Enter fusions detected by RT-PCR",
                key="aml_fusions_rt_pcr"
            )

        with col2:
            germline_significance_input = st.text_input(
                "Gene with potential germline significance",
                placeholder="Enter gene",
                key="aml_germline_significance"
            )


        # Caveats
        display_caveat_box(
            key="aml_caveat"
        )


    # =========================================
    # MDS / ALL
    # =========================================
    elif selected_disease in [
        "MDS",
        "ALL"
    ]:

        # Focal CNV / SV detected
        col1, col2 = st.columns(2)

        with col1:
            focal_cnv_input = st.text_input(
                "Focal CNV",
                placeholder="Enter focal CNV",
                key="mds_all_focal_cnv"
            )

        with col2:
            sv_detected_input = st.text_input(
                "SV detected",
                placeholder="Enter SV detected",
                key="mds_all_sv_detected"
            )


        # Caveats
        display_caveat_box(
            key="mds_all_caveat"
        )


    # =========================================
    # B lymphoid / T lymphoid / CLL
    # =========================================
    elif selected_disease in [
        "B lymphoid",
        "T lymphoid",
        "CLL"
    ]:

        # Focal CNV / Standardised CNV
        col1, col2 = st.columns(2)

        with col1:
            focal_cnv_input = st.text_input(
                "Focal CNV",
                placeholder="Enter focal CNV",
                key="b_t_cll_focal_cnv"
            )

        with col2:
            display_standardised_cnv_box(
                selected_disease=selected_disease,
                key="b_t_cll_standardised_cnv"
            )


        # Caveats
        display_caveat_box(
            key="b_t_cll_caveat"
        )

    # Convert inputs to lists
    input_genes = [
        gene.strip().upper()
        for gene in gene_input.split(",")
        if gene.strip()
    ]

    # Preserve the formatting entered by the user
    medium_genes = [
        gene.strip()
        for gene in medium_gene_input.split(",")
        if gene.strip()
    ]

    low_genes = [
        gene.strip()
        for gene in low_gene_input.split(",")
        if gene.strip()
    ]

    # Uppercase versions for matching only
    medium_genes_upper = [
        gene.upper()
        for gene in medium_genes
    ]

    low_genes_upper = [
        gene.upper()
        for gene in low_genes
    ]

    # Continue only if genes have been entered
    if selected_disease and input_genes:
        try:
           
            # -----------------------------
            # Load gene comments
            # -----------------------------
            df = pd.read_excel(
                EXCEL_FILE,
                sheet_name=selected_disease,
                usecols="A:B"
            )

            df.columns = ["Gene", "Relevant_comments"]

            # Ensure Gene and Relevant_comments are always strings
            df["Gene"] = (
                df["Gene"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df["Relevant_comments"] = (
                df["Relevant_comments"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            try:
                mode_df = pd.read_excel(
                    EXCEL_FILE,
                    sheet_name=selected_disease,
                    usecols="C"
                )
                df["Mode"] = mode_df.iloc[:, 0]
            except:
                df["Mode"] = ""

            # Preserve order entered by user
            filtered_rows = []
            genes_without_comments = []

            for gene in input_genes:

                matches = df[
                    df["Gene"].str.upper() == gene
                ]

                if not matches.empty:

                    # Check whether the gene has a comment
                    comment_values = (
                        matches["Relevant_comments"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    if comment_values.eq("").all():

                        genes_without_comments.append(gene)

                    else:

                        # Only add genes with comments
                        filtered_rows.append(matches)

            # Display genes that have no comments
            for gene in genes_without_comments:
                st.write(
                    f"No comment found for '{gene}'."
                )

            # Continue only if genes with comments were found
            if filtered_rows:

                filtered_df = pd.concat(
                    filtered_rows,
                    ignore_index=True
                )

                # Your existing comment grouping code continues here                         
           
                # -----------------------------
                # Display gene comments
                # -----------------------------

                grouped_comments = []

                used_indices = set()

                for i, row in filtered_df.iterrows():

                    if i in used_indices:
                        continue

                    gene = str(row["Gene"])
                    comment = str(row["Relevant_comments"])

                    matching_genes = [gene]

                    for j, row2 in filtered_df.iterrows():

                        if j <= i or j in used_indices:
                            continue

                        gene2 = str(row2["Gene"])
                        comment2 = str(row2["Relevant_comments"])

                        # Remove gene names for comparison
                        clean_comment = (
                            comment
                            .replace(gene, "")
                            .lower()
                        )

                        clean_comment2 = (
                            comment2
                            .replace(gene2, "")
                            .lower()
                        )

                        similarity = SequenceMatcher(
                            None,
                            clean_comment,
                            clean_comment2
                        ).ratio()

                        # Group similar comments
                        if similarity > 0.92:
                            matching_genes.append(gene2)
                            used_indices.add(j)

                    used_indices.add(i)

                    if len(matching_genes) > 1:

                        # Use the first comment as the template
                        combined_comment = comment.replace(
                            gene,
                            " and ".join(matching_genes)
                        )

                        grouped_comments.append(combined_comment)

                    else:
                        grouped_comments.append(comment)

                # If all comments have grouped into one short comment
                if (
                    len(grouped_comments) == 1
                    and len(str(grouped_comments[0])) < 250
                ):

                    st.write(grouped_comments[0])

                else:

                    # Otherwise display table
                    st.success(
                        f"Found {len(filtered_df)} matching comment(s):"
                    )

                    show_mode = st.checkbox("Show Mode column")

                    def format_mode(val):
                        if not isinstance(val, str):
                            return val

                        v = val.lower()

                        is_ts = "tumour suppressor" in v
                        is_onc = "oncogene" in v

                        if is_ts and not is_onc:
                            return "🟢 Tumour suppressor"
                        elif is_onc and not is_ts:
                            return "🔴 Oncogene"
                        elif is_ts and is_onc:
                            return "🟢🔴 Oncogene / Tumour suppressor"
                        else:
                            return val

                    filtered_df["Mode"] = filtered_df["Mode"].apply(
                        format_mode
                    )

                    if show_mode:
                        display_df = filtered_df
                    else:
                        display_df = filtered_df.drop(
                            columns=["Mode"]
                        )

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
           
                # -----------------------------
                # Combined panel comment + caveats
                # -----------------------------
                output_text = []

                # Remaining panel genes
                panel_df = pd.read_excel(
                    EXCEL_FILE,
                    sheet_name="Panel"
                )

                auto_panel = DISEASE_TO_PANEL.get(
                    selected_disease
                )

                if auto_panel:

                    result = panel_df[
                        panel_df["Panel"] == auto_panel
                    ]

                    if not result.empty:

                        panel_genes = str(
                            result.iloc[0]["Genes"]
                        )

                        panel_gene_list = [
                            gene.strip()
                            for gene in panel_genes.split(",")
                        ]

                        # -----------------------------------------
                        # Remove all detected genes and low confidence genes
                        # -----------------------------------------

                        # Create a set containing all genes to remove
                        # This includes:
                        # 1. All genes entered in the main gene input
                        # 2. All low confidence genes
                        genes_to_remove = set(
                            input_genes + low_genes_upper
                        )

                        # Remove genes from the panel
                        # Matching is case-insensitive and ignores spaces
                        panel_gene_list = [
                            gene
                            for gene in panel_gene_list
                            if gene.strip().upper() not in genes_to_remove
                        ]

                        output_text.append(
                            ", ".join(panel_gene_list)
                        )

                # Load caveats
                caveat_df = pd.read_excel(
                    EXCEL_FILE,
                    sheet_name="Caveats",
                    usecols="A:B"
                )

                caveat_df.columns = [
                    "Caveat",
                    "Comment"
                ]

                # Ensure Caveat and Comment are always strings
                caveat_df["Caveat"] = (
                    caveat_df["Caveat"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

                caveat_df["Comment"] = (
                    caveat_df["Comment"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

                # Medium confidence
                if medium_genes:

                    result = caveat_df[
                        caveat_df["Caveat"].str.lower()
                        == "medium confidence"
                    ]

                    if not result.empty:

                        comment = result.iloc[0]["Comment"]

                        # Handle blank Excel cells
                        if pd.isna(comment):
                            comment = ""
                        else:
                            comment = str(comment)

                        if "[list genes]" in comment:
                            comment = comment.replace(
                                "[list genes]",
                                ", ".join(medium_genes)
                            )

                        output_text.append(comment)

                # Low confidence
                if low_genes:

                    result = caveat_df[
                        caveat_df["Caveat"].str.lower()
                        == "low confidence"
                    ]

                    if not result.empty:

                        comment = result.iloc[0]["Comment"]

                        # Handle blank Excel cells
                        if pd.isna(comment):
                            comment = ""
                        else:
                            comment = str(comment)

                        if "[list genes]" in comment:
                            comment = comment.replace(
                                "[list genes]",
                                ", ".join(low_genes)
                            )

                        output_text.append(comment)

                # Display everything as normal text
                if output_text:
                    st.write(
                        "\n\n".join(output_text)
                    )

        except Exception as e:
            st.error(
                f"Error loading gene comments: {e}"
            )





  

               
    # --- Panel Lookup Section ---
    st.markdown("---")
    st.markdown("### Panel Lookup")

    try:

        panel_df = pd.read_excel(
            EXCEL_FILE,
            sheet_name="Panel"
        )

        if (
            "Panel" in panel_df.columns
            and "Genes" in panel_df.columns
        ):

            panel_names = (
                panel_df["Panel"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_panel = st.selectbox(
                "Select Panel Name:",
                [""] + panel_names
            )

            if selected_panel:

                result = panel_df[
                    panel_df["Panel"]
                    == selected_panel
                ]

                if not result.empty:

                    st.success(
                        "Panel genes found:"
                    )

                    st.write(
                        result.iloc[0]["Genes"]
                    )

                else:

                    st.warning(
                        "No matching panel found."
                    )

        else:

            st.error(
                "Expected columns 'Panel' "
                "and/or 'Genes' not found in the sheet."
            )

    except Exception as e:

        st.error(
            f"Error loading Panel data: {e}"
        )


    # --- Images Section (conditional on gene input) ---
    if input_genes:

        # Show header if at least one gene with images is selected
        if any(
            gene in [
                "DDX41",
                "RUNX1",
                "BCL2",
                "CALR"
            ]
            for gene in input_genes
        ):

            st.markdown("---")
            st.markdown(
                "### Figures from papers:"
            )
            st.markdown("")


    # --- DDX41 Images ---
    if "DDX41" in input_genes:

        st.markdown("#### DDX41:")

        st.image(
            "DDX41_1.png",
            use_container_width=True
        )

        st.image(
            "DDX41_2.png",
            use_container_width=True
        )

        st.image(
            "DDX41_3.png",
            use_container_width=True
        )

        st.markdown(
            "[Reference 1: The genetic landscape of germline DDX41 variants](https://ashpublications.org/blood/article/140/7/716/485483/The-genetic-landscape-of-germline-DDX41-variants?guestAccessKey=)"
        )

        st.markdown(
            "[Reference 2: Germ-line DDX41 mutations define a unique subtype](https://ashpublications.org/blood/article/141/5/534/486974/Germ-line-DDX41-mutations-define-a-unique-subtype?guestAccessKey=)"
        )

        st.markdown(
            "[Reference 3: Prevalence and significance of DDX41 gene variants](https://ashpublications.org/blood/article/142/14/1185/497190/Prevalence-and-significance-of-DDX41-gene-variants?guestAccessKey=)"
        )

        st.markdown("")


    # --- RUNX1 Image ---
    if "RUNX1" in input_genes:

        st.markdown("#### RUNX1:")

        st.image(
            "RUNX1_image.png",
            use_container_width=True
        )

        st.markdown(
            "[Reference: RUNX1-mutated families phenotype](https://ashpublications.org/bloodadvances/article/4/6/1131/452758/RUNX1-mutated-families-show-phenotype)"
        )

        st.markdown("")


    # --- BCL2 Image ---
    if "BCL2" in input_genes:

        st.markdown("#### BCL2:")

        st.image(
            "BCL2_venetoclax.png",
            use_container_width=True
        )

        st.markdown("")


    # --- CALR Image ---
    if "CALR" in input_genes:

        st.markdown("#### CALR:")

        st.image(
            "CALR_image.jpg",
            use_container_width=True
        )

        st.markdown(
            "[Reference: CALR study](https://doi.org/10.1002/ajh.25065)"
        )

        st.markdown("")


    # --- Bottom Image ---
    st.markdown("---")
    st.markdown(
        "### Build 38 variant position changes"
    )

    st.image(
        "Variant_new_positions.png",
        use_container_width=True
    )
