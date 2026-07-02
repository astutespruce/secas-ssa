import pandas as pd

from analysis.constants import DATASETS

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_protected_areas_sheet(xlsx, df, name_col_width, area_col_width):
    dataset = DATASETS["protected_areas"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

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
                        pa["name"],
                        pa["owner"],
                        pa["gap_status"],
                        f"{pa['acres']:.2f}",
                    ]
                )
        else:
            protected_areas.append(
                [
                    id,
                    f"{row.acres:.2f}",
                    "no protected areas at this location",
                    "",
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
            "Protected area name",
            "Owner",
            "GAP status",
            "Overlap acres",
        ],
    )
    protected_areas.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]

    set_column_widths(ws, [name_col_width, area_col_width, 40, 30, 20, area_col_width])

    set_cell_styles(ws)

    add_data_note(ws, description)
