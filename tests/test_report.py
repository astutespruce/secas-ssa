import os
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
from api.report.urban import value_columns as urban_value_columns
from api.report.xlsx import create_xlsx
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

    result, errors = await get_report_inputs(
        mock_ctx, f"tests/fixtures/{filename}", dataset, layer="poly_small", uuid=uuid
    )

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

    with pytest.raises(
        DataError,
        match="area of interest does not overlap any of the available datasets",
    ):
        await get_report_inputs(
            mock_ctx,
            f"tests/fixtures/{filename}",
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

    result, errors = await get_report_inputs(
        mock_ctx,
        f"tests/fixtures/{filename}",
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

    result, errors = await get_report_inputs(
        mock_ctx,
        f"tests/fixtures/{filename}",
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
    for col in [
        "states",
        "count",
        "acres",
        "rasterized_acres",
        "overlap_acres",
        "outside_extent_acres",
    ]:
        assert col in results.columns

    row = results.iloc[0]

    assert row.states == "Alabama"
    assert row["count"] == 1
    assert np.isclose(row.acres, 51.026)
    assert np.isclose(row.rasterized_acres, 50.7059)
    assert np.isclose(row.overlap_acres, 50.7059)
    assert np.isclose(row.outside_extent_acres, 0)

    # Landfire EVT is stored as a dict of indexes and acres
    assert list(row.landfire_evt.keys()) == [64, 93, 133, 496]
    assert np.allclose(list(row.landfire_evt.values()), [10.8973, 3.1135, 36.0279, 0.6672], atol=1e-4)

    # NLCD landcover is stored as a dict of arrays
    assert list(row.nlcd_landcover.keys()) == [
        "Deciduous forest",
        "Evergreen forest",
        "Mixed forest",
    ]
    assert np.allclose(
        row.nlcd_landcover["Deciduous forest"],
        [48.2596, 48.9268, 48.9268, 48.9268, 48.9268],
        atol=1e-4,
    )

    assert len(row.protected_areas) == 1
    assert row.protected_areas[0]["name"] == "Talladega National Forest"
    assert row.protected_areas[0]["owner"] == "USDA Forest Service"
    assert row.protected_areas[0]["gap_status"] == "3"
    assert np.isclose(row.protected_areas[0]["acres"], 34.5465)

    assert len(row.slr_depth) == 14
    assert np.allclose(row.slr_depth, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50.71, 0])

    assert list(row.urban.keys()) == ["high", "low"]
    assert np.allclose(row.urban["high"], [0, 0, 0, 0, 0, 0, 0, 0, 0])


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_get_analysis_unit_results_multiple_areas_partial_overlap(format):
    # NOTE: this needs to be updated for each blueprint version; this is just a
    # smoke test that values do not change except during Blueprint version updates

    filename = f"{format}_poly_multiple_partial_overlap.zip"
    dataset = filename.replace(f"{format}_", "").replace(".zip", f".{format}")
    df = read_dataframe(f"/vsizip/tests/fixtures/{filename}/{dataset}", columns=[], use_arrow=True).to_crs(DATA_CRS)
    datasets = get_available_datasets(df)

    results = await get_analysis_unit_results(df, datasets)

    assert len(results) == len(df)
    for col in [
        "states",
        "count",
        "acres",
        "rasterized_acres",
        "overlap_acres",
        "outside_extent_acres",
    ]:
        assert col in results.columns

    assert results.states.fillna("").values.tolist() == [
        "North Carolina",
        "",
        "Missouri",
    ]

    assert results["count"].values.tolist() == [1] * 3
    assert np.allclose(results["acres"], [280.4020, 394.7394, 68.8730])
    assert np.allclose(results["rasterized_acres"], [280.6619, 397.4190, 69.6095])
    assert np.allclose(results["rasterized_acres"], [280.6619, 397.4190, 69.6095])
    assert np.allclose(results["outside_extent_acres"], [0, 397.4190, 0])

    outside_row = results.iloc[1]
    assert np.isnan(outside_row.landfire_evt)
    assert np.isnan(outside_row.nlcd_landcover)
    assert np.isnan(outside_row.slr_depth)
    assert np.isnan(outside_row.urban)


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
    assert np.allclose(results["rasterized_acres"], [747.6904])
    assert np.allclose(results["outside_extent_acres"], [397.4190])


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
    summary = reader.parse(sheet_name="Summary")
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    assert np.allclose(summary["Analysis acres (rasterized to 30m pixels)"], results.rasterized_acres)
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results["pixels"])
    assert np.allclose(summary["Number of areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details")
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["name"] for id, d in DATASETS.items() if id in datasets]

    # skip caption at end
    landfire_evt = reader.parse(sheet_name="LANDFIRE EVT", nrows=5)
    assert len(landfire_evt) == 4
    assert landfire_evt.columns.tolist() == [
        "Analysis unit",
        "Analysis acres",
        "Existing Vegetation Type",
        "Group",
        "Acres",
    ]
    assert landfire_evt["Existing Vegetation Type"].tolist() == [
        "Southern Piedmont Mesic Forest",
        "Southeastern Interior Longleaf Pine Woodland",
        "Southern Piedmont Dry Oak Forest",
        "Southeastern Native Ruderal Forest",
    ]
    assert landfire_evt["Group"].tolist() == [
        "White Oak-Beech Forest and Woodland",
        "Longleaf Pine Woodland",
        "Chestnut Oak-Virginia Pine Forest and Woodland",
        "Introduced Upland Vegetation-Treed",
    ]
    assert np.allclose(landfire_evt["Acres"], list(results.iloc[0].landfire_evt.values()))

    nlcd_landcover = reader.parse(sheet_name="Landcover trends", nrows=4)
    assert (
        nlcd_landcover.columns.tolist() == ["Analysis unit", "Analysis acres", "Land cover type"] + nlcd_value_columns
    )
    assert nlcd_landcover["Land cover type"].tolist() == list(results.nlcd_landcover.iloc[0].keys())

    for i, landcover_type in enumerate(nlcd_landcover["Land cover type"].values):
        assert np.allclose(
            nlcd_landcover[nlcd_value_columns].iloc[i].values, results.nlcd_landcover.iloc[0][landcover_type], atol=1e-4
        )

    urban = reader.parse(sheet_name="Urbanization", nrows=3)
    assert urban.columns.tolist() == ["Analysis unit", "Analysis acres", "Urbanization level"] + urban_value_columns
    assert urban["Urbanization level"].tolist() == ["Low", "High"]
    for i, level in enumerate(urban["Urbanization level"].values):
        assert np.allclose(urban[urban_value_columns].iloc[i].values, results.urban.iloc[0][level.lower()])


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
    xlsx = create_xlsx(results, datasets, name="Test area")

    if SAVE_XLSX:
        with open("/tmp/test_create_xlsx_file_multiple_areas_partial_overlap.xlsx", "wb") as out:
            _ = out.write(xlsx)

    reader = pd.ExcelFile(BytesIO(xlsx))

    assert len(reader.sheet_names) == len(datasets) + 2
    summary = reader.parse(sheet_name="Summary")
    assert len(summary) == len(df)

    assert np.allclose(summary["GIS acres"], results.acres)
    # when there is partial overlap, we have two rasterized area columns: within and outside
    assert np.allclose(summary["Acres within Southeast data extent (rasterized to 30m pixels)"], results.overlap_acres)
    assert np.allclose(
        summary["Acres outside Southeast data extent (rasterized to 30m pixels)"], results.outside_extent_acres
    )
    assert np.allclose(summary["Number of 30m pixels in analysis unit"], results.pixels)
    assert np.allclose(summary["Number of distinct areas in analysis unit"], results["count"])
    assert summary["State(s)"].tolist() == results.states.tolist()

    details = reader.parse(sheet_name="Data details", skiprows=2)
    assert len(details) == len(datasets)
    assert details["Name"].tolist() == [d["name"] for id, d in DATASETS.items() if id in datasets]
