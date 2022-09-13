import numpy as np
import pandas as pd

from analysis.constants import (
    DATASETS,
    SLR_DEPTHS,
    SLR_YEARS,
)

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_slr_projection_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    """Add sheet with decadal projections for each population unit, only if
    there is SLR at 10ft within the population unit.
    """
    dataset = DATASETS["slr_proj"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    # transform data into one row per SLR scenario per population
    slr = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        # must have depth to show projection data
        if row.get("slr_depth", None) is None or row.get("slr_proj", None) is None:
            slr.append([id, row.overlap, "no"] + [""] * (len(SLR_YEARS) + 1))
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
    description = dataset["description"]

    slr = []
    for id, row in df.iterrows():
        if row.slr_depth is None:
            slr.append([id, row.overlap, "no"] + [""] * len(SLR_DEPTHS))
        else:
            # calculate proportion
            slr.append(
                [id, row.overlap, "yes"] + list(np.array(row.slr_depth) / row.overlap)
            )

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label, "Has SLR up to 10ft?"]
        + [f"Inundated at {depth} feet" for depth in SLR_DEPTHS],
    )

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 10] + ([10] * len(SLR_DEPTHS))
    )
    set_cell_styles(
        ws, area_columns=[1], percent_columns=list(range(3, len(SLR_DEPTHS) + 4))
    )
    add_data_note(ws, description)
