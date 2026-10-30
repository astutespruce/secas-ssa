import numpy as np
import pandas as pd

from analysis.constants import DATASETS
from api.report.writer import write_excel
from api.settings import DATA_DIR

table_filename = DATA_DIR / "inputs/landfire/landfire_evt.feather"


def add_landfire_evt_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["landfire_evt"]

    table = pd.read_feather(table_filename).set_index("value")

    landfire_evt = df[["rasterized_acres"]].join(
        df.landfire_evt.apply(pd.Series)
        .melt(var_name="value", value_name="acres", ignore_index=False)
        .dropna(subset="acres")
        .join(table, on="value")
    )
    landfire_evt = landfire_evt.join(landfire_evt.groupby(level=0).acres.sum().rename("total_acres"))
    landfire_evt["outside_dataset_acres"] = (landfire_evt.rasterized_acres - landfire_evt.total_acres).fillna(0)
    landfire_evt.loc[landfire_evt.outside_dataset_acres < 1e-6, "outside_dataset_acres"] = 0
    landfire_evt["label"] = landfire_evt.label.fillna("")
    landfire_evt["group"] = landfire_evt.group.fillna("")
    landfire_evt["acres"] = landfire_evt.acres.fillna(np.nan)

    breaks = np.arange(1, len(landfire_evt))[landfire_evt.index[1:] != landfire_evt.index[:-1]].tolist()

    landfire_evt = landfire_evt[["rasterized_acres", "outside_dataset_acres", "acres", "label", "group"]]

    num_left_area_columns = 3
    has_area_outside_dataset = landfire_evt.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        landfire_evt = landfire_evt.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    landfire_evt = landfire_evt.rename(
        columns={
            "rasterized_acres": area_label,
            "outside_dataset_acres": "Area outside extent of this dataset\n(acres)",
            "acres": "Acres",
            "label": "Existing Vegetation Type",
            "group": "Group",
        }
    ).reset_index()

    write_excel(
        xlsx,
        landfire_evt,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=[name_col_width] + [area_col_width] * num_left_area_columns + [50, 40],
        area_columns=list(range(1, num_left_area_columns + 1)),
        breaks=breaks,
    )
