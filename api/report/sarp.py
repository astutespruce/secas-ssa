from analysis.constants import DATASETS

from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_sarp_barriers_sheet(xlsx, df, name_col_width):
    dataset = DATASETS["sarp_aquatic_barriers"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    barriers = df[["subwatersheds", "dams", "crossings",]].rename(
        columns={
            "subwatersheds": "Subwatersheds",
            "dams": "Dams",
            "crossings": "Potential road-related barriers",
        }
    )
    barriers.reset_index().to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]

    set_column_widths(ws, [name_col_width, 14, 12, 12])

    set_cell_styles(ws)

    add_data_note(ws, description)


def add_sarp_network_alteration_sheet(xlsx, df, name_col_width):
    dataset = DATASETS["sarp_aquatic_network_alteration"]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    alteration = df[
        ["subwatersheds", "altered_miles", "total_miles", "pct_altered"]
    ].rename(
        columns={
            "subwatersheds": "Subwatersheds",
            "altered_miles": "Altered miles",
            "total_miles": "Total miles",
            "pct_altered": "Percent of aquatic network altered",
        }
    )
    alteration.reset_index().to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]

    set_column_widths(ws, [name_col_width, 14, 12, 12, 12])

    set_cell_styles(ws, area_columns=[2, 3], percent_columns=[4])

    add_data_note(ws, description)
