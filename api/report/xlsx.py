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


from api.report.metadata import add_data_details_sheet
from api.report.slr import add_slr_inundation_sheet, add_slr_projection_sheet
from api.report.nlcd import add_ncld_landcover_sheet, add_ncld_impervious_sheet
from api.report.summary import add_summary_sheet
from api.report.se_blueprint_indicators import add_indicator_sheet
from api.report.style import CHAR_PER_WIDTH_UNIT
from api.report.urban import add_urbanization_sheet


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

        # NLCD sheets
        if "nlcd_landcover" in datasets:
            add_ncld_landcover_sheet(
                xlsx, df, name_col_width, area_col_width, area_label
            )

        if "nlcd_impervious" in datasets:
            add_ncld_impervious_sheet(
                xlsx, df, name_col_width, area_col_width, area_label
            )

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
