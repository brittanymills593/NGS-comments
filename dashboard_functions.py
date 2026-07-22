import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

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
    
        Returns the selected CNV comment for inclusion in the report.
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
                cnv_df["Disease"] == selected_disease
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
    
            # Return comment for selected CNV
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
                        cnv_comment = str(cnv_comment).strip()
    
                    return cnv_comment
    
            return ""
    
        except Exception as e:
    
            st.error(
                f"Error loading Standardised CNV data: {e}"
            )
    
            return ""
        

    def display_focal_cnv_box(key):
    
        focal_cnv_input = st.text_input(
            "Focal CNV",
            placeholder="e.g. loss of CDKN2A, gain of ATM",
            key=key
        )
    
        focal_cnv_output = ""
    
        if focal_cnv_input.strip():
    
            focal_cnv_list = [
                item.strip()
                for item in focal_cnv_input.split(",")
                if item.strip()
            ]
    
            if len(focal_cnv_list) == 1:
    
                focal_cnv_output = (
                    f"CNV analysis detected focal "
                    f"{focal_cnv_list[0]}."
                )
    
            elif len(focal_cnv_list) == 2:
    
                focal_cnv_output = (
                    "CNV analysis detected focal "
                    + " and ".join(focal_cnv_list)
                    + "."
                )
    
            else:
    
                focal_cnv_output = (
                    "CNV analysis detected focal "
                    + ", ".join(focal_cnv_list[:-1])
                    + " and "
                    + focal_cnv_list[-1]
                    + "."
                )
    
    
        return focal_cnv_output

    def display_sv_detected_box(key):
    
        sv_detected_input = st.text_input(
            "SV detected",
            placeholder="e.g. FLT3 ITD",
            key=key
        )
    
        sv_detected_output = ""
    
        if sv_detected_input.strip():
    
            sv_detected_output = (
                f"SV analysis detected "
                f"{sv_detected_input.strip()}."
            )
    
        return sv_detected_output

    
    def parse_comma_separated_input(text, uppercase=False):
        """
        Convert comma-separated text into a list.
    
        If uppercase=True, convert entries to uppercase.
        Otherwise, preserve the user's formatting.
        """
    
        if not text:
            return []
    
        values = [
            item.strip()
            for item in text.split(",")
            if item.strip()
        ]
    
        if uppercase:
            values = [
                item.upper()
                for item in values
            ]
    
        return values

    def load_gene_comments(disease):
        """
        Load gene comments and Mode information
        from the selected disease Excel sheet.
        """
    
        df = pd.read_excel(
            EXCEL_FILE,
            sheet_name=disease,
            usecols="A:B"
        )
    
        df.columns = [
            "Gene",
            "Relevant_comments"
        ]
    
        # Ensure Gene and comments are strings
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
    
        # Load Mode column
        try:
    
            mode_df = pd.read_excel(
                EXCEL_FILE,
                sheet_name=disease,
                usecols="C"
            )
    
            df["Mode"] = (
                mode_df.iloc[:, 0]
                .fillna("")
                .astype(str)
                .str.strip()
            )
    
        except Exception:
    
            df["Mode"] = ""
    
        return df

    def filter_gene_comments(df, input_genes):
        """
        Find matching gene comments while preserving
        the order entered by the user.
    
        Returns:
        filtered_rows
        genes_without_comments
        """
    
        filtered_rows = []
        genes_without_comments = []
    
        for gene in input_genes:
    
            matches = df[
                df["Gene"].str.upper() == gene
            ]
    
            if matches.empty:
                continue
    
            comment_values = (
                matches["Relevant_comments"]
                .fillna("")
                .astype(str)
                .str.strip()
            )
    
            if comment_values.eq("").all():
    
                genes_without_comments.append(gene)
    
            else:
    
                filtered_rows.append(matches)
    
        return filtered_rows, genes_without_comments


    def group_similar_comments(filtered_df):
        """
        Group similar gene comments using SequenceMatcher.
        """
    
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
    
                # Remove gene names before comparing comments
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
    
                    matching_genes.append(gene2)
                    used_indices.add(j)
    
            used_indices.add(i)
    
            if len(matching_genes) > 1:
    
                combined_comment = comment.replace(
                    gene,
                    " and ".join(matching_genes)
                )
    
                grouped_comments.append(
                    combined_comment
                )
    
            else:
    
                grouped_comments.append(
                    comment
                )
    
        return grouped_comments
    

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
    

    def display_gene_comments(filtered_df, grouped_comments):

        # If all comments have grouped into one short comment
        if (
            len(grouped_comments) == 1
            and len(str(grouped_comments[0])) < 250
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
    
            filtered_df = filtered_df.copy()
    
            filtered_df["Mode"] = (
                filtered_df["Mode"]
                .apply(format_mode)
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

    def get_remaining_panel_genes(
        selected_disease,
        input_genes,
        low_genes_upper
    ):
        """
        Return the remaining panel genes after removing
        detected genes and low-confidence genes.
        """
    
        panel_df = pd.read_excel(
            EXCEL_FILE,
            sheet_name="Panel"
        )
    
        auto_panel = DISEASE_TO_PANEL.get(
            selected_disease
        )
    
        if not auto_panel:
            return ""
    
        result = panel_df[
            panel_df["Panel"] == auto_panel
        ]
    
        if result.empty:
            return ""
    
        panel_genes = str(
            result.iloc[0]["Genes"]
        )
    
        panel_gene_list = [
            gene.strip()
            for gene in panel_genes.split(",")
        ]
    
        genes_to_remove = set(
            input_genes
            + low_genes_upper
        )
    
        panel_gene_list = [
            gene
            for gene in panel_gene_list
            if gene.strip().upper()
            not in genes_to_remove
        ]
    
        return ", ".join(
            panel_gene_list
        )

    def get_confidence_caveats(
    medium_genes,
    low_genes
    ):
        """
        Return Medium and Low confidence caveats
        for inclusion in the final report.
        """
    
        output = []
    
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
    
        for genes, caveat_name in [
            (medium_genes, "medium confidence"),
            (low_genes, "low confidence")
        ]:
    
            if not genes:
                continue
    
            result = caveat_df[
                caveat_df["Caveat"].str.lower()
                == caveat_name
            ]
    
            if result.empty:
                continue
    
            comment = result.iloc[0]["Comment"]
    
            if "[list genes]" in comment:
    
                comment = comment.replace(
                    "[list genes]",
                    ", ".join(genes)
                )
    
            if comment:
                output.append(comment)
    
        return output
