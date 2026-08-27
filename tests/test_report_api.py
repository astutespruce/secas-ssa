import pytest
from httpx import HTTPStatusError

from analysis.constants import DATASETS
from api.settings import API_TOKEN
from tests.lib.jobs import poll_until_done


@pytest.mark.anyio
async def test_custom_report_missing_token(client):
    response = await client.post("/report")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_custom_report_missing_file(client):
    response = await client.post(f"/report?token={API_TOKEN}")
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["msg"] == "Field required"
    assert error["loc"][1] == "file"


@pytest.mark.anyio
async def test_custom_report_empty_zip(client):
    with open("tests/fixtures/zip_empty.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 400
    assert response.json()["detail"] == "zip file must include a shapefile or file geodatabase"


@pytest.mark.anyio
async def test_custom_report_invalid_type(client):
    with open("tests/fixtures/zip_empty.zip", "rb") as infile:
        # spoof an invalid mime type and filename
        response = await client.post(
            f"/report?token={API_TOKEN}",
            files={"file": ("zip_empty.not-zip", infile, "invalid-mime-type")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "file must be a zip file containing shapefile or file geodatabase"


@pytest.mark.anyio
async def test_custom_report_unsupported_format(client):
    with open("tests/fixtures/geojson.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 400
    assert response.json()["detail"] == "zip file must include a shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
@pytest.mark.parametrize("geometry_type", ["point", "line"])
async def test_custom_report_invalid_geometry(client, format, geometry_type):
    with open(f"tests/fixtures/{format}_{geometry_type}.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 400
    assert response.json()["detail"] == "data source must be a Polygon type"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_report_multiple_files(client, format):
    with open(f"tests/fixtures/{format}_poly_multiple_files.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 400
    assert response.json()["detail"] == "zip file must include only one shapefile or file geodatabase"


@pytest.mark.anyio
async def test_custom_report_multiple_layers(client):
    with open("tests/fixtures/gdb_poly_multiple_files.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 400
    assert response.json()["detail"] == "zip file must include only one shapefile or file geodatabase"


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_report_too_many_features(client, format):
    with open(f"tests/fixtures/{format}_poly_too_many.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 400
    assert "data source contains too many features" in response.json()["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_report_area_too_small(client, format):
    with open(f"tests/fixtures/{format}_poly_tiny.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "failed"
    assert (
        r"100% of the total area in the data source is in polygons less than a single 30x30m pixel" in result["detail"]
    )


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_report_area_too_large(client, format):
    with open(f"tests/fixtures/{format}_poly_large.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "failed"
    assert "Your area of interest is too large" in result["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_report_no_overlap(client, format):
    with open(f"tests/fixtures/{format}_poly_no_overlap.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "failed"
    assert "area of interest does not overlap" in result["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_xlsx_report_api_single_area(client, format):
    with open(f"tests/fixtures/{format}_poly_small.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"

    result_payload = result["result"]
    uuid = result_payload["uuid"]
    assert result_payload["count"] == 1

    fields = result_payload["fields"]
    assert fields["ID"] == 1
    assert fields["Name"] == 1

    datasets = set(result_payload["datasets"])
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

    ### submit finalize job
    response = await client.post(f"/report/{uuid}/finalize?token={API_TOKEN}", data={"datasets": ",".join(datasets)})
    assert response.status_code == 200

    job_id = response.json()["job"]
    result_url = f"/jobs/{job_id}/xlsx"
    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"
    assert result.get("result").replace("/api", "") == result_url

    response = await client.get(result_url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.headers["content-disposition"].startswith("attachment;")


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_xlsx_report_api_single_area_invalid_field(client, format):
    """This will raise an HTTP 500 because the field is not found"""
    with open(f"tests/fixtures/{format}_poly_small.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"

    result_payload = result["result"]
    datasets = result_payload["datasets"]
    uuid = result_payload["uuid"]

    response = await client.post(
        f"/report/{uuid}/finalize?token={API_TOKEN}", data={"datasets": ",".join(datasets), "field": "INVALID"}
    )
    assert response.status_code == 200

    job_id = response.json()["job"]

    with pytest.raises(HTTPStatusError):
        result = await poll_until_done(client, job_id)


@pytest.mark.anyio
@pytest.mark.parametrize("format", ["shp", "gdb"])
async def test_custom_xlsx_report_api_multiple_areas(client, format):
    with open(f"tests/fixtures/{format}_poly_multiple.zip", "rb") as infile:
        response = await client.post(f"/report?token={API_TOKEN}", files={"file": infile})

    assert response.status_code == 200
    job_id = response.json()["job"]

    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"

    result_payload = result["result"]
    uuid = result_payload["uuid"]
    assert result_payload["count"] == 5

    fields = result_payload["fields"]
    assert fields["Name"] == 5

    datasets = set(result_payload["datasets"])
    assert len(datasets) == 20

    ### submit finalize job
    response = await client.post(
        f"/report/{uuid}/finalize?token={API_TOKEN}", data={"datasets": ",".join(datasets), "field": "Name"}
    )
    assert response.status_code == 200

    job_id = response.json()["job"]
    result_url = f"/jobs/{job_id}/xlsx"
    result = await poll_until_done(client, job_id)
    assert result["status"] == "success"
    assert result.get("result").replace("/api", "") == result_url

    response = await client.get(result_url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.headers["content-disposition"].startswith("attachment;")
