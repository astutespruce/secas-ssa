import pandas as pd

from analysis.constants import DATASETS

from api.report.metadata import add_data_note
from api.report.style import CHAR_PER_WIDTH_UNIT, set_cell_styles, set_column_widths


def add_indicator_sheet(
    xlsx, df, dataset_id, name_col_width, area_col_width, area_label
):
    dataset = DATASETS[dataset_id]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]
    values = dataset["values"]
    nodata_label = dataset.get(
        "nodata_label", f"Area outside {sheet_name.lower()} data extent"
    )

    columns = [f"{v['label']} (acres)" for v in values]
    col_width = min(max([len(c) for c in columns]) * CHAR_PER_WIDTH_UNIT, 16)

    # split list into columns
    tmp = df[dataset_id].apply(pd.Series)
    tmp.columns = columns
    tmp = df[["overlap"]].join(tmp)

    # calculate area outside
    tmp["outside"] = tmp.overlap - tmp[columns].sum(axis=1)
    # remove small rounding-related errors
    tmp.loc[tmp.outside < 0, "outside"] = 0

    # reorder columns
    tmp = tmp[["overlap", "outside"] + columns]
    has_area_outside = tmp.outside.max() > 1e-2
    if not has_area_outside:
        tmp = tmp.drop(columns=["outside"])

    tmp.rename(
        columns={"overlap": area_label, "outside": nodata_label}
    ).reset_index().to_excel(xlsx, sheet_name=sheet_name, index=False)

    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width] + ([col_width] * len(tmp.columns)))
    set_cell_styles(ws, area_columns=range(1, len(tmp.columns) + 3))
    add_data_note(ws, description)
