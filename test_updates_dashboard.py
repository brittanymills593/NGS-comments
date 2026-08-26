import streamlit as st
import pandas as pd
from difflib import SequenceMatcher


def run_test_dashboard():

    st.set_page_config(layout="wide")

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
    # SETTINGS
    # =========================================================

    EXCEL_FILE = "NGS_comments_automation_further_review.xlsx"

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
        "MPN unconfirmed": "Myeloid panelv1.0"
    }

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
                <h1 style='color:#2E004F; margin: 0; font-size: 2em;'>
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

        st.markdown("## 🧬 Report structure")

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
    # DISEASE CHANGE HANDLING
    # =========================================================

    if "previous_disease" not in st.session_state:

        st.session_state.previous_disease = selected_disease

        st.session_state.aml_popup_closed = False

    if selected_disease != st.session_state.previous_disease:

        st.session_state.previous_disease = selected_disease

        st.session_state.aml_popup_closed = False

    # =========================================================
    # AML POPUP
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
        "Enter one or more gene symbols (comma-separated, e.g. TP53, NRAS, FLT3):"
    )

    # =========================================================
    # CLEAR CONFIDENCE INPUTS WHEN DISEASE OR GENES CHANGE
    # =========================================================

    if "previous_selected_disease" not in st.session_state:

        st.session_state.previous_selected_disease = selected_disease

    if "previous_gene_input" not in st.session_state:

        st.session_state.previous_gene_input = gene_input

    if (
        selected_disease
        != st.session_state.previous_selected_disease
        or gene_input
        != st.session_state.previous_gene_input
    ):

        st.session_state.medium_gene_input = ""

        st.session_state.low_gene_input = ""

        st.session_state.previous_selected_disease = selected_disease

        st.session_state.previous_gene_input = gene_input

    # =========================================================
    # MEDIUM / LOW CONFIDENCE BOXES
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

            # -------------------------------------------------
            # Load CLL CNV sheet
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Clean columns
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Get infiltration options
            # -------------------------------------------------

            infiltration_options = [
                value
                for value in cll_cnv_df["Infiltration"].unique()
                if value
            ]

            # -------------------------------------------------
            # Two CLL boxes
            # -------------------------------------------------

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
            # CNV
            # -------------------------------------------------

            with col2:

                if infiltration:

                    matching_cnv_df = cll_cnv_df[
                        cll_cnv_df["Infiltration"]
                        == infiltration
                    ]

                    cnv_options = [
                        value
                        for value in matching_cnv_df["CNV"].unique()
                        if value
                    ]

                    cnv = st.selectbox(
                        "CNV(s) present",
                        options=cnv_options,
                        index=None,
                        placeholder="Select CNV(s)",
                        key=f"cll_cnv_{infiltration}"
                    )

                    # -------------------------------------------------
                    # Get corresponding comment
                    # -------------------------------------------------

                    if cnv:

                        matching_comment = matching_cnv_df[
                            matching_cnv_df["CNV"] == cnv
                        ]

                        if not matching_comment.empty:

                            cll_comment = str(
                                matching_comment.iloc[0]["Comment"]
                            ).strip()

                else:

                    st.selectbox(
                        "CNV(s) present",
                        options=[],
                        index=None,
                        placeholder="Select infiltration first",
                        disabled=True,
                        key="cll_cnv_disabled"
                    )

        except Exception as e:

            st.error(
                f"Error loading CLL CNV information: {e}"
            )

    # =========================================================
    # CONVERT GENE INPUTS TO LISTS
    # =========================================================

    input_genes = [
        gene.strip().upper()
        for gene in gene_input.split(",")
        if gene.strip()
    ]

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

    # =========================================================
    # GENE COMMENTS
    # =========================================================

    if selected_disease and input_genes:

        try:

            # -------------------------------------------------
            # Load gene comments
            # -------------------------------------------------

            df = pd.read_excel(
                EXCEL_FILE,
                sheet_name=selected_disease,
                usecols="A:B"
            )

            df.columns = [
                "Gene",
                "Relevant_comments"
            ]

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

            # -------------------------------------------------
            # Load Mode
            # -------------------------------------------------

            try:

                mode_df = pd.read_excel(
                    EXCEL_FILE,
                    sheet_name=selected_disease,
                    usecols="C"
                )

                df["Mode"] = mode_df.iloc[:, 0]

            except:

                df["Mode"] = ""

            # -------------------------------------------------
            # Find matching genes
            # -------------------------------------------------

            filtered_rows = []

            genes_without_comments = []

            for gene in input_genes:

                matches = df[
                    df["Gene"].str.upper() == gene
                ]

                if not matches.empty:

                    comment_values = (
                        matches["Relevant_comments"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    if comment_values.eq("").all():

                        genes_without_comments.append(
                            gene
                        )

                    else:

                        filtered_rows.append(
                            matches
                        )

            # -------------------------------------------------
            # Display genes without comments
            # -------------------------------------------------

            for gene in genes_without_comments:

                st.write(
                    f"No comment found for '{gene}'."
                )

            # -------------------------------------------------
            # Display matching gene comments
            # -------------------------------------------------

            if filtered_rows:

                filtered_df = pd.concat(
                    filtered_rows,
                    ignore_index=True
                )

                grouped_comments = []

                used_indices = set()

                for i, row in filtered_df.iterrows():

                    if i in used_indices:

                        continue

                    gene = str(
                        row["Gene"]
                    )

                    comment = str(
                        row["Relevant_comments"]
                    )

                    matching_genes = [
                        gene
                    ]

                    for j, row2 in filtered_df.iterrows():

                        if (
                            j <= i
                            or j in used_indices
                        ):

                            continue

                        gene2 = str(
                            row2["Gene"]
                        )

                        comment2 = str(
                            row2["Relevant_comments"]
                        )

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

                        if similarity > 0.92:

                            matching_genes.append(
                                gene2
                            )

                            used_indices.add(j)

                    used_indices.add(i)

                    if len(matching_genes) > 1:

                        combined_comment = (
                            comment.replace(
                                gene,
                                " and ".join(
                                    matching_genes
                                )
                            )
                        )

                        grouped_comments.append(
                            combined_comment
                        )

                    else:

                        grouped_comments.append(
                            comment
                        )

                # -------------------------------------------------
                # Display comments
                # -------------------------------------------------

                if (
                    len(grouped_comments) == 1
                    and len(
                        str(grouped_comments[0])
                    ) < 250
                ):

                    st.write(
                        grouped_comments[0]
                    )

                else:

                    st.success(
                        f"Found {len(filtered_df)} matching comment(s):"
                    )

                    show_mode = st.checkbox(
                        "Show Mode column"
                    )

                    def format_mode(val):

                        if not isinstance(
                            val,
                            str
                        ):

                            return val

                        v = val.lower()

                        is_ts = (
                            "tumour suppressor"
                            in v
                        )

                        is_onc = (
                            "oncogene"
                            in v
                        )

                        if is_ts and not is_onc:

                            return (
                                "🟢 Tumour suppressor"
                            )

                        elif is_onc and not is_ts:

                            return (
                                "🔴 Oncogene"
                            )

                        elif is_ts and is_onc:

                            return (
                                "🟢🔴 Oncogene / "
                                "Tumour suppressor"
                            )

                        else:

                            return val

                    filtered_df["Mode"] = (
                        filtered_df["Mode"]
                        .apply(format_mode)
                    )

                    if show_mode:

                        display_df = filtered_df

                    else:

                        display_df = (
                            filtered_df.drop(
                                columns=["Mode"]
                            )
                        )

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )

        except Exception as e:

            st.error(
                f"Error loading gene comments: {e}"
            )

    # =========================================================
    # COMBINED PANEL COMMENT + CAVEATS
    #
    # This section is deliberately OUTSIDE the
    # "if input_genes" section so CLL comments can
    # appear even when no gene has been entered.
    # =========================================================

    try:

        output_text = []

        # =====================================================
        # PANEL COMMENT
        # =====================================================

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

                panel_text = str(
                    result.iloc[0]["Genes"]
                )

                marker = (
                    "No pathogenic/likely pathogenic variants "
                    "were detected in the regions analysed "
                    "within the "
                )

                if marker in panel_text:

                    intro, remainder = (
                        panel_text.split(
                            marker,
                            1
                        )
                    )

                    if " genes." in remainder:

                        gene_string, ending = (
                            remainder.split(
                                " genes.",
                                1
                            )
                        )

                        panel_gene_list = [
                            gene.strip()
                            for gene
                            in gene_string.split(",")
                        ]

                        genes_to_remove = {
                            gene.strip().upper()
                            for gene in (
                                input_genes
                                + low_genes_upper
                            )
                        }

                        panel_gene_list = [
                            gene
                            for gene
                            in panel_gene_list
                            if gene.upper()
                            not in genes_to_remove
                        ]

                        rebuilt_text = (
                            intro
                            + marker
                            + ", ".join(
                                panel_gene_list
                            )
                            + " genes."
                            + ending
                        )

                    else:

                        rebuilt_text = panel_text

                else:

                    rebuilt_text = panel_text

                # Only add panel text if it exists
                if rebuilt_text.strip():

                    output_text.append(
                        rebuilt_text
                    )

        # =====================================================
        # CAVEATS
        # =====================================================

        caveat_df = pd.read_excel(
            EXCEL_FILE,
            sheet_name="Caveats",
            usecols="A:B"
        )

        caveat_df.columns = [
            "Caveat",
            "Comment"
        ]

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

        # =====================================================
        # MEDIUM CONFIDENCE
        # =====================================================

        if medium_genes:

            result = caveat_df[
                caveat_df["Caveat"].str.lower()
                == "medium confidence"
            ]

            if not result.empty:

                comment = result.iloc[0]["Comment"]

                if pd.isna(comment):

                    comment = ""

                else:

                    comment = str(
                        comment
                    )

                if "[list genes]" in comment:

                    comment = comment.replace(
                        "[list genes]",
                        ", ".join(
                            medium_genes
                        )
                    )

                if comment.strip():

                    output_text.append(
                        comment
                    )

        # =====================================================
        # LOW CONFIDENCE
        # =====================================================

        if low_genes:

            result = caveat_df[
                caveat_df["Caveat"].str.lower()
                == "low confidence"
            ]

            if not result.empty:

                comment = result.iloc[0]["Comment"]

                if pd.isna(comment):

                    comment = ""

                else:

                    comment = str(
                        comment
                    )

                if "[list genes]" in comment:

                    comment = comment.replace(
                        "[list genes]",
                        ", ".join(
                            low_genes
                        )
                    )

                if comment.strip():

                    output_text.append(
                        comment
                    )

        # =====================================================
        # CLL COMMENT
        #
        # This is deliberately LAST.
        # =====================================================

        if (
            selected_disease == "CLL"
            and cll_comment
        ):

            output_text.append(
                cll_comment
            )

        # =====================================================
        # DISPLAY FINAL COMMENT
        # =====================================================

        if output_text:

            st.write(
                "\n\n".join(
                    output_text
                )
            )

    except Exception as e:

        st.error(
            f"Error creating combined comment: {e}"
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
