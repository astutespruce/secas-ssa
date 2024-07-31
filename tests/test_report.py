import asyncio
from pathlib import Path
import subprocess
from time import time

from pyogrio.geopandas import read_dataframe
import shapely

from analysis.constants import DATA_CRS
from analysis.lib.geometry import dissolve, make_valid
from analysis.lib.stats.analysis_units import get_analysis_unit_results
from analysis.lib.stats.prescreen import (
    get_available_datasets,
    get_overlapping_analysis_units,
)
from api.report.xlsx import create_xlsx


### Create XLSX reports for an AOI
aois = [
    # template: {"name": "", "path": "", "field": ""},
    # {
    #     "name": "Balduina",
    #     "path": "Balduina_pop_resiliency_final",
    #     "field": "Population",
    # },
    # {
    #     "name": "Rabbitsfoot",
    #     "path": "Rabbitsfott_resilience_final_SECAS_only",
    #     "field": "HUC10",
    # },
    {
        "name": "Data_Cdan_Populations_1km_Buffer_Dissolve",
        "path": "Data_Cdan_Populations_1km_Buffer_Dissolve",
        "field": None,
        "analysis_unit_label": "Pop A",
        # "field": "POP_ID",
    },
    # {
    #     "name": "Test single area",
    #     "path": "SingleTest",
    #     "field": None,
    #     # "analysis_unit_label": "Pop A",
    #     "analysis_unit_label": 1,
    # },
    # {"name": "Lousiana COAs", "path": "Combined_COAsv1_dis", "field": "COAName"},
    # {
    #     "name": "San Juan area, PR",
    #     "path": "SanJuan",
    #     "field": None,
    #     "analysis_unit_label": 1,
    # },
    # {
    #     "name": "fl_slr_test",
    #     "path": "fl_slr_test",
    #     "field": None,
    #     "analysis_unit_label": "Test population",
    # },
    # {
    #     "name": "big_cypress",
    #     "path": "big_cypress",
    #     "field": None,
    #     "analysis_unit_label": "Test population",
    # },
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]

    # if field is missing, analysis unit column must be present and will be added
    field = aoi.get("field", None) or "__analysis_unit"
    analysis_unit_label = aoi.get("analysis_unit_label", None)

    print(f"Creating report for {name}...")

    start = time()

    columns = [field] if analysis_unit_label is None else []
    df = read_dataframe(f"examples/{path}.shp", columns=columns).to_crs(DATA_CRS)

    if analysis_unit_label is not None:
        df[field] = analysis_unit_label

    # make valid and only keep polygon parts
    df["geometry"] = make_valid(df.geometry.values)
    df = df.explode(index_parts=False)
    df = df.loc[shapely.get_type_id(df.geometry.values) == 3]

    # dissolve by analysis unit identifier
    df = dissolve(df, by=field).set_index(field)

    overlapping_df = get_overlapping_analysis_units(df)

    if len(overlapping_df) == 0:
        raise ValueError("None of the polygon boundaries overlap available datasets")

    # find available datasets
    datasets = [
        id for id, present in get_available_datasets(overlapping_df).items() if present
    ]
    # datasets = ["nlcd_inundation_freq"]

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = asyncio.run(get_analysis_unit_results(df, datasets))

    # FIXME:
    # results.reset_index().to_feather("/tmp/test.feather")

    if results is None:
        print(f"AOI: {path} does not overlap SECAS states")
        continue

    out_dir = Path("/tmp/aoi") / path
    out_dir.mkdir(exist_ok=True, parents=True)

    xlsx = create_xlsx(results, datasets)

    outfilename = out_dir / f"{path}_report.xlsx"
    with open(outfilename, "wb") as out:
        out.write(xlsx)

    print("Elapsed {:.2f}s".format(time() - start))

    subprocess.run(["open", outfilename])
