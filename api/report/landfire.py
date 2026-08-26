import pandas as pd

from analysis.constants import DATASETS, LANDFIRE_INDEXES
from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_landfire_evt_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["landfire_evt"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    # transform data into one row per land cover type per analysis unit
    rows = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.overlap > 0:
            for index, acres in row.landfire_evt.items():
                evt = LANDFIRE_INDEXES[index]
                rows.append([id, row.overlap, evt["label"], evt["group"], acres])
                counter += 1
        else:
            rows.append([id, row.overlap])
            counter += 1

        breaks.append(counter)

    landfire_evt = pd.DataFrame(
        rows,
        columns=[
            df.index.name,
            area_label,
            "Existing Vegetation Type",
            "Group",
            "Acres",
        ],
    )

    landfire_evt.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 30, 30, 12])
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1, 4],
    )

    add_data_note(ws, description)
