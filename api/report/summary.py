from api.report.style import set_cell_styles, set_column_widths, CHAR_PER_WIDTH_UNIT


def add_summary_sheet(xlsx, df, name_col_width, area_col_width, area_label, outside_se):
    sheet_name = "Summary"

    pixel_col_width = max(
        df.pixels.apply(lambda x: len("{x:,}")).max() * CHAR_PER_WIDTH_UNIT, 12
    )

    cols = ["acres", "overlap"]
    col_widths = [name_col_width, area_col_width, area_col_width]
    area_columns = [1, 2]
    if outside_se:
        cols.append("outside_se")
        col_widths.append(16)
        area_columns.append(3)

    cols.extend(["pixels", "count", "states"])
    col_widths.extend([pixel_col_width, 16, 20])
    # NOTE: pixels col is treated as an area col so it can be formated with commas
    area_columns.append(4 if outside_se else 3)

    df[cols].reset_index().rename(
        columns={
            "acres": "GIS acres",
            "pixels": "Number of 30m pixels in analysis unit",
            "overlap": area_label + " (rasterized to 30m pixels)",
            "outside_se": "Acres outside Southeast data extent (rasterized to 30m pixels)",
            "count": "Number of areas in analysis unit",
            "states": "State(s)",
        }
    ).to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_cell_styles(ws, area_columns=area_columns)
    set_column_widths(ws, col_widths)
