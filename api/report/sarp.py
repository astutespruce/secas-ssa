from analysis.constants import DATASETS
from api.report.writer import write_excel


def add_sarp_barriers_sheet(xlsx, df, name_col_width):
    dataset = DATASETS["sarp_aquatic_barriers"]

    barriers = (
        df[
            [
                "subwatersheds",
                "dams",
                "crossings",
            ]
        ]
        .rename(
            columns={
                "subwatersheds": "Subwatersheds",
                "dams": "Dams",
                "crossings": "Potential road-related barriers",
            }
        )
        .reset_index()
    )

    write_excel(
        xlsx,
        barriers,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=[name_col_width, 14, 12, 16],
    )


def add_sarp_network_alteration_sheet(xlsx, df, name_col_width):
    dataset = DATASETS["sarp_aquatic_network_alteration"]

    alteration = (
        df[["subwatersheds", "altered_miles", "total_miles", "pct_altered"]]
        .rename(
            columns={
                "subwatersheds": "Subwatersheds",
                "altered_miles": "Altered miles",
                "total_miles": "Total miles",
                "pct_altered": "Percent of aquatic network altered",
            }
        )
        .reset_index()
    )

    write_excel(
        xlsx,
        alteration,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=[name_col_width, 14, 14, 12, 16],
        area_columns=[2, 3],
        percent_columns=[4],
    )
