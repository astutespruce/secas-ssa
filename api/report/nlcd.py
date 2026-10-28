import numpy as np
import pandas as pd

from analysis.constants import DATASETS, NLCD_YEARS
from api.report.writer import write_excel

value_columns = [f"{year}\n(acres)" for year in NLCD_YEARS]


def add_ncld_landcover_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_landcover"]

    nlcd_landcover = (
        df[["rasterized_acres"]]
        .join(
            df.nlcd_landcover.apply(pd.Series)
            .melt(var_name="label", value_name="acres", ignore_index=False)
            .dropna(subset="acres")
        )
        .set_index("label", append=True)
    )
    nlcd_landcover["acres"] = nlcd_landcover.acres.astype(object)
    ix = nlcd_landcover.acres.isnull()
    nlcd_landcover.loc[ix, "acres"] = nlcd_landcover.loc[ix].acres.apply(lambda x: [np.nan] * len(value_columns))
    # convert acres from list into DataFrame and join
    acres = pd.DataFrame(nlcd_landcover.acres.tolist(), index=nlcd_landcover.index, columns=value_columns)
    nlcd_landcover = nlcd_landcover.drop(columns=["acres"]).join(acres).reset_index(level=-1)
    nlcd_landcover = nlcd_landcover.join(nlcd_landcover.groupby(level=0)[value_columns[0]].sum().rename("total_acres"))
    nlcd_landcover["label"] = nlcd_landcover.label.fillna("")

    # use first year to calculate nodata
    nlcd_landcover["outside_dataset_acres"] = nlcd_landcover.rasterized_acres - nlcd_landcover.total_acres
    nlcd_landcover.loc[nlcd_landcover.outside_dataset_acres < 1e-6, "outside_dataset_acres"] = 0

    breaks = np.arange(1, len(nlcd_landcover))[nlcd_landcover.index[1:] != nlcd_landcover.index[:-1]].tolist()

    nlcd_landcover = nlcd_landcover[
        ["rasterized_acres", "outside_dataset_acres", "label"] + value_columns
    ].reset_index()

    num_left_area_columns = 2
    has_area_outside_dataset = nlcd_landcover.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        nlcd_landcover = nlcd_landcover.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    nlcd_landcover = nlcd_landcover.rename(
        columns={
            "rasterized_acres": area_label,
            "outside_dataset_acres": "Area outside extent of this dataset\n(acres)",
            "label": "Land cover type",
        }
    )

    column_widths = [name_col_width] + [area_col_width] * num_left_area_columns + [30] + ([12] * len(value_columns))
    area_columns = list(range(1, num_left_area_columns + 1)) + list(
        range(1 + num_left_area_columns + 1, len(value_columns) + num_left_area_columns + 3)
    )

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
    nlcd_impervious.columns = value_columns + ["outside_dataset_acres"]

    nlcd_impervious = df[["rasterized_acres"]].join(nlcd_impervious)
    nlcd_impervious = nlcd_impervious[["rasterized_acres", "outside_dataset_acres"] + value_columns]
    nlcd_impervious.loc[nlcd_impervious.rasterized_acres == nlcd_impervious.outside_dataset_acres, value_columns] = (
        np.nan
    )

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
    area_columns = list(range(1, len(nlcd_impervious.columns)))
    write_excel(
        xlsx,
        nlcd_impervious,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
    )
