import numpy as np
import pandas as pd

from analysis.constants import DATASETS, INUNDATION_FREQUENCY
from api.report.writer import write_excel

value_columns = [f"{entry['label']}\n(acres)" for entry in INUNDATION_FREQUENCY]


def add_nlcd_inundation_frequency_sheet(xlsx, df, name_col_width, area_col_width, area_label):
    dataset_id = "nlcd_inundation_freq"
    dataset = DATASETS[dataset_id]

    inundation_frequency = (
        df[["rasterized_acres"]]
        .join(
            df.nlcd_inundation_freq.apply(pd.Series)
            .melt(var_name="label", value_name="acres", ignore_index=False)
            .dropna(subset="acres")
        )
        .set_index("label", append=True)
    )
    inundation_frequency = inundation_frequency.astype(object)
    ix = inundation_frequency.acres.isnull()
    inundation_frequency.loc[ix, "acres"] = inundation_frequency.loc[ix].acres.apply(lambda x: [0] * len(value_columns))
    acres = pd.DataFrame(inundation_frequency.acres.tolist(), index=inundation_frequency.index, columns=value_columns)
    inundation_frequency = inundation_frequency.drop(columns=["acres"]).join(acres).reset_index(level=-1)

    inundation_frequency = inundation_frequency.join(
        inundation_frequency.groupby(level=0)[value_columns].sum().sum(axis=1).rename("total_acres")
    )
    inundation_frequency["label"] = inundation_frequency.label.fillna("")

    # use first year to calculate nodata
    inundation_frequency["outside_dataset_acres"] = (
        inundation_frequency.rasterized_acres - inundation_frequency.total_acres
    )
    inundation_frequency.loc[inundation_frequency.outside_dataset_acres < 1e-6, "outside_dataset_acres"] = 0

    breaks = np.arange(1, len(inundation_frequency))[
        inundation_frequency.index[1:] != inundation_frequency.index[:-1]
    ].tolist()

    inundation_frequency = inundation_frequency[
        ["rasterized_acres", "outside_dataset_acres", "label"] + value_columns
    ].reset_index()

    num_left_area_columns = 2
    has_area_outside_dataset = inundation_frequency.outside_dataset_acres.max() > 1e-2
    if not has_area_outside_dataset:
        inundation_frequency = inundation_frequency.drop(columns=["outside_dataset_acres"])
        num_left_area_columns -= 1

    inundation_frequency = inundation_frequency.rename(
        columns={
            "rasterized_acres": area_label,
            "outside_dataset_acres": "Area outside extent of this dataset\n(acres)",
            "label": "Land cover type",
        }
    )

    column_widths = [name_col_width] + [area_col_width] * num_left_area_columns + [30] + ([20] * len(value_columns))

    area_columns = list(range(1, num_left_area_columns + 1)) + list(
        range(1 + num_left_area_columns + 1, len(value_columns) + num_left_area_columns + 3)
    )

    write_excel(
        xlsx,
        inundation_frequency,
        sheet_name=dataset["sheet_name"],
        caption=f"{dataset['name']}.\n{dataset['valueDescription']}",
        column_widths=column_widths,
        area_columns=area_columns,
        breaks=breaks,
    )
