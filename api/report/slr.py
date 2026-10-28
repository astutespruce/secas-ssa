import numpy as np
import pandas as pd

from analysis.constants import DATASETS, SLR_DEPTH_VALUES, SLR_NODATA_VALUES, SLR_PROJ_SCENARIOS, SLR_YEARS
from api.report.writer import write_excel

SLR_BINS = SLR_DEPTH_VALUES + [v["value"] for v in SLR_NODATA_VALUES]

depth_value_columns = [f"Inundated at {v['label']}\n(acres)" for v in SLR_DEPTH_VALUES] + [
    f"{v['label']}\n(acres)" for v in SLR_NODATA_VALUES
]

proj_value_columns = ["Has projected SLR?", "SLR scenario"] + [f"{year}\n(feet)" for year in SLR_YEARS]


def add_slr_projection_sheet(xlsx: pd.ExcelWriter, df: pd.DataFrame, name_col_width: float):
    """Add sheet with decadal projections for each analysis unit, only if
    there is SLR at 10ft within the analysis unit.
    """
    dataset = DATASETS["slr_proj"]

    if "slr_proj" in df.columns:
        slr_proj = df.slr_proj.explode()
        ix = slr_proj.isnull()
        slr_proj.loc[ix] = slr_proj.loc[ix].apply(
            lambda x: {"scenario": "", "values": [np.nan] * len(proj_value_columns[2:])}
        )
        slr_proj = slr_proj.apply(pd.Series).set_index("scenario", append=True)

    else:
        slr_proj = pd.DataFrame(
            [{"scenario": "", "values": [np.nan] * len(proj_value_columns[2:])}] * len(df), index=df.index
        ).set_index("scenario", append=True)

    values = pd.DataFrame(slr_proj["values"].tolist(), index=slr_proj.index, columns=proj_value_columns[2:])
    slr_proj = slr_proj.drop(columns=["values"]).join(values).reset_index(level=-1)

    breaks = np.arange(1, len(slr_proj))[slr_proj.index[1:] != slr_proj.index[:-1]].tolist()

    slr_proj["scenario"] = slr_proj.scenario.map(SLR_PROJ_SCENARIOS).fillna("")
    slr_proj["has_scenario"] = (slr_proj.scenario == "").map({False: "yes", True: "no"})

    slr_proj = (
        slr_proj[["has_scenario", "scenario"] + proj_value_columns[2:]]
        .rename(columns={"has_scenario": "Has projected SLR?", "scenario": "SLR scenario"})
        .reset_index()
    )

    column_widths = [name_col_width, 10, 18] + ([12] * len(SLR_YEARS))
    # SLR values are not really areas but we want 2 decimal places
    area_columns = area_columns = [1] + list(range(4, len(SLR_YEARS) + 5))
    write_excel(
        xlsx,
        slr_proj,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )


def add_slr_inundation_sheet(xlsx, df, name_col_width, area_label):
    dataset = DATASETS["slr_depth"]

    # split values into columns
    slr = df[["rasterized_acres"]].join(df.slr_depth.apply(pd.Series))
    slr.columns = ["rasterized_acres"] + depth_value_columns + ["outside_dataset_acres"]

    slr.loc[slr.rasterized_acres == slr.outside_dataset_acres, depth_value_columns] = np.nan

    # reorder columns so that nodata comes first
    slr = (
        slr[["rasterized_acres", "outside_dataset_acres"] + depth_value_columns]
        .reset_index()
        .rename(
            columns={
                "rasterized_acres": area_label,
                "outside_dataset_acres": "Area outside extent of this dataset\n(acres)",
            }
        )
    )

    # drop unnecessary nodata
    remove_cols = []
    for col in depth_value_columns[-len(SLR_NODATA_VALUES) :]:
        if slr[col].sum() == 0:
            remove_cols.append(col)
    if remove_cols:
        slr = slr.drop(columns=remove_cols)

    num_value_cols = len(slr.columns) - 2
    column_widths = [name_col_width] + ([18] * (num_value_cols + 1))
    area_columns = [1] + list(range(2, num_value_cols + 3))
    write_excel(
        xlsx,
        slr,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
    )
