from io import BytesIO
from copy import copy

import numpy as np
import pandas as pd
from openpyxl.styles import (
    Alignment,
    Font,
    NamedStyle,
    Border,
    Side,
    PatternFill,
    Color,
)
from openpyxl.utils.cell import get_column_letter

from analysis.constants import (
    DATASETS,
    NLCD_YEARS,
    URBAN_YEARS,
    SLR_DEPTHS,
    SLR_YEARS,
)

# Guess at how many characters fit into a column width measurement
CHAR_PER_WIDTH_UNIT = 1.7

### Create named styles for formatting cells
font_bold = Font(bold=True)


alignment_left_wrap = Alignment(horizontal="left", wrap_text=True)
alignment_center_wrap = Alignment(horizontal="center", wrap_text=True)

default_header_border = Border(
    bottom=Side(border_style="medium", color="000000"),
)
default_cell_border = Border(
    bottom=Side(border_style="thin", color="AAAAAA"),
    left=Side(border_style="thin", color="DDDDDD"),
    right=Side(border_style="thin", color="DDDDDD"),
)

# Note: all cells are setup to wrap text
left_header_style = NamedStyle(
    name="Left Header Style",
    font=font_bold,
    alignment=alignment_left_wrap,
    border=default_header_border,
)

center_header_style = NamedStyle(
    name="Center Header Style",
    font=font_bold,
    alignment=alignment_center_wrap,
    border=default_header_border,
)

value_style = NamedStyle(
    name="Value Style",
    alignment=alignment_left_wrap,
    border=default_cell_border,
)

even_row_bg = PatternFill("solid", fgColor="00F6F6F6")

population_divider = Border(
    bottom=Side(border_style="medium", color="AAAAAA"),
    left=Side(border_style="thin", color="DDDDDD"),
    right=Side(border_style="thin", color="DDDDDD"),
)

description_font = Font(color="999999")


def set_cell_styles(ws, breaks=None, area_columns=None, percent_columns=None):
    area_columns = area_columns or []
    percent_columns = percent_columns or []

    for col_idx, col in enumerate(ws.columns):
        col[0].style = center_header_style

        for i, cell in enumerate(col[1:]):
            cell.style = value_style
            value = cell.value
            is_int = isinstance(value, (float, int)) and int(value) == value

            if col_idx in area_columns:
                if is_int:
                    cell.number_format = "#,##0"
                else:
                    cell.number_format = "#,##0.00"
            elif col_idx in percent_columns:
                if is_int:
                    cell.number_format = "0%"
                else:
                    cell.number_format = "0.00%"

            if i % 2 == 1:
                cell.fill = even_row_bg

    ws["A1"].style = left_header_style

    if breaks is not None:
        # add a stronger line between populations
        for col in ws.columns:
            for line in breaks:
                col[line].border = population_divider


def set_column_widths(ws, widths):
    for i, width in enumerate(widths):
        letter = get_column_letter(i + 1)
        ws.column_dimensions[letter].width = width


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


def add_summary_sheet(xlsx, df, name_col_width, area_col_width, area_label, outside_se):
    sheet_name = "Summary"

    cols = ["acres", "overlap"]
    col_widths = [name_col_width, area_col_width, area_col_width]
    area_columns = [1, 2]
    if outside_se:
        cols.append("outside_se")
        col_widths.append(16)
        area_columns.append(3)

    cols.extend(["count", "states"])
    col_widths.extend([16, 20])

    df[cols].reset_index().rename(
        columns={
            "acres": "GIS acres",
            "overlap": area_label + " (rasterized to 30m pixels)",
            "outside_se": "Acres outside Southeast data extent (rasterized to 30m pixels)",
            "count": "Number of areas in population unit",
            "states": "State(s)",
        }
    ).to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_cell_styles(ws, area_columns=area_columns)
    set_column_widths(ws, col_widths)


def add_ncld_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["nlcd"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    # transform data into one row per land cover type per population
    nlcd = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        for landcover, values in row.nlcd.items():
            # convert to proportion, displayed as percent
            nlcd.append(
                [id, row.overlap, landcover] + list((np.asarray(values) / row.overlap))
            )

            counter += 1
        breaks.append(counter)

    nlcd = pd.DataFrame(
        nlcd,
        columns=[df.index.name, area_label, "Land cover type"] + NLCD_YEARS,
    )

    nlcd.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 30] + ([8] * len(NLCD_YEARS))
    )
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1],
        percent_columns=list(range(3, len(NLCD_YEARS) + 4)),
    )

    add_data_note(ws, description)


def add_urbanization_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["urban"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    # transform data into one row for high and low urbanization per population
    years = [2019] + URBAN_YEARS
    urban = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        for level in ["low", "high"]:
            values = row["urban"][level]
            urban.append(
                [id, row.overlap, level.capitalize()]
                + list((np.asarray(values) / row.overlap))
            )

            counter += 1
        breaks.append(counter)

    urban = pd.DataFrame(
        urban,
        columns=[df.index.name, area_label, "Urbanization level"] + years,
    )

    urban.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width, 10] + ([10] * len(years)))
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1],
        percent_columns=list(range(3, len(years) + 4)),
    )
    add_data_note(ws, description)


def add_slr_projection_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["slr_proj"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    # transform data into one row per SLR scenario per population
    slr = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.slr_proj is None:
            slr.append([id, row.overlap, "no"] + [""] * (len(SLR_YEARS) + 1))
            counter += 1
        else:
            for scenario, values in row.slr_proj.items():
                slr.append([id, row.overlap, "yes", scenario] + list(values))

                counter += 1
        breaks.append(counter)

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label, "Has projected SLR?", "SLR scenario"]
        + [f"{year} (ft)" for year in SLR_YEARS],
    )

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 10, 18] + ([8] * len(SLR_YEARS))
    )
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1],
    )

    add_data_note(ws, description)


def add_slr_inundation_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset = DATASETS["slr_depth"]
    sheet_name = dataset["sheet_name"]
    description = dataset["description"]

    slr = []
    for id, row in df.iterrows():
        if row.slr_depth is None:
            slr.append([id, row.overlap, "no"] + [""] * len(SLR_DEPTHS))
        else:
            # calculate proportion
            slr.append(
                [id, row.overlap, "yes"] + list(np.array(row.slr_depth) / row.overlap)
            )

    slr = pd.DataFrame(
        slr,
        columns=[df.index.name, area_label, "Has SLR up to 10ft?"]
        + [f"Inundated at {depth} feet" for depth in SLR_DEPTHS],
    )

    slr.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 10] + ([10] * len(SLR_DEPTHS))
    )
    set_cell_styles(
        ws, area_columns=[1], percent_columns=list(range(3, len(SLR_DEPTHS) + 4))
    )
    add_data_note(ws, description)


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

    columns = [v["label"] for v in values]
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

    # convert to percent
    cols = [c for c in tmp.columns if not c == "overlap"]
    for col in cols:
        tmp[col] = tmp[col].values / tmp.overlap.values

    tmp.rename(
        columns={"overlap": area_label, "outside": nodata_label}
    ).reset_index().to_excel(xlsx, sheet_name=sheet_name, index=False)

    ws = xlsx.sheets[sheet_name]
    set_column_widths(ws, [name_col_width, area_col_width] + ([col_width] * len(cols)))
    set_cell_styles(ws, area_columns=[1], percent_columns=list(range(2, len(cols) + 3)))
    add_data_note(ws, description)


def add_data_details_sheet(xlsx, datasets):
    pd.DataFrame([DATASETS[dataset] for dataset in datasets])[
        [
            "name",
            "sheet_name",
            "source",
            "date",
            "description",
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
            "citation": "Citation",
            "url": "URL",
        }
    ).to_excel(
        xlsx, sheet_name="Data details", index=False
    )
    ws = xlsx.sheets["Data details"]
    set_column_widths(ws, [16, 16, 18, 8, 48, 32, 40])
    set_cell_styles(ws)
    for cell in list(ws.columns)[-1][1:]:
        cell.hyperlink = cell.value
        cell.font = Font(color=Color(index=4))


def create_xlsx(df, datasets):
    df.index.name = "Population unit"
    outside_se = df.outside_se.sum() > 1e-2

    name_col_width = max(
        min(pd.Series(df.index).apply(len).max() * CHAR_PER_WIDTH_UNIT, 28), 14
    )
    area_col_width = max(
        df.overlap.astype("str").apply(len).max() * CHAR_PER_WIDTH_UNIT, 10
    )

    area_label = (
        "Acres within Southeast data extent" if outside_se else "Analysis acres"
    )

    ### Create XLSX file and write to memory buffer
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as xlsx:

        # Summary sheet
        add_summary_sheet(
            xlsx, df, name_col_width, area_col_width, area_label, outside_se
        )

        # NLCD sheet
        if "nlcd" in datasets:
            add_ncld_sheet(xlsx, df, name_col_width, area_col_width, area_label)

        # Urbanization sheet
        if "urban" in datasets:
            add_urbanization_sheet(xlsx, df, name_col_width, area_col_width, area_label)

        # SLR projection sheet
        if "slr_proj" in datasets:
            add_slr_projection_sheet(
                xlsx, df, name_col_width, area_col_width, area_label
            )

        # SLR inundation sheet
        if "slr_depth" in datasets:
            add_slr_inundation_sheet(
                xlsx, df, name_col_width, area_col_width, area_label
            )

        se_blueprint_indicators = [
            dataset for dataset in datasets if dataset.startswith("se_blueprint")
        ]
        for dataset in se_blueprint_indicators:
            add_indicator_sheet(
                xlsx, df, dataset, name_col_width, area_col_width, area_label
            )

        # Data details sheet
        add_data_details_sheet(xlsx, datasets)

    # rewind buffer and read data
    buffer.seek(0)
    xlsx_data = buffer.read()

    return xlsx_data
