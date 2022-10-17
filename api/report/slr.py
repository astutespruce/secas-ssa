import numpy as np
import pandas as pd

from analysis.constants import DATASETS, SLR_DEPTHS, SLR_YEARS, SLR_NODATA_VALUES

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


SLR_NODATA_LABELS = {v["key"]: v["label"] for v in SLR_NODATA_VALUES}


def add_slr_projection_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    """Add sheet with decadal projections for each analysis unit, only if
    there is SLR at 10ft within the analysis unit.
    """
    dataset = DATASETS["slr_proj"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    # transform data into one row per SLR scenario per analysis unit
    slr = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        # must have depth to show projection data
        if (
            "slr_depth" in row
            and isinstance(row["slr_depth"], str)
            and row["slr_depth"] in SLR_NODATA_LABELS
        ):
            slr.append(
                [id, row.overlap, SLR_NODATA_LABELS[row["slr_depth"]]]
                + [""] * (len(SLR_YEARS) + 1)
            )
            counter += 1
        else:
            for scenario, values in row.slr_proj.items():
                slr.append([id, row.overlap, "yes", scenario] + list(values))

                counter += 1
        breaks.append(counter)

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label, "Has projected SLR?", "SLR scenario"]
        + [f"{year} (ft)" for year in SLR_YEARS],
    )

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 10, 18] + ([8] * len(SLR_YEARS))
    )
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1],
    )

    add_data_note(ws, description)


def add_slr_inundation_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["slr_depth"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    slr = []
    for id, row in df.iterrows():
        if isinstance(row["slr_depth"], str) and row["slr_depth"] in SLR_NODATA_LABELS:
            slr.append(
                [id, row.overlap, SLR_NODATA_LABELS[row["slr_depth"]]]
                + [""] * len(SLR_DEPTHS)
            )
        else:
            # calculate proportion
            slr.append(
                [id, row.overlap, "yes"] + list(np.array(row.slr_depth) / row.overlap)
            )

    nodata_cols = [f"{v['label']} (acres)" for v in SLR_NODATA_VALUES]
    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label, "Has SLR up to 10ft?"]
        + [f"Inundated at {depth} feet" for depth in SLR_DEPTHS]
        + nodata_cols,
    )
    remove_cols = []
    for col in nodata_cols:
        if slr[col].sum() == 0:
            remove_cols.append(col)
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    num_percent_columns = len(slr.columns) - 3

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 10] + ([10] * num_percent_columns)
    )
    set_cell_styles(
        ws, area_columns=[1], percent_columns=list(range(3, num_percent_columns + 4))
    )
    add_data_note(ws, description)
