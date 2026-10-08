from math import ceil

from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    NamedStyle,
    PatternFill,
    Side,
)
from openpyxl.utils.cell import get_column_letter

# Guess at how many characters fit into a column width measurement
CHAR_PER_WIDTH_UNIT = 1.7

### Create named styles for formatting cells
font_bold = Font(bold=True)

alignment_left_wrap = Alignment(horizontal="left", wrap_text=True)
alignment_center_wrap = Alignment(horizontal="center", wrap_text=True)

default_header_border = Border(
    top=Side(border_style="medium", color="000000"),
    bottom=Side(border_style="medium", color="000000"),
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

table_caption_style = NamedStyle(
    name="Table Header Style",
    font=Font(italic=True),
    alignment=Alignment(vertical="top", horizontal="left", wrap_text=True),
)

value_style = NamedStyle(name="Value Style", alignment=alignment_left_wrap)

analysis_unit_divider = Border(
    bottom=Side(border_style="medium", color="AAAAAA"),
    left=Side(border_style="thin", color="DDDDDD"),
    right=Side(border_style="thin", color="DDDDDD"),
)

description_font = Font(color="999999")


def add_caption(ws, table_counter, caption):
    """Add a table caption in the first cell of the table, and merge all cells
    of that row together.

    Parameters
    ----------
    ws : Worksheet
    table_counter : int
    caption : str
    """

    cell = ws["A1"]
    cell.value = f"Table {table_counter}: {caption}"
    cell.style = table_caption_style

    end_col = get_column_letter(ws.max_column)
    ws.merge_cells(f"A1:{end_col}1")

    # Excel does not auto-calculate the height properly for merged cells with wrapping
    # so we calculate the height based on the approx number of lines of text for the width
    width = sum(ws.column_dimensions[get_column_letter(i)].width for i in range(1, ws.max_column + 1))
    chars_per_line = width * CHAR_PER_WIDTH_UNIT
    total_line_height = sum([max(1, ceil(len(line) / chars_per_line)) * 16 for line in caption.split("\n")])
    # default is height 20, but extend up to 16 units per line of text
    ws.row_dimensions[1].height = max(20, total_line_height)
