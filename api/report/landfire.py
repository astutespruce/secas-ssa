import pandas as pd

from analysis.constants import DATASETS, LANDFIRE_INDEXES
from api.report.writer import write_excel


def add_landfire_evt_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["landfire_evt"]

    # transform data into one row per land cover type per analysis unit
    rows = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.overlap_acres > 0:
            for index, acres in row.landfire_evt.items():
                evt = LANDFIRE_INDEXES[index]
                rows.append([id, row.overlap_acres, evt["label"], evt["group"], acres])
                counter += 1
        else:
            rows.append([id, row.overlap_acres])
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

    write_excel(
        xlsx,
        landfire_evt,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=[name_col_width, area_col_width, 30, 30, 12],
        area_columns=[1, 4],
        breaks=breaks,
    )
