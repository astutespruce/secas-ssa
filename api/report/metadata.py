import pandas as pd

from analysis.constants import DATASETS
from api.report.style import alignment_left_wrap, description_font
from api.report.writer import write_excel


def add_data_note(ws, content, columns=None):
    columns = columns or len(list(ws.columns)) - 1
    # add data note below data table
    row_index = len(list(ws.rows)) + 3
    ws.merge_cells(
        start_row=row_index,
        start_column=1,
        end_row=row_index + 1,
        end_column=columns + 1,
    )
    cell_index = f"A{row_index}"
    ws[cell_index].value = content
    ws[cell_index].font = description_font
    ws[cell_index].alignment = alignment_left_wrap


def add_data_details_sheet(xlsx, datasets):
    # Keep original order so it matches sheets
    metadata = pd.DataFrame([DATASETS[dataset] for dataset in DATASETS if dataset in datasets])[
        [
            "name",
            "sheet_name",
            "source",
            "date",
            "description",
            "methods",
            "citation",
            "url",
        ]
    ].rename(
        columns={
            "name": "Name",
            "sheet_name": "Sheet",
            "source": "Data source",
            "date": "Date",
            "description": "Description",
            "methods": "Data Preparation Methods",
            "citation": "Citation",
            "url": "URL",
        }
    )

    column_widths = [24, 18, 24, 8, 48, 48, 40, 40]
    write_excel(
        xlsx,
        metadata,
        sheet_name="Data details",
        caption="Details for datasets included in this analysis.",
        column_widths=column_widths,
    )

    # .to_excel(xlsx, sheet_name="Data details", index=False)
    # ws = xlsx.sheets["Data details"]
    # set_column_widths(ws, [24, 18, 24, 8, 48, 48, 40, 40])
    # set_cell_styles(ws)
    # for cell in list(ws.columns)[-1][1:]:
    #     cell.hyperlink = cell.value
    #     cell.font = Font(color=Color(index=4))
