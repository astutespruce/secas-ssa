import pandas as pd

from analysis.constants import DATASETS, SLR_DEPTH_VALUES, SLR_NODATA_VALUES, SLR_PROJ_SCENARIOS, SLR_YEARS
from api.report.writer import write_excel

SLR_BINS = SLR_DEPTH_VALUES + [v["value"] for v in SLR_NODATA_VALUES]

depth_value_columns = [f"Inundated at {v['label']} (acres)" for v in SLR_DEPTH_VALUES] + [
    f"{v['label']} (acres)" for v in SLR_NODATA_VALUES
]

proj_value_columns = ["Has projected SLR?", "SLR scenario"] + [f"{year} (feet)" for year in SLR_YEARS]


def add_slr_projection_sheet(
    xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float, area_col_width: float, area_label: str
):
    """Add sheet with decadal projections for each analysis unit, only if
    there is SLR at 10ft within the analysis unit.
    """
    dataset = DATASETS["slr_proj"]

    # transform data into one row per SLR scenario per analysis unit
    slr = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        # must also have depth to show projection data
        if row.overlap_acres == 0 or row.get("slr_depth", None) is None or not len(row.get("slr_proj", [])):
            slr.append([id, row.overlap_acres, "no", ""] + [""] * len(SLR_YEARS))
            counter += 1
        else:
            for scenario in row.slr_proj:
                slr.append(
                    [id, row.overlap_acres, "yes", SLR_PROJ_SCENARIOS[scenario["scenario"]]] + list(scenario["values"])
                )
                counter += 1

            breaks.append(counter)

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label] + proj_value_columns,
    )

    column_widths = [name_col_width, area_col_width, 10, 18] + ([12] * len(SLR_YEARS))
    # SLR values are not really areas but we want 2 decimal places
    area_columns = area_columns = [1] + list(range(4, len(SLR_YEARS) + 5))
    write_excel(
        xlsx,
        slr,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )


def add_slr_inundation_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["slr_depth"]

    # split values into columns
    slr = df.slr_depth.apply(pd.Series)

    # set NODATA into value 13
    outside_acres = df.overlap_acres - slr.sum(axis=1)
    outside_acres.loc[outside_acres < 0] = 0
    slr[13] += outside_acres

    slr = df[["overlap_acres"]].join(slr)
    slr.columns = ["overlap_acres"] + depth_value_columns

    # reorder columns so that SLR not available (last column) comes first
    slr = (
        slr[["overlap_acres", depth_value_columns[-1]] + depth_value_columns[:-1]]
        .rename(columns={"overlap_acres": area_label})
        .reset_index()
    )

    # drop unnecessary nodata
    remove_cols = []
    for col in depth_value_columns[-3:]:
        if slr[col].sum() == 0:
            remove_cols.append(col)
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    num_value_cols = len(slr.columns) - 2

    column_widths = [name_col_width, area_col_width] + ([18] * num_value_cols)

    area_columns = [1] + list(range(2, num_value_cols + 3))
    write_excel(
        xlsx,
        slr,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
    )
