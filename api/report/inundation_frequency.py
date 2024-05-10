import pandas as pd

from analysis.constants import (
    DATASETS,
    INUNDATION_FREQUENCY,
)
from api.report.metadata import add_data_note
from api.report.style import set_cell_styles, set_column_widths


def add_nlcd_inundation_frequency_sheet(
    xlsx, df, name_col_width, area_col_width, area_label
):
    dataset_id = "nlcd_inundation_freq"
    dataset = DATASETS[dataset_id]
    sheet_name = dataset["sheet_name"]
    description = dataset["valueDescription"]

    # transform data into one row per land cover type per analysis unit
    nlcd = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.overlap > 0:
            for landcover, values in row[dataset_id].items():
                nlcd.append([id, row.overlap, landcover] + list(values))
                counter += 1
        else:
            nlcd.append([id, row.overlap])
            counter += 1

        breaks.append(counter)

    nlcd = pd.DataFrame(
        nlcd,
        columns=[df.index.name, area_label, "Land cover type"]
        + [f"{entry['label']} (acres)" for entry in INUNDATION_FREQUENCY],
    )

    nlcd.to_excel(xlsx, sheet_name=sheet_name, index=False)
    ws = xlsx.sheets[sheet_name]
    set_column_widths(
        ws, [name_col_width, area_col_width, 30] + ([20] * len(INUNDATION_FREQUENCY))
    )
    set_cell_styles(
        ws,
        breaks=breaks,
        area_columns=[1] + list(range(3, len(INUNDATION_FREQUENCY) + 4)),
    )

    add_data_note(ws, description)
