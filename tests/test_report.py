import os
import shutil
from io import BytesIO

import numpy as np
import pandas as pd
import pytest
from dotenv import load_dotenv
from pyogrio.geopandas import read_dataframe

from analysis.constants import DATA_CRS, DATASETS
from analysis.lib.geometry import dissolve
from analysis.lib.stats.analysis_units import get_analysis_unit_results
from analysis.lib.stats.prescreen import get_available_datasets
from api.errors import DataError
from api.logger import log
from api.report.nlcd import value_columns as nlcd_value_columns
from api.report.slr import depth_value_columns as slr_depth_value_columns
from api.report.slr import proj_value_columns as slr_proj_value_columns
from api.report.urban import value_columns as urban_value_columns
from api.report.xlsx import create_xlsx
from api.settings import TEMP_DIR
from api.tasks.report import get_report_inputs

load_dotenv()

# add to .env file to name saving test files
SAVE_XLSX = bool(os.getenv("TEST_SAVE_XLSX", False))


# mock redis context for set progress
class MockRedis(object):
    async def setex(self, prefix, expiration, message):
        log.info(f"{prefix}: {message}")


mock_ctx = {"redis": MockRedis(), "job_id": 123}


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_single_area(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)

    assert len(datasets) == 15

    # just some of the expected datasets
    expected_datasets = [
        "landfire_evt",
        "nlcd_impervious",
        "nlcd_inundation_freq",
        "nlcd_landcover",
        "protected_areas",
        "sarp_aquatic_barriers",
        "sarp_aquatic_network_alteration",
        "se_blueprint_firefrequency",
        "se_blueprint_resilientterrestrialsites",
        "slr_depth",
        "slr_proj",
        "urban",
    ]
    for dataset in expected_datasets:
        assert dataset in datasets

    # does not overlap with Caribbean, so there should be no associated indicators
    unexpected_datasets = [dataset for dataset in DATASETS.keys() if "caribbean" in dataset]
    for dataset in unexpected_datasets:
        assert dataset not in datasets


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_no_overlap(format):
    filename = f"{format}_poly_no_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)

    assert len(datasets) == 0


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_multiple_areas_partial_overlap(format):
    # just a test that this runs, not checking specific ones
    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)

    assert len(datasets) == 15


@pytest.mark.parametrize("format", ["shp", "gdb"])
def test_get_available_datasets_multiple_areas(format):
    # just a test that this runs, not checking specific ones
    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)

    assert len(datasets) == 20


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_report_inputs_single_area(format):
    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    uuid = "123"

    tmp_filename = TEMP_DIR / filename
    shutil.copy(f"tests/fixtures/{filename}", tmp_filename)

    result, errors = await get_report_inputs(mock_ctx, tmp_filename, dataset, layer="poly_small", uuid=uuid)

    assert len(errors) == 0

    payload = result["payload"]
    assert payload["uuid"] == uuid
    assert payload["count"] == 1
    assert payload["fields"] == {"ID": 1, "Name": 1}

    datasets = payload["datasets"]
    assert len(datasets) == 15

    # just some of the expected datasets
    expected_datasets = [
        "landfire_evt",
        "nlcd_landcover",
        "protected_areas",
        "sarp_aquatic_barriers",
        "slr_depth",
    ]
    for dataset in expected_datasets:
        assert dataset in datasets

    # does not overlap with Caribbean, so there should be no associated indicators
    unexpected_datasets = [dataset for dataset in DATASETS.keys() if "caribbean" in dataset]
    for dataset in unexpected_datasets:
        assert dataset not in datasets


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_report_inputs_no_overlap(format):
    filename = f"{format}_poly_no_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    uuid = "123"

    tmp_filename = TEMP_DIR / filename
    shutil.copy(f"tests/fixtures/{filename}", tmp_filename)

    with pytest.raises(
        DataError,
        match="area of interest does not overlap any of the available datasets",
    ):
        await get_report_inputs(
            mock_ctx,
            tmp_filename,
            dataset,
            layer="poly_no_overlap",
            uuid=uuid,
        )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_report_inputs_multiple_areas_partial_overlap(format):
    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    uuid = "123"

    tmp_filename = TEMP_DIR / filename
    shutil.copy(f"tests/fixtures/{filename}", tmp_filename)

    result, errors = await get_report_inputs(
        mock_ctx,
        tmp_filename,
        dataset,
        layer="poly_multiple_partial_overlap",
        uuid=uuid,
    )

    assert len(errors) == 0

    payload = result["payload"]
    assert payload["uuid"] == uuid
    assert payload["count"] == 3
    assert payload["fields"] == {"ID": 3, "Name": 3, "Blueprint": 3, "Common": 1}

    datasets = payload["datasets"]
    assert len(datasets) == 15


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_report_inputs_multiple_areas(format):
    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    uuid = "123"

    tmp_filename = TEMP_DIR / filename
    shutil.copy(f"tests/fixtures/{filename}", tmp_filename)

    result, errors = await get_report_inputs(
        mock_ctx,
        tmp_filename,
        dataset,
        layer="poly_multiple",
        uuid=uuid,
    )

    assert len(errors) == 0

    payload = result["payload"]
    assert payload["uuid"] == uuid
    assert payload["count"] == 5
    assert payload["fields"] == {"ID": 5, "Name": 5, "Region": 3, "Common": 1}

    datasets = payload["datasets"]
    assert len(datasets) == 20


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_single_area(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)

    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "count", "acres", "rasterized_acres"]:
        assert col in results.columns

    row = results.iloc[0]

    assert row.states == "Alabama"
    assert row["count"] == 1
    assert np.isclose(row.acres, 51.026)

    assert np.isclose(row.rasterized_acres, 50.9283)

    # Landfire EVT is stored as a dict of indexes and acres
    assert list(row.landfire_evt.keys()) == [656, 658, 706, 714]
    assert np.allclose(list(row.landfire_evt.values()), [3.1135, 0.6672, 36.2503, 10.8973], atol=1e-4)

    # NLCD landcover is stored as a dict of arrays
    assert list(row.nlcd_landcover.keys()) == ["Deciduous forest", "Evergreen forest", "Mixed forest"]
    assert np.allclose(row.nlcd_landcover["Deciduous forest"], [48.4820, 49.1492, 49.1492, 49.1492, 49.1492], atol=1e-4)

    assert len(row.protected_areas) == 1
    assert row.protected_areas[0]["name"] == "Talladega National Forest"
    assert row.protected_areas[0]["owner"] == "USDA Forest Service"
    assert row.protected_areas[0]["gap_status"] == "3"
    assert np.isclose(row.protected_areas[0]["acres"], 34.5465)

    assert len(row.slr_depth) == 14
    assert np.allclose(row.slr_depth, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, row.rasterized_acres, 0])

    assert list(row.urban.keys()) == ["high", "low"]
    assert np.allclose(row.urban["high"], [0, 0, 0, 0, 0, 0, 0, 0, 0, row.rasterized_acres, 0])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas_partial_overlap(format):
    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    datasets = get_available_datasets(df)

    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "count", "acres", "rasterized_acres"]:
        assert col in results.columns

    assert results.states.fillna("").values.tolist() == ["North Carolina", "Minnesota", "Missouri"]

    assert results["count"].values.tolist() == [1] * 3
    assert np.allclose(results["acres"], [280.4020, 394.7394, 68.8730])
    assert np.allclose(results["rasterized_acres"], [279.9947, 396.7518, 69.8319])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas_partial_overlap_dissolved(
    format,
):
    # NOTE: this is just a smoke test to ensure it runs without failure

    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    df = dissolve(df.explode(ignore_index=True))

    datasets = get_available_datasets(df)
    results = await get_analysis_unit_results(df, datasets)

    assert results["count"].values.tolist() == [3]

    assert np.allclose(results["acres"], [744.0144])
    assert np.allclose(results["rasterized_acres"], [746.5783])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas(format):
    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    datasets = set(get_available_datasets(df))
    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "count", "acres", "rasterized_acres"]:
        assert col in results.columns

    assert results.states.fillna("").values.tolist() == ["Georgia", "Florida", "Mississippi", "Puerto Rico", ""]
    assert results["count"].values.tolist() == [1] * 5
    assert np.allclose(results["acres"], [313.13876187, 40.55673456, 99.02771972, 147.19913421, 5386.09794185])
    assert np.allclose(results["rasterized_acres"].tolist(), [312.6867, 41.1430, 99.1879, 147.2252, 5386.8396])

    ga_poly = results.iloc[0]
    fl_poly = results.iloc[1]
    pr_poly = results.iloc[3]
    marine_poly = results.iloc[4]

    fl_protected_areas_poly = fl_poly.protected_areas
    assert len(fl_protected_areas_poly) == 3
    assert fl_protected_areas_poly[0]["name"] == "Crystal River Preserve State Park"
    assert np.isclose(fl_protected_areas_poly[0]["acres"], 27.801745)

    assert np.allclose(
        fl_poly.slr_depth,
        [25.5754, 39.3638, 41.1430, 41.1430, 41.1430, 41.1430, 41.1430, 41.1430, 41.1430, 41.1430, 41.1430, 0, 0, 0],
    )

    assert np.allclose(pr_poly.slr_depth, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, pr_poly.rasterized_acres, 0, 0])

    pr_slr_proj = pr_poly.slr_proj
    assert len(pr_slr_proj) == 5
    assert pr_slr_proj[0]["scenario"] == "l"

    assert np.allclose(
        pr_slr_proj[0]["values"], [0.2625, 0.4921, 0.8202, 1.3123, 2.0669, 3.0512, 4.1995, 5.4462, 6.7913], atol=1e4
    )

    assert np.allclose(
        ga_poly.urban["low"],
        [22.9066, 22.9066, 22.9066, 22.9066, 22.9066, 22.9066, 22.9066, 22.9066, 22.9066, 289.7800, 0],
    )
    assert np.allclose(
        ga_poly.urban["high"],
        [22.9066, 23.1602, 24.1743, 24.3211, 25.5754, 26.7051, 27.2834, 27.5903, 28.0217, 284.6650, 0],
    )

    assert np.allclose(fl_poly.urban["high"], [0] * 9 + [fl_poly.rasterized_acres] + [0])
    assert np.allclose(pr_poly.urban["high"], [0] * 10 + [pr_poly.rasterized_acres])
    assert np.allclose(marine_poly.urban["high"], [0] * 10 + [marine_poly.rasterized_acres])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp"])
async def test_get_analysis_unit_results_west_coast(format):
    filename = f"{format}_poly_west_coast.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    datasets = get_available_datasets(df)

    unexpected_datasets = ["slr_depth", "slr_proj"]
    for dataset in unexpected_datasets:
        assert dataset not in datasets

    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in ["states", "count", "acres", "rasterized_acres"]:
        assert col in results.columns

    row = results.iloc[0]

    assert row.states == "California"
    assert row["count"] == 1
    assert np.isclose(row.acres, 5294.93)
    assert np.isclose(row.pixels, 23853)
    assert np.isclose(row.rasterized_acres, 5304.78)

    # Landfire EVT is stored as a dict of indexes and acres
    assert len(row.landfire_evt.keys()) == 30
    assert list(row.landfire_evt.keys())[:4] == [56, 58, 62, 67]
    assert np.allclose(list(row.landfire_evt.values())[:4], [7.1166, 1982.4246, 2.8911, 60.4913], atol=1e-4)

    # NLCD landcover is stored as a dict of arrays
    assert list(row.nlcd_landcover.keys()) == [
        "Open water",
        "Developed (open space)",
        "Developed (low intensity)",
        "Developed (medium intensity)",
        "Developed (high intensity)",
        "Barren land",
        "Deciduous forest",
        "Evergreen forest",
        "Mixed forest",
        "Shrub/scrub",
        "Grassland/herbaceous",
        "Pasture/hay",
        "Cultivated crops",
        "Woody wetlands",
        "Emergent herbaceous wetlands",
    ]
    assert np.allclose(
        row.nlcd_landcover["Evergreen forest"], [2699.202, 2626.0343, 2559.9831, 2620.252, 2588.2272], atol=1e-4
    )

    assert len(row.protected_areas) == 10
    assert (
        row.protected_areas[0]["name"]
        == "Agricultural Conservation Easement Program - Wetland Reserve Easements (ACEP-WRE), Humboldt, CA"
    )
    assert row.protected_areas[0]["owner"] == ""
    assert row.protected_areas[0]["gap_status"] == "2"
    assert np.isclose(row.protected_areas[0]["acres"], 12.8445)

    assert list(row.urban.keys()) == ["high", "low"]
    assert np.allclose(
        row.urban["high"],
        [909.5935, 909.718, 909.718, 909.718, 909.718, 909.718, 909.718, 909.718, 909.718, 4395.058, 0],
    )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_create_xlsx_file_single_area(format):
    filename = f"{format}_poly_small.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)

    # dissolve like API endpoint
    field = "__analysis_unit"
    df[field] = "all areas"
    df = dissolve(df.explode(ignore_index=True), by=field).set_index(field)

    # representative sample of datasets
    datasets = [
        "landfire_evt",
        "nlcd_impervious",
        "nlcd_inundation_freq",
        "nlcd_landcover",
        "protected_areas",
        "sarp_aquatic_barriers",
        "sarp_aquatic_network_alteration",
        "se_blueprint_firefrequency",
        "se_blueprint_resilientterrestrialsites",
        "slr_depth",
        "slr_proj",
        "urban",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_xlsx(results, datasets)

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_single_area.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 2
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results["pixels"])
    assert np.allclose(summary["Number of areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["name"] for id, d in DATASETS.items() if id in datasets]

    # skip caption at end
    landfire_evt = reader.parse(sheet_name="LANDFIRE EVT", skiprows=2)
    assert len(landfire_evt) == 4
    assert landfire_evt.columns.tolist() == [
        "Analysis unit",
        "Analysis area\n(acres)",
        "Acres",
        "Existing Vegetation Type",
        "Group",
    ]
    assert landfire_evt["Existing Vegetation Type"].tolist() == [
        "Southeastern Interior Longleaf Pine Woodland",
        "Southeastern Native Ruderal Forest",
        "Southern Piedmont Dry Oak Forest",
        "Southern Piedmont Mesic Forest",
    ]
    assert landfire_evt["Group"].tolist() == [
        "Longleaf Pine Woodland",
        "Introduced Upland Vegetation-Treed",
        "Chestnut Oak-Virginia Pine Forest and Woodland",
        "White Oak-Beech Forest and Woodland",
    ]
    assert np.allclose(landfire_evt["Acres"], list(results.iloc[0].landfire_evt.values()))

    nlcd_landcover = reader.parse(sheet_name="Landcover trends", skiprows=2)
    assert (
        nlcd_landcover.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Land cover type"] + nlcd_value_columns
    )
    assert nlcd_landcover["Land cover type"].tolist() == list(results.nlcd_landcover.iloc[0].keys())

    for i, landcover_type in enumerate(nlcd_landcover["Land cover type"].values):
        assert np.allclose(
            nlcd_landcover[nlcd_value_columns].iloc[i].values, results.nlcd_landcover.iloc[0][landcover_type], atol=1e-4
        )

    slr_depth = reader.parse(sheet_name="SLR inundation area", skiprows=2)
    # only nodata is areas outside counties
    slr_depth_col_ix = list(range(11)) + [12]
    slr_value_cols = np.array(slr_depth_value_columns).take(slr_depth_col_ix).tolist()
    assert (
        slr_depth.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Area outside extent of this dataset\n(acres)"] + slr_value_cols
    )
    assert np.allclose(
        slr_depth[slr_value_cols].iloc[0].values,
        results.slr_depth.iloc[0].take(list(range(0, 11)) + [12]),
    )

    slr_proj = reader.parse(sheet_name="Projected SLR", skiprows=2)

    assert slr_proj.columns.tolist() == ["Analysis unit"] + slr_proj_value_columns
    assert slr_proj.iloc[0]["Has projected SLR?"] == "no"

    urban = reader.parse(sheet_name="Urbanization", skiprows=2)
    assert (
        urban.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Urbanization level"] + urban_value_columns
    )
    assert urban["Urbanization level"].tolist() == ["Low", "High"]
    for i, level in enumerate(urban["Urbanization level"].values):
        # last column is nodata, omitted here
        assert np.allclose(urban[urban_value_columns].iloc[i].values, results.urban.iloc[0][level.lower()][:-1])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_create_xlsx_file_multiple_areas_partial_overlap(format):
    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = (
        read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=["Blueprint"], use_arrow=True)
        .to_crs(DATA_CRS)
        .set_index("Blueprint")
    )

    # representative sample of datasets
    datasets = [
        "landfire_evt",
        "nlcd_impervious",
        "nlcd_inundation_freq",
        "nlcd_landcover",
        "protected_areas",
        "sarp_aquatic_barriers",
        "sarp_aquatic_network_alteration",
        "se_blueprint_firefrequency",
        "se_blueprint_resilientterrestrialsites",
        "slr_depth",
        "slr_proj",
        "urban",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_xlsx(results, datasets)

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_multiple_areas_partial_overlap.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 2
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results.pixels)
    assert np.allclose(summary["Number of areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["name"] for id, d in DATASETS.items() if id in datasets]

    slr_depth = reader.parse(sheet_name="SLR inundation area", skiprows=2)
    slr_depth_col_ix = list(range(11)) + [12]
    slr_value_cols = np.array(slr_depth_value_columns).take(slr_depth_col_ix).tolist()
    assert (
        slr_depth.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Area outside extent of this dataset\n(acres)"] + slr_value_cols
    )
    assert np.allclose(
        slr_depth[slr_value_cols].iloc[0].values,
        results.slr_depth.iloc[0].take(slr_depth_col_ix),
    )

    slr_proj = reader.parse(sheet_name="Projected SLR", skiprows=2)
    assert slr_proj.columns.tolist() == ["Analysis unit"] + slr_proj_value_columns
    assert slr_proj["Has projected SLR?"].iloc[:3].tolist() == ["no"] * 3

    urban = reader.parse(sheet_name="Urbanization", skiprows=2, nrows=2)
    assert (
        urban.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Urbanization level"] + urban_value_columns
    )
    assert urban["Urbanization level"].tolist() == ["Low", "High"]
    for i, level in enumerate(urban["Urbanization level"].values):
        # last column is nodata, omitted here
        assert np.allclose(urban[urban_value_columns].iloc[i].values, results.urban.iloc[0][level.lower()][:-1])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_create_xlsx_file_multiple_areas(format):
    filename = f"{format}_poly_multiple.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=["Region"], use_arrow=True).to_crs(
        DATA_CRS
    )
    df = dissolve(df.explode(ignore_index=True), by="Region").set_index("Region")

    # representative sample of datasets
    datasets = [
        "landfire_evt",
        "nlcd_impervious",
        "nlcd_inundation_freq",
        "nlcd_landcover",
        "protected_areas",
        "sarp_aquatic_barriers",
        "sarp_aquatic_network_alteration",
        "se_blueprint_firefrequency",
        "se_blueprint_resilientterrestrialsites",
        "slr_depth",
        "slr_proj",
        "urban",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_xlsx(results, datasets)

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_multiple_areas.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 2
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results.pixels)
    assert np.allclose(summary["Number of areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["name"] for id, d in DATASETS.items() if id in datasets]

    slr_depth = reader.parse(sheet_name="SLR inundation area", skiprows=2)
    assert (
        slr_depth.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Area outside extent of this dataset\n(acres)"]
        + slr_depth_value_columns
    )
    # last value is nodata, ignore that for comparison because it is shuffled to a different column
    assert np.allclose(slr_depth[slr_depth_value_columns].iloc[0].values, results.slr_depth.iloc[0][:-1])

    slr_proj = reader.parse(sheet_name="Projected SLR", skiprows=2)
    assert slr_proj.columns.tolist() == ["Analysis unit"] + slr_proj_value_columns
    assert slr_proj["Has projected SLR?"].iloc[:15].tolist() == ["yes"] * 15
    assert np.allclose(slr_proj.iloc[0][slr_proj_value_columns[2:]].values, results.slr_proj.iloc[0][0]["values"])

    urban = reader.parse(sheet_name="Urbanization", skiprows=2, nrows=2)
    assert (
        urban.columns.tolist()
        == [
            "Analysis unit",
            "Analysis area\n(acres)",
            "Area outside extent of this dataset\n(acres)",
            "Urbanization level",
        ]
        + urban_value_columns
    )
    assert urban["Urbanization level"].tolist() == ["Low", "High"]
    for i, level in enumerate(urban["Urbanization level"].values):
        # last column is nodata, omitted here
        assert np.allclose(
            urban[urban_value_columns].iloc[i].fillna(0).values, results.urban.iloc[0][level.lower()][:-1]
        )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp"])
async def test_create_xlsx_file_west_coast(format):
    filename = f"{format}_poly_west_coast.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=["id"], use_arrow=True).to_crs(DATA_CRS)

    df = dissolve(df.explode(ignore_index=True), by="id").set_index("id")

    # representative sample of datasets
    datasets = [
        "landfire_evt",
        "nlcd_impervious",
        "nlcd_inundation_freq",
        "nlcd_landcover",
        "protected_areas",
        "sarp_aquatic_barriers",
        "sarp_aquatic_network_alteration",
        "se_blueprint_resilientterrestrialsites",
        "slr_depth",
        "slr_proj",
        "urban",
    ]

    results = await get_analysis_unit_results(df, datasets)
    xlsx = create_xlsx(results, datasets)

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_west_coast.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 2
    summary = reader.parse(sheet_name="Summary", skiprows=2)
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results.pixels)
    assert np.allclose(summary["Number of areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    slr_depth = reader.parse(sheet_name="SLR inundation area", skiprows=2)
    # drops inland counties because not applicable
    slr_depth_col_ix = list(range(11))
    slr_value_cols = np.array(slr_depth_value_columns).take(slr_depth_col_ix).tolist()
    assert (
        slr_depth.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Area outside extent of this dataset\n(acres)"] + slr_value_cols
    )
    assert np.allclose(
        slr_depth[slr_value_cols].iloc[0].fillna(0).values, results.slr_depth.iloc[0].take(slr_depth_col_ix)
    )

    slr_proj = reader.parse(sheet_name="Projected SLR", skiprows=2)
    assert slr_proj.columns.tolist() == ["Analysis unit"] + slr_proj_value_columns
    assert slr_proj["Has projected SLR?"].iloc[:3].tolist() == ["no"]

    urban = reader.parse(sheet_name="Urbanization", skiprows=2, nrows=2)
    assert (
        urban.columns.tolist()
        == ["Analysis unit", "Analysis area\n(acres)", "Urbanization level"] + urban_value_columns
    )
    assert urban["Urbanization level"].tolist() == ["Low", "High"]
    for i, level in enumerate(urban["Urbanization level"].values):
        # last column is nodata, omitted here
        assert np.allclose(urban[urban_value_columns].iloc[i].values, results.urban.iloc[0][level.lower()][:-1])
