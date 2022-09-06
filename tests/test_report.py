import os
from pathlib import Path
from time import time

import numpy as np
import pygeos as pg
from pyogrio.geopandas import read_dataframe

from analysis.constants import DATA_CRS, M2_ACRES
from analysis.lib.geometry import dissolve, explode, make_valid
from analysis.lib.stats.population import get_results


### Create XLSX reports for an AOI
aois = [
    # template: {"name": "", "path": "", "field": ""},
    {
        "name": "Balduina",
        "path": "Balduina_pop_resiliency_final",
        "field": "Population",
    },
    # {
    #     "name": "Rabbitsfoot",
    #     "path": "Rabbitsfott_resilience_final_SECAS_only",
    #     "field": "HUC10",
    # },
    # {
    #     "name": "Test single area",
    #     "path": "SingleTest",
    #     "field": None,
    #     "population": "Pop A",
    # },
]


for aoi in aois:
    name = aoi["name"]
    path = aoi["path"]
    # if field is misisng, population must be present and will be added
    field = aoi.get("field", "__pop")
    population = aoi.get("population", None)

    print(f"Creating report for {name}...")

    start = time()

    columns = [field] if population is None else []
    df = read_dataframe(f"examples/{path}.shp", columns=columns).to_crs(DATA_CRS)
    if population is not None:
        df[field] = population

    # make valid and only keep polygon parts
    df["geometry"] = make_valid(df.geometry.values.data)
    df = explode(df)
    df = df.loc[pg.get_type_id(df.geometry.values.data) == 3]

    # dissolve by population
    df = dissolve(df, by=field).set_index(field)

    ### calculate results, data must be in DATA_CRS
    print("Calculating results...")
    results = get_results(df)

    if results is None:
        print(f"AOI: {path} does not overlap SECAS states")
        continue

    out_dir = Path("/tmp/aoi") / path
    if not out_dir.exists():
        os.makedirs(out_dir)

    xlsx = create_xlsx(results=results)

    with open(out_dir / f"{path}_report.pdf", "wb") as out:
        out.write(pdf)

    print("Elapsed {:.2f}s".format(time() - start))
