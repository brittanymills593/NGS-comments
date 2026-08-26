import streamlit as st
import pandas as pd
import dashboard_functions as df


def run_test_dashboard():

    st.set_page_config(layout="wide")

    # =========================================================
    # SETTINGS
    # =========================================================

    EXCEL_FILE = "NGS_comments_automation.xlsx"

    DISEASE_SHEETS = [
        "AML",
        "MDS",
        "MPN",
        "MPN limited",
        "CMML",
        "JMML",
        "Myeloid generic",
        "MDS unconfirmed",
        "MPN unconfirmed",
        "B lymphoid",
        "T lymphoid",
        "CLL",
        "Myeloma",
        "Histiocytic disorders",
        "Systemic mastocytosis",
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
    # DISEASE SELECTION
    # =========================================================

    selected_disease = st.selectbox(
        "Select Disease Type",
        DISEASE_SHEETS
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
    # CLL INFILTRATION / CNV
    # =========================================================

    cll_comment = ""

    if selected_disease == "CLL":

        try:

            cll_cnv_df = pd.read_excel(
                EXCEL_FILE,
                sheet_name="CLL CNV",
                usecols="A:C"
            )

            cll_cnv_df.columns = [
                "Infiltration",
                "CNV",
                "Comment"
            ]

            cll_cnv_df["Infiltration"] = (
                cll_cnv_df["Infiltration"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            cll_cnv_df["CNV"] = (
                cll_cnv_df["CNV"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            cll_cnv_df["Comment"] = (
                cll_cnv_df["Comment"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            infiltration_options = [
                value
                for value in cll_cnv_df[
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
                    key="cll_infiltration"
                )

            # -------------------------------------------------
            # CNVs
            # -------------------------------------------------

            with col2:

                if infiltration:

                    matching_cnv_df = cll_cnv_df[
                        cll_cnv_df["Infiltration"]
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
                        key="cll_cnvs"
                    )

                    # -------------------------------------------------
                    # Retrieve comments for all selected CNVs
                    # -------------------------------------------------

                    if selected_cnvs:

                        selected_cnv_rows = matching_cnv_df[
                            matching_cnv_df["CNV"].isin(
                                selected_cnvs
                            )
                        ]

                        comments = [
                            comment
                            for comment in selected_cnv_rows[
                                "Comment"
                            ]
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
                        key="cll_cnvs_disabled"
                    )

        except Exception as e:

            st.error(
                f"Error loading CLL CNV information: {e}"
            )

    # =========================================================
    # GERMLINE LOOKUP
    # =========================================================
    
    MYELOID_DISEASES = [
        "AML",
        "MDS",
        "MPN",
        "MPN limited",
        "CMML",
        "JMML",
        "Myeloid generic",
        "MDS unconfirmed",
        "MPN unconfirmed",
        "Systemic mastocytosis",
    ]

    if selected_disease in MYELOID_DISEASES:

        st.markdown(
            "### Germline lookup"
        )

        df.germline_lookup(
            EXCEL_FILE
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

    if selected_disease and input_genes:

        try:

            # -------------------------------------------------
            # Load gene comments
            # -------------------------------------------------

            gene_df = df.load_gene_comments(
                selected_disease
            )

            # -------------------------------------------------
            # Find matching comments
            # -------------------------------------------------

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
            # Gene comments
            # -------------------------------------------------

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

                df.display_gene_comments(
                    filtered_df,
                    grouped_comments
                )

            # =================================================
            # FINAL REPORT TEXT
            # =================================================

            output_text = []

            # -------------------------------------------------
            # Panel genes
            # -------------------------------------------------

            panel_genes = df.get_remaining_panel_genes(
                selected_disease,
                input_genes,
                low_genes_upper
            )

            if panel_genes:

                # Your Panel sheet contains the full
                # standard introductory wording.
                #
                # The function returns the remaining
                # gene list, so rebuild the standard text.

                panel_comment = (
                    "No pathogenic/likely pathogenic variants "
                    "were detected in the regions analysed "
                    "within the "
                    + panel_genes
                    + " genes."
                )

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
            #
            # Deliberately LAST
            # -------------------------------------------------

            if (
                selected_disease == "CLL"
                and cll_comment
            ):

                output_text.append(
                    cll_comment
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
