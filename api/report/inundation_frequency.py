import pandas as pd

from analysis.constants import DATASETS, INUNDATION_FREQUENCY
from api.report.writer import write_excel


def add_nlcd_inundation_frequency_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset_id = "nlcd_inundation_freq"
    dataset = DATASETS[dataset_id]

    # transform data into one row per land cover type per analysis unit
    inundation_frequency = []
    breaks = []
    counter = 0
    for id, row in df.iterrows():
        if row.overlap_acres > 0:
            for landcover, values in row[dataset_id].items():
                inundation_frequency.append([id, row.overlap_acres, landcover] + list(values))
                counter += 1
        else:
            inundation_frequency.append([id, row.overlap_acres])
            counter += 1

        breaks.append(counter)

    inundation_frequency = pd.DataFrame(
        inundation_frequency,
        columns=[df.index.name, area_label, "Land cover type"]
        + [f"{entry['label']} (acres)" for entry in INUNDATION_FREQUENCY],
    )

    column_widths = [name_col_width, area_col_width, 30] + ([20] * len(INUNDATION_FREQUENCY))
    area_columns = [1] + list(range(3, len(INUNDATION_FREQUENCY) + 4))
    write_excel(
        xlsx,
        inundation_frequency,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )
