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
        if row.landfire_evt:
            outside_dataset_acres = max(row.rasterized_acres - sum(row.landfire_evt.values()), 0)
            for index, acres in row.landfire_evt.items():
                evt = LANDFIRE_INDEXES[index]
                rows.append([id, row.rasterized_acres, outside_dataset_acres, acres, evt["label"], evt["group"]])
                counter += 1
        else:
            rows.append([id, row.rasterized_acres, row.rasterized_acres, "", "", ""])
            counter += 1

        breaks.append(counter)

    landfire_evt = pd.DataFrame(
        rows,
        columns=[
            df.index.name,
            area_label,
            "outside_dataset_acres",
            "Acres",
            "Existing Vegetation Type",
            "Group",
        ],
    )

    has_area_outside_dataset = landfire_evt.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        landfire_evt = landfire_evt.drop(columns=["outside_dataset_acres"])

    landfire_evt = landfire_evt.rename(
        columns={"outside_dataset_acres": "Area outside extent of this dataset\n(acres)"}
    )

    num_area_columns = len([c for c in landfire_evt.columns if "acres" in c.lower()])

    write_excel(
        xlsx,
        landfire_evt,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=[name_col_width] + [area_col_width] * num_area_columns + [30, 30],
        area_columns=list(range(1, num_area_columns + 1)),
        breaks=breaks,
    )
