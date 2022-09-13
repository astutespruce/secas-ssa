import numpy as np
import pandas as pd


from analysis.constants import DATASETS, URBAN_YEARS

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_urbanization_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["urban"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    # transform data into one row for high and low urbanization per population
    years = [2019] + URBAN_YEARS
    urban = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        for level in ["low", "high"]:
            values = row["urban"][level]
            urban.append(
                [id, row.overlap, level.capitalize()]
                + list((np.asarray(values) / row.overlap))
            )

            counter += 1
        breaks.append(counter)

    urban = pd.DataFrame(
        urban,
        columns=[df.index.name, area_label, "Urbanization level"] + years,
    )

    urban.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 10] + ([10] * len(years)))
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1],
        percent_columns=list(range(3, len(years) + 4)),
    )
    add_data_note(ws, description)
