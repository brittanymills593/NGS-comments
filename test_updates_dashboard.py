import streamlit as st
import pandas as pd
import dashboard_functions as df


def run_test_dashboard():

    st.set_page_config(layout="wide")

    # =========================================================
    # SETTINGS
    # =========================================================

    EXCEL_FILE = "NGS_comments_automation_further_review.xlsx"

    MYELOID_DISEASES = [
        "AML",
        "MDS",
        "MPN",
        "MPN limited",
        "CMML",
        "JMML",
        "Myeloid generic",
        "MPN unconfirmed",
        "MDS unconfirmed",
        "Systemic mastocytosis",
        "Histiocytic disorders",
    ]
    
    LYMPHOID_DISEASES = [
        "B lymphoid",
        "T lymphoid",
        "B and T lymphoid",
        "CLL",
        "Myeloma",
    ]

    DISEASE_TO_PANEL = {
        "AML": "Myeloid panelv1.0",
        "MDS": "Myeloid panelv1.0",
        "MPN": "Myeloid panelv1.0",
        "MPN limited": "MPNlimitedv3.0",
        "CMML": "Myeloid panelv1.0",
        "JMML": "Myeloid panelv1.0",
        "B lymphoid": "ChronicBlymphoidv4.0",
        "T lymphoid": "chronicTlymphoidv4.0",
        "B and T lymphoid": "ChronicBandTlymphoidV2.0",
        "CLL": "CLLv3.0",
        "Myeloma": "Myelomav4.0",
        "ALL": "ALLv4.0",
        "Histiocytic disorders": "Histiocytosisv4.0",
        "Systemic mastocytosis": "Myeloid panelv1.0",
        "Myeloid generic": "Myeloid panelv1.0",
        "MDS unconfirmed": "Myeloid panelv1.0",
        "MPN unconfirmed": "Myeloid panelv1.0",
    }

    # ---------------------------------------------------------
    # Give dashboard_functions access to these variables
    # ---------------------------------------------------------

    df.EXCEL_FILE = EXCEL_FILE
    df.DISEASE_TO_PANEL = DISEASE_TO_PANEL

    # =========================================================
    # PAGE CSS
    # =========================================================

    st.markdown(
        """
        <style>

        .block-container {
            max-width: 1050px;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # HEADER
    # =========================================================

    col1, col2 = st.columns([3.5, 1.5])

    with col1:

        st.markdown(
            """
            <div style="
                background-color: white;
                padding: 10px 20px;
                display: inline-block;
            ">
                <h1 style='
                    color:#2E004F;
                    margin:0;
                    font-size:2em;
                '>
                    Haem NGS Comments
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.image(
            "Logo.jpg",
            width=250
        )

    # =========================================================
    # SIDEBAR
    # =========================================================

    with st.sidebar:

        st.markdown(
            "## 🧬 Report structure"
        )

        st.write(
            """
            - Pathogenic/likely pathogenic variants >5% VAF
            - Low level (<5% VAF) pathogenic/likely pathogenic variants
            - Interpretation of variants >5% VAF only and TP53 + JAK2 at any level
            """
        )

    # =========================================================
    # AML REMINDER
    # =========================================================

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

    # =========================================================
    # DISEASE GROUP SELECTION
    # =========================================================
    
    if "disease_group" not in st.session_state:
        st.session_state.disease_group = "Myeloid"
    
    col1, col2 = st.columns(2)
    
    with col1:
    
        myeloid_selected = st.checkbox(
            "Myeloid",
            value=st.session_state.disease_group == "Myeloid"
        )
    
    with col2:
    
        lymphoid_selected = st.checkbox(
            "Lymphoid",
            value=st.session_state.disease_group == "Lymphoid"
        )
    
    # ---------------------------------------------------------
    # Only allow one group to be selected
    # ---------------------------------------------------------
    
    if myeloid_selected and not lymphoid_selected:
    
        st.session_state.disease_group = "Myeloid"
    
    elif lymphoid_selected and not myeloid_selected:
    
        st.session_state.disease_group = "Lymphoid"
    
    elif myeloid_selected and lymphoid_selected:
    
        # Keep the previously selected group
        if st.session_state.disease_group == "Myeloid":
            lymphoid_selected = False
        else:
            myeloid_selected = False
    
    else:
    
        # Don't allow both boxes to be unchecked
        if st.session_state.disease_group == "Myeloid":
            myeloid_selected = True
        else:
            lymphoid_selected = True
    
    # =========================================================
    # DISEASE SELECTION
    # =========================================================
    
    if st.session_state.disease_group == "Myeloid":
    
        available_diseases = MYELOID_DISEASES
    
    else:
    
        available_diseases = LYMPHOID_DISEASES
    
    # Keep the currently selected disease if it is still
    # available in the selected disease group
    
    if (
        "previous_disease" in st.session_state
        and st.session_state.previous_disease in available_diseases
    ):
    
        disease_index = available_diseases.index(
            st.session_state.previous_disease
        )
    
    else:
    
        disease_index = 0
    
    selected_disease = st.selectbox(
        "Select Disease Type",
        available_diseases,
        index=disease_index
    )

    # =========================================================
    # SESSION STATE
    # =========================================================

    if "previous_disease" not in st.session_state:

        st.session_state.previous_disease = selected_disease

    if "previous_selected_disease" not in st.session_state:

        st.session_state.previous_selected_disease = selected_disease

    if "previous_gene_input" not in st.session_state:

        st.session_state.previous_gene_input = ""

    if "aml_popup_closed" not in st.session_state:

        st.session_state.aml_popup_closed = False

    if "cll_infiltration" not in st.session_state:

        st.session_state.cll_infiltration = None

    if "germline_panel_open" not in st.session_state:

        st.session_state.germline_panel_open = False

    # =========================================================
    # RESET WHEN DISEASE CHANGES
    # =========================================================

    if selected_disease != st.session_state.previous_disease:

        st.session_state.previous_disease = selected_disease

        st.session_state.aml_popup_closed = False

        st.session_state.cll_infiltration = None

        st.session_state.germline_panel_open = False

        # Reset confidence inputs

        st.session_state.medium_gene_input = ""

        st.session_state.low_gene_input = ""

        # Reset CLL CNV widget

        if "cll_cnvs" in st.session_state:

            del st.session_state.cll_cnvs

    # =========================================================
    # AML REMINDER
    # =========================================================

    if (
        selected_disease == "AML"
        and not st.session_state.aml_popup_closed
    ):

        aml_reminder_popup()

    # =========================================================
    # GENE INPUT
    # =========================================================

    gene_input = st.text_input(
        "Enter one or more gene symbols "
        "(comma-separated, e.g. TP53, NRAS, FLT3):"
    )

    # =========================================================
    # RESET CONFIDENCE INPUTS WHEN GENES CHANGE
    # =========================================================

    if gene_input != st.session_state.previous_gene_input:

        st.session_state.medium_gene_input = ""

        st.session_state.low_gene_input = ""

        st.session_state.previous_gene_input = gene_input

    # =========================================================
    # MEDIUM / LOW CONFIDENCE
    # =========================================================

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


    # =========================================================
    # LYMPHOID INFILTRATION / CNV
    # =========================================================
    
    cll_comment = ""
    
    LYMPHOID_CNV_DISEASES = [
        "CLL",
        "B lymphoid",
        "T lymphoid",
        "B and T lymphoid",
    ]
    
    if selected_disease in LYMPHOID_CNV_DISEASES:
    
        try:
    
            # -------------------------------------------------
            # Select the appropriate CNV sheet
            # -------------------------------------------------
    
            if selected_disease == "CLL":
    
                cnv_sheet = "CLL CNV"
    
            else:
    
                cnv_sheet = "CNV lymphoid"
    
            # -------------------------------------------------
            # Load CNV information
            # -------------------------------------------------
    
            lymphoid_cnv_df = pd.read_excel(
                EXCEL_FILE,
                sheet_name=cnv_sheet,
                usecols="A:C"
            )
    
            lymphoid_cnv_df.columns = [
                "Infiltration",
                "CNV",
                "Comment"
            ]
    
            # -------------------------------------------------
            # Clean text
            # -------------------------------------------------
    
            for column in [
                "Infiltration",
                "CNV",
                "Comment"
            ]:
    
                lymphoid_cnv_df[column] = (
                    lymphoid_cnv_df[column]
                    .fillna("")
                    .astype(str)
                    .str.replace("\u00a0", " ", regex=False)
                    .str.replace(r"\s+", " ", regex=True)
                    .str.strip()
                )
    
            # -------------------------------------------------
            # Infiltration options
            # -------------------------------------------------
    
            infiltration_options = [
                value
                for value in lymphoid_cnv_df[
                    "Infiltration"
                ].unique()
                if value
            ]
    
            col1, col2 = st.columns(2)
    
            # -------------------------------------------------
            # Infiltration
            # -------------------------------------------------
    
            with col1:
    
                infiltration = st.selectbox(
                    "Infiltration (immunophenotyping)",
                    options=infiltration_options,
                    index=None,
                    placeholder="Select infiltration",
                    key=f"{selected_disease}_infiltration"
                )
    
            # -------------------------------------------------
            # CNVs
            # -------------------------------------------------
    
            with col2:
    
                if infiltration:
    
                    matching_cnv_df = lymphoid_cnv_df[
                        lymphoid_cnv_df["Infiltration"]
                        == infiltration
                    ]
    
                    cnv_options = [
                        value
                        for value in matching_cnv_df[
                            "CNV"
                        ].unique()
                        if value
                    ]
    
                    selected_cnvs = st.multiselect(
                        "CNV(s) present",
                        options=cnv_options,
                        placeholder="Select one or more CNVs",
                        key=f"{selected_disease}_cnvs"
                    )
    
                    # -------------------------------------------------
                    # Retrieve comments for all selected CNVs
                    # -------------------------------------------------
    
                    if selected_cnvs:
    
                        # Normalise the selected values too
                        selected_cnvs_clean = [
                            str(cnv)
                            .replace("\u00a0", " ")
                            .strip()
                            for cnv in selected_cnvs
                        ]
    
                        selected_cnv_rows = matching_cnv_df[
                            matching_cnv_df["CNV"].isin(
                                selected_cnvs_clean
                            )
                        ]
    
                        comments = (
                            selected_cnv_rows["Comment"]
                            .dropna()
                            .astype(str)
                            .str.strip()
                        )
    
                        comments = [
                            comment
                            for comment in comments
                            if comment
                        ]
    
                        cll_comment = "\n\n".join(
                            comments
                        )
    
                else:
    
                    st.multiselect(
                        "CNV(s) present",
                        options=[],
                        placeholder="Select infiltration first",
                        disabled=True,
                        key=f"{selected_disease}_cnvs_disabled"
                    )
    
        except Exception as e:
    
            st.error(
                f"Error loading lymphoid CNV information: {e}"
            )


    # =========================================================
    # MYELOID LOOKUPS
    # =========================================================
        
    caveat_comment = ""
    
    if selected_disease in MYELOID_DISEASES:
    
        col1, col2 = st.columns(2)
    
        # -----------------------------------------------------
        # Germline lookup
        # -----------------------------------------------------
    
        with col1:
    
            df.germline_lookup(
                EXCEL_FILE
            )
    
        # -----------------------------------------------------
        # Caveat selection
        # -----------------------------------------------------
    
        with col2:
    
            caveat_comment = df.display_caveat_box(
                key="myeloid_caveat"
            )

    # =========================================================
    # CONVERT GENE INPUTS
    # =========================================================

    input_genes = df.parse_comma_separated_input(
        gene_input,
        uppercase=True
    )

    medium_genes = df.parse_comma_separated_input(
        medium_gene_input
    )

    low_genes = df.parse_comma_separated_input(
        low_gene_input
    )

    low_genes_upper = df.parse_comma_separated_input(
        low_gene_input,
        uppercase=True
    )

# =========================================================
# GENE COMMENTS
# =========================================================

    if selected_disease:
    
        try:
    
            # -------------------------------------------------
            # Load gene comments
            # -------------------------------------------------
    
            gene_df = df.load_gene_comments(
                selected_disease
            )
    
            # -------------------------------------------------
            # Find matching gene comments
            # -------------------------------------------------
    
            filtered_rows = []
            genes_without_comments = []
    
            if input_genes:
    
                filtered_rows, genes_without_comments = (
                    df.filter_gene_comments(
                        gene_df,
                        input_genes
                    )
                )
    
                # -------------------------------------------------
                # Display genes without comments
                # -------------------------------------------------
    
                for gene in genes_without_comments:
    
                    st.write(
                        f"No comment found for '{gene}'."
                    )
    
            # -------------------------------------------------
            # Process gene comments
            # -------------------------------------------------
    
            filtered_df = None
            grouped_comments = None
    
            if filtered_rows:
    
                filtered_df = pd.concat(
                    filtered_rows,
                    ignore_index=True
                )
    
                grouped_comments = (
                    df.group_similar_comments(
                        filtered_df
                    )
                )
    
                # -------------------------------------------------
                # For all diseases EXCEPT Myeloma:
                # keep the existing display behaviour
                # -------------------------------------------------
    
                if selected_disease != "Myeloma":
    
                    df.display_gene_comments(
                        filtered_df,
                        grouped_comments
                    )
    
            # =================================================
            # FINAL REPORT TEXT
            # =================================================
    
            output_text = []
    
            # -------------------------------------------------
            # Myeloma-specific panel introduction
            # -------------------------------------------------
    
            if selected_disease == "Myeloma":
    
                output_text.append(
                    "Analysis on CD138+ cells:"
                )
    
                # -------------------------------------------------
                # Myeloma gene comments
                # These go between the introduction and
                # the negative panel
                # -------------------------------------------------
    
                if filtered_df is not None and not filtered_df.empty:
    
                    myeloma_comments = (
                        filtered_df["Relevant_comments"]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .drop_duplicates()
                        .tolist()
                    )
    
                    output_text.extend(
                        myeloma_comments
                    )
    
            # -------------------------------------------------
            # Panel negative comment
            # -------------------------------------------------
    
            panel_comment = df.get_remaining_panel_genes(
                selected_disease,
                input_genes,
                low_genes_upper
            )
    
            if panel_comment:
    
                output_text.append(
                    panel_comment
                )
    
            # -------------------------------------------------
            # Medium / Low confidence caveats
            # -------------------------------------------------
    
            confidence_comments = (
                df.get_confidence_caveats(
                    medium_genes,
                    low_genes
                )
            )
    
            output_text.extend(
                confidence_comments
            )
    
            # -------------------------------------------------
            # CLL CNV comment
            # Deliberately LAST
            # -------------------------------------------------
    
            if (
                selected_disease == "CLL"
                and cll_comment
            ):
    
                output_text.append(
                    cll_comment
                )
    
            # ---------------------------------------------------------
            # Myeloid caveat
            # This is deliberately LAST
            # ---------------------------------------------------------
    
            if caveat_comment:
    
                output_text.append(
                    caveat_comment
                )
    
            # -------------------------------------------------
            # Display final text
            # -------------------------------------------------
    
            if output_text:
    
                st.write(
                    "\n\n".join(
                        output_text
                    )
                )
    
        except Exception as e:
    
            st.error(
                f"Error loading gene comments: {e}"
            )
