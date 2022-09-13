import numpy as np
import pandas as pd

from analysis.constants import DATASETS, NLCD_YEARS

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_ncld_landcover_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_landcover"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    # transform data into one row per land cover type per population
    nlcd = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        for landcover, values in row.nlcd_landcover.items():
            # convert to proportion, displayed as percent
            nlcd.append(
                [id, row.overlap, landcover] + list((np.asarray(values) / row.overlap))
            )

            counter += 1
        breaks.append(counter)

    nlcd = pd.DataFrame(
        nlcd,
        columns=[df.index.name, area_label, "Land cover type"] + NLCD_YEARS,
    )

    nlcd.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 30] + ([8] * len(NLCD_YEARS))
    )
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1],
        percent_columns=list(range(3, len(NLCD_YEARS) + 4)),
    )

    add_data_note(ws, description)


def add_ncld_impervious_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_impervious"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    nlcd = df.nlcd_impervious.apply(pd.Series)
    nlcd.columns = NLCD_YEARS
    nlcd = df[["overlap"]].join(nlcd)
    for col in NLCD_YEARS:
        nlcd[col] = nlcd[col] / nlcd.overlap

    nlcd.reset_index().to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width] + ([8] * len(NLCD_YEARS)))
    set_cell_styles(
        ws,
        area_columns=[1],
        percent_columns=list(range(2, len(NLCD_YEARS) + 3)),
    )

    add_data_note(ws, description)
