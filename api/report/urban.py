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

    # transform data into one row for high and low urbanization per analysis unit
    urban = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row["urban"]:
            for level in ["low", "high"]:
                values = row["urban"][level]
                urban.append([id, row.rasterized_acres, level.capitalize()] + list(values))
                counter += 1
        else:
            urban.append([id, row.rasterized_acres] + [""] * len(values))
            counter += 1

        breaks.append(counter)

    columns = value_columns + ["outside_dataset_acres"]
    urban = pd.DataFrame(
        urban,
        columns=[df.index.name, area_label, "Urbanization level"] + columns,
    )
    # move nodata to left
    urban = urban[[df.index.name, area_label, "outside_dataset_acres", "Urbanization level"] + value_columns]

    has_area_outside_dataset = urban.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        urban = urban.drop(columns=["outside_dataset_acres"])

    urban = urban.rename(columns={"outside_dataset_acres": "Area outside extent of this dataset\n(acres)"})

    column_widths = [name_col_width] + ([18] * (len(urban.columns) - 1))
    area_columns = [i for i, c in enumerate(urban.columns) if "acres" in c]
    write_excel(
        xlsx,
        urban,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )
