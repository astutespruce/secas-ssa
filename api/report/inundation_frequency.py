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
        if row[dataset_id]:
            outside_dataset_acres = max(row.rasterized_acres - sum([v[0] for v in row[dataset_id].values()]), 0)
            for landcover, values in row[dataset_id].items():
                inundation_frequency.append([id, row.rasterized_acres, outside_dataset_acres, landcover] + list(values))
                counter += 1
        else:
            inundation_frequency.append(
                [id, row.rasterized_acres, row.rasterized_acres, ""] + [""] * len(INUNDATION_FREQUENCY)
            )
            counter += 1

        breaks.append(counter)

    inundation_frequency = pd.DataFrame(
        inundation_frequency,
        columns=[df.index.name, area_label, "outside_dataset_acres", "Land cover type"]
        + [f"{entry['label']}\n(acres)" for entry in INUNDATION_FREQUENCY],
    )

    num_left_area_columns = 2
    has_area_outside_dataset = inundation_frequency.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        inundation_frequency = inundation_frequency.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    inundation_frequency = inundation_frequency.rename(
        columns={"outside_dataset_acres": "Area outside extent of this dataset\n(acres)"}
    )

    column_widths = (
        [name_col_width] + [area_col_width] * num_left_area_columns + [30] + ([20] * len(INUNDATION_FREQUENCY))
    )
    area_columns = list(range(1, num_left_area_columns + 1)) + list(range(3, len(INUNDATION_FREQUENCY) + 4))
    write_excel(
        xlsx,
        inundation_frequency,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )
