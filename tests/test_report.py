import asyncio
from pathlib import Path
import subprocess
from time import time

import numpy as np
import pygeos as pg
from pyogrio.geopandas import read_dataframe

from analysis.constants import DATA_CRS, DATASETS
from analysis.lib.geometry import dissolve, make_valid, to_dict_all
from analysis.lib.stats.population import get_population_results
from analysis.lib.stats.prescreen import get_available_datasets
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
        "name": "Test single area",
        "path": "SingleTest",
        "field": None,
        "population_label": "Pop A",
    },
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]

    # if field is missing, population must be present and will be added
    field = aoi.get("field", None) or "__pop"
    population_label = aoi.get("population_label", None)

    print(f"Creating report for {name}...")

    start = time()

    columns = [field] if population_label is None else []
    df = read_dataframe(f"examples/{path}.shp", columns=columns).to_crs(DATA_CRS)

    # FIXME:
    # df = df.head(2)
    # df = df.tail(15)

    if population_label is not None:
        df[field] = population_label

    # make valid and only keep polygon parts
    df["geometry"] = make_valid(df.geometry.values.data)
    df = df.explode(index_parts=False)
    df = df.loc[pg.get_type_id(df.geometry.values.data) == 3]

    # find available datasets
    datasets = [
        id
        for id, present in get_available_datasets(
            to_dict_all(df.geometry.values.data),
            pg.total_bounds(df.geometry.values.data),
        ).items()
        if present
    ]

    # dissolve by population
    df = dissolve(df, by=field).set_index(field)

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = asyncio.run(get_population_results(df, datasets))

    # FIXME:
    results.reset_index().to_feather("/tmp/test.feather")

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
