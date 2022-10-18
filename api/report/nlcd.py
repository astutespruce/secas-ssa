import numpy as np
import pandas as pd

from analysis.constants import DATASETS, NLCD_YEARS

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_ncld_landcover_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_landcover"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    # transform data into one row per land cover type per analysis unit
    nlcd = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        for landcover, values in row.nlcd_landcover.items():
            nlcd.append([id, row.overlap, landcover] + list(values))

            counter += 1
        breaks.append(counter)

    nlcd = pd.DataFrame(
        nlcd,
        columns=[df.index.name, area_label, "Land cover type"]
        + [f"{year} (acres)" for year in NLCD_YEARS],
    )

    nlcd.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 30] + ([12] * len(NLCD_YEARS))
    )
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1] + list(range(3, len(NLCD_YEARS) + 4)),
    )

    add_data_note(ws, description)


def add_ncld_impervious_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_impervious"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    nlcd = df.nlcd_impervious.apply(pd.Series)
    nlcd.columns = [f"{year} (acres)" for year in NLCD_YEARS]
    nlcd = df[["overlap"]].join(nlcd)

    nlcd.reset_index().to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width] + ([12] * len(NLCD_YEARS)))
    set_cell_styles(
        ws,
        area_columns=[1] + list(range(2, len(NLCD_YEARS) + 3)),
    )

    add_data_note(ws, description)
