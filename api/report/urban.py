import pandas as pd

from analysis.constants import DATASETS, URBAN_YEARS
from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths

value_columns = (
    ["Urban in 2021 (acres)"]
    + [f"{year} (acres)" for year in URBAN_YEARS]
    + ["Not projected to urbanize by 2100 (acres)"]
)


def add_urbanization_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["urban"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    # transform data into one row for high and low urbanization per analysis unit
    urban = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.overlap_acres > 0:
            for level in ["low", "high"]:
                values = row["urban"][level]
                urban.append([id, row.overlap_acres, level.capitalize()] + list(values))
                counter += 1
        else:
            urban.append([id, row.overlap_acres])
            counter += 1

        breaks.append(counter)

    columns = value_columns + ["outside_acres"]
    urban = pd.DataFrame(
        urban,
        columns=[df.index.name, area_label, "Urbanization level"] + columns,
    )
    # move nodata to left
    urban = urban[[df.index.name, area_label, "Urbanization level", "outside_acres"] + value_columns]
    if urban.outside_acres.max() < 1e-2:
        urban = urban.drop(columns=["outside_acres"])

    urban = urban.rename(columns={"outside_acres": "Outside extent of this dataset"})

    urban.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 14] + ([18] * (len(urban.columns) - 2)))
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1] + list(range(3, len(value_columns) + 4)),
    )
    add_data_note(ws, description)
