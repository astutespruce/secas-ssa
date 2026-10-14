import pandas as pd

from analysis.constants import DATASETS, NLCD_YEARS
from api.report.writer import write_excel

value_columns = [f"{year} (acres)" for year in NLCD_YEARS]


def add_ncld_landcover_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd_landcover"]

    # transform data into one row per land cover type per analysis unit
    nlcd_landcover = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.overlap_acres > 0:
            for landcover, values in row.nlcd_landcover.items():
                nlcd_landcover.append([id, row.overlap_acres, landcover] + list(values))
                counter += 1
        else:
            nlcd_landcover.append([id, row.overlap_acres])
            counter += 1

        breaks.append(counter)

    nlcd_landcover = pd.DataFrame(
        nlcd_landcover,
        columns=[df.index.name, area_label, "Land cover type"] + value_columns,
    )

    column_widths = [name_col_width, area_col_width, 30] + ([12] * len(NLCD_YEARS))
    area_columns = [1] + list(range(3, len(NLCD_YEARS) + 4))
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
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    nlcd_impervious = df.nlcd_impervious.apply(pd.Series)
    nlcd_impervious.columns = value_columns

    nlcd_impervious = (
        df[["overlap_acres"]].rename(columns={"overlap_acres": area_label}).join(nlcd_impervious).reset_index()
    )

    column_widths = [name_col_width, area_col_width] + ([12] * len(NLCD_YEARS))
    area_columns = [1] + list(range(2, len(NLCD_YEARS) + 3))
    write_excel(
        xlsx,
        nlcd_impervious,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
    )
