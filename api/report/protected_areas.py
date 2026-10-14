import pandas as pd

from analysis.constants import DATASETS
from api.report.writer import write_excel


def add_protected_areas_sheet(xlsx, df, name_col_width, area_col_width):
    dataset = DATASETS["protected_areas"]

    # transform data into one row per per protected area per analysis unit
    protected_areas = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if hasattr(row, "protected_areas") and row.protected_areas:
            for pa in row.protected_areas:
                protected_areas.append(
                    [
                        id,
                        f"{row.acres:.2f}",
                        f"{pa['acres']:.2f}",
                        pa["name"],
                        pa["owner"],
                        pa["gap_status"],
                    ]
                )
        else:
            protected_areas.append(
                [
                    id,
                    f"{row.acres:.2f}",
                    "0",
                    "no protected areas at this location",
                    "",
                    "",
                ]
            )
            counter += 1

        breaks.append(counter)

    protected_areas = pd.DataFrame(
        protected_areas,
        columns=[
            df.index.name,
            "GIS Acres",
            "Overlap acres",
            "Protected area name",
            "Owner",
            "GAP status",
        ],
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
