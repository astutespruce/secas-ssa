import numpy as np
import pandas as pd

from analysis.constants import DATASETS
from api.report.writer import write_excel


def add_protected_areas_sheet(xlsx, df, name_col_width, area_col_width):
    dataset = DATASETS["protected_areas"]

    if "protected_areas" in df.columns:
        protected_areas = df.protected_areas.explode()
        ix = protected_areas.isnull()
        protected_areas.loc[ix] = protected_areas.loc[ix].apply(
            lambda x: {"name": "", "owner": "", "gap_status": "", "acres": 0}
        )
        protected_areas = protected_areas.apply(pd.Series)

    else:
        protected_areas = pd.DataFrame(
            [{"name": "", "owner": "", "gap_status": "", "acres": 0}] * len(df), index=df.index
        )

    protected_areas = df[["acres"]].rename(columns={"acres": "total_acres"}).join(protected_areas)

    breaks = np.arange(1, len(protected_areas))[protected_areas.index[1:] != protected_areas.index[:-1]].tolist()

    protected_areas = (
        protected_areas[["total_acres", "acres", "name", "owner", "gap_status"]]
        .rename(
            columns={
                "total_acres": "GIS Acres",
                "acres": "Overlap acres",
                "name": "Protected area name",
                "owner": "Owner",
                "gap_status": "GAP status",
            }
        )
        .reset_index()
    )

    column_widths = [name_col_width, area_col_width, area_col_width, 40, 30, 10]
    write_excel(
        xlsx,
        protected_areas,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=[1, 2],
        breaks=breaks,
    )
