import pandas as pd

from analysis.constants import DATASETS, SLR_DEPTHS, SLR_YEARS, SLR_NODATA_VALUES

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


SLR_BINS = SLR_DEPTHS + [v["value"] for v in SLR_NODATA_VALUES]


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
        # must also have depth to show projection data
        if (
            row.overlap == 0
            or row.get("slr_depth", None) is None
            or row.get("slr_proj", None) is None
        ):
            slr.append([id, row.overlap, "no", ""] + [""] * len(SLR_YEARS))
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
        out_row = [id, row.overlap]
        if row.overlap > 0:
            out_row += list(row.slr_depth)

        slr.append(out_row)

    first_cols = [df.index.name, area_label]
    depth_cols = [f"Inundated at {depth} feet (acres)" for depth in SLR_DEPTHS]
    nodata_cols = [f"{v['label']} (acres)" for v in SLR_NODATA_VALUES]

    slr = pd.DataFrame(
        slr,
        columns=first_cols + depth_cols + nodata_cols,
    )
    # reorder to put NODATA col to the left
    slr = slr[first_cols + [nodata_cols[2]] + depth_cols + nodata_cols[:2]]

    remove_cols = []
    for col in nodata_cols:
        if slr[col].sum() == 0:
            remove_cols.append(col)
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    num_value_cols = len(slr.columns) - 2

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 12] + ([12] * num_value_cols)
    )
    set_cell_styles(
        ws,
        area_columns=[1] + list(range(2, num_value_cols + 3)),
    )
    add_data_note(ws, description)
