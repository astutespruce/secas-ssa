import numpy as np
import pandas as pd

from analysis.constants import DATASETS, URBAN_YEARS
from api.report.writer import write_excel

value_columns = (
    ["Urban in 2021\n(acres)"]
    + [f"{year}\n(acres)" for year in URBAN_YEARS]
    + ["Not projected to urbanize by 2100\n(acres)"]
)


def add_urbanization_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["urban"]

    urban = (
        df[["rasterized_acres"]]
        .join(
            df.urban.apply(pd.Series)[["low", "high"]]
            .melt(var_name="urban_level", value_name="acres", ignore_index=False)
            .dropna(subset="acres")
        )
        .set_index("urban_level", append=True)
    )
    urban["acres"] = urban.acres.astype(object)
    ix = urban.acres.isnull()
    urban.loc[ix, "acres"] = urban.loc[ix].acres.apply(lambda x: [np.nan] * len(value_columns))

    # convert acres from list into DataFrame and join (nodata already calculated in last position)
    acres = pd.DataFrame(urban.acres.tolist(), index=urban.index, columns=value_columns + ["outside_dataset_acres"])
    urban = urban.drop(columns=["acres"]).join(acres).reset_index(level=-1)

    urban.loc[urban.rasterized_acres == urban.outside_dataset_acres, value_columns] = np.nan

    urban["urban_level"] = urban.urban_level.map({"high": "High", "low": "Low"})

    breaks = np.arange(1, len(urban))[urban.index[1:] != urban.index[:-1]].tolist()

    urban = urban[["rasterized_acres", "outside_dataset_acres", "urban_level"] + value_columns]

    num_left_area_columns = 2
    has_area_outside_dataset = urban.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        urban = urban.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    urban = urban.rename(
        columns={
            "rasterized_acres": area_label,
            "outside_dataset_acres": "Area outside extent of this dataset\n(acres)",
            "urban_level": "Urbanization level",
        }
    ).reset_index()

    area_columns = list(range(1, num_left_area_columns + 1)) + list(
        range(1 + num_left_area_columns + 1, len(value_columns) + num_left_area_columns + 3)
    )

    column_widths = [name_col_width] + [area_col_width] * num_left_area_columns + [12] + ([18] * (len(value_columns)))

    write_excel(
        xlsx,
        urban,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )
