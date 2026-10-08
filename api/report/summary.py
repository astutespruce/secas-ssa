from api.report.style import CHAR_PER_WIDTH_UNIT
from api.report.writer import write_excel


def add_summary_sheet(xlsx, df, name_col_width, area_col_width, area_label, outside_extent_acres):
    pixel_col_width = max(df.pixels.apply(lambda x: len("{x:,}")).max() * CHAR_PER_WIDTH_UNIT, 12)

    cols = ["acres", "overlap_acres"]
    column_widths = [name_col_width, area_col_width, area_col_width]
    area_columns = [1, 2]
    if outside_extent_acres:
        cols.append("outside_extent_acres")
        column_widths.append(16)
        area_columns.append(3)

    cols.extend(["pixels", "count", "states"])
    column_widths.extend([pixel_col_width, 16, 20])
    # NOTE: pixels col is treated as an area col so it can be formated with commas
    area_columns.append(4 if outside_extent_acres else 3)

    df = (
        df[cols]
        .reset_index()
        .rename(
            columns={
                "acres": "GIS acres",
                "pixels": "Number of 30m pixels in analysis unit",
                "overlap_acres": area_label + " (rasterized to 30m pixels)",
                "outside_extent_acres": "Acres outside Southeast data extent (rasterized to 30m pixels)",
                "count": "Number of areas in analysis unit",
                "states": "State(s)",
            }
        )
    )

    write_excel(
        xlsx,
        df,
        sheet_name="Summary",
        caption="Summary of analysis units included in this analysis.",
        column_widths=column_widths,
        area_columns=area_columns,
    )
