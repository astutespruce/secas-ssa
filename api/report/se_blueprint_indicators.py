import pandas as pd

from analysis.constants import DATASETS
from api.report.style import CHAR_PER_WIDTH_UNIT
from api.report.writer import write_excel


def add_indicator_sheet(xlsx, df, dataset_id, name_col_width, area_label):
    dataset = DATASETS[dataset_id]
    values = dataset["values"]
    columns = [f"{v['label']}\n(acres)" for v in values]
    col_width = min(max([len(c) for c in columns]) * CHAR_PER_WIDTH_UNIT, 16)

    # split list into columns
    tmp = df[dataset_id].apply(pd.Series)
    tmp.columns = columns
    tmp = df[["rasterized_acres"]].join(tmp)

    # calculate area outside dataset
    tmp["outside_dataset"] = tmp.rasterized_acres - tmp[columns].sum(axis=1)
    # remove small rounding-related errors
    tmp.loc[tmp.outside_dataset < 0, "outside_dataset"] = 0

    # reorder columns
    tmp = tmp[["rasterized_acres", "outside_dataset"] + columns]
    has_area_outside = tmp.outside_dataset.max() > 1e-2
    if not has_area_outside:
        tmp = tmp.drop(columns=["outside_dataset"])

    tmp = tmp.rename(
        columns={"rasterized_acres": area_label, "outside_dataset": "Area outside extent of this dataset\n(acres)"}
    ).reset_index()

    column_widths = [name_col_width] + ([col_width] * (len(tmp.columns) - 1))
    area_columns = list(range(1, len(tmp.columns) + 3))
    caption = f"{dataset['name']}.\n{dataset['description']}"
    write_excel(
        xlsx,
        tmp,
        sheet_name=dataset["sheet_name"],
        caption=caption,
        column_widths=column_widths,
        area_columns=area_columns,
    )
