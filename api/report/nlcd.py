import pandas as pd

from analysis.constants import DATASETS, NLCD_YEARS
from api.report.writer import write_excel

value_columns = [f"{year}\n(acres)" for year in NLCD_YEARS]


def add_ncld_landcover_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_landcover"]

    # transform data into one row per land cover type per analysis unit
    nlcd_landcover = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.nlcd_landcover:
            outside_dataset_acres = max(row.rasterized_acres - sum([v[0] for v in row.nlcd_landcover.values()]), 0)
            for landcover, values in row.nlcd_landcover.items():
                nlcd_landcover.append([id, row.rasterized_acres, outside_dataset_acres, landcover] + list(values))
                counter += 1
        else:
            nlcd_landcover.append([id, row.rasterized_acres, row.rasterized_acres, ""] + [""] * len(value_columns))
            counter += 1

        breaks.append(counter)

    nlcd_landcover = pd.DataFrame(
        nlcd_landcover,
        columns=[df.index.name, area_label, "outside_dataset_acres", "Land cover type"] + value_columns,
    )

    num_left_area_columns = 2
    has_area_outside_dataset = nlcd_landcover.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        nlcd_landcover = nlcd_landcover.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    nlcd_landcover = nlcd_landcover.rename(
        columns={"outside_dataset_acres": "Area outside extent of this dataset\n(acres)"}
    )

    column_widths = [name_col_width] + [area_col_width] * num_left_area_columns + [30] + ([12] * len(NLCD_YEARS))
    area_columns = list(range(1, num_left_area_columns + 1)) + list(range(3, len(NLCD_YEARS) + 4))
    write_excel(
        xlsx,
        nlcd_landcover,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )


def add_ncld_impervious_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_impervious"]

    nlcd_impervious = df.nlcd_impervious.apply(pd.Series)
    nlcd_impervious.columns = value_columns

    nlcd_impervious = df[["rasterized_acres"]].join(nlcd_impervious)
    nlcd_impervious["outside_dataset_acres"] = nlcd_impervious.rasterized_acres - nlcd_impervious[value_columns].sum(
        axis=1
    )
    nlcd_impervious = nlcd_impervious[["rasterized_acres", "outside_dataset_acres"] + value_columns]

    num_left_area_columns = 2
    has_area_outside_dataset = nlcd_impervious.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        nlcd_impervious = nlcd_impervious.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    nlcd_impervious = nlcd_impervious.rename(
        columns={
            "rasterized_acres": area_label,
            "outside_dataset_acres": "Area outside extent of this dataset\n(acres)",
        }
    ).reset_index()

    column_widths = [name_col_width] + [area_col_width] * num_left_area_columns + ([12] * len(NLCD_YEARS))
    area_columns = list(range(1, num_left_area_columns + 1)) + list(range(2, len(NLCD_YEARS) + 3))
    write_excel(
        xlsx,
        nlcd_impervious,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
    )
