# Data preparation

Where possible, data are prepared in the associated Southeast Conservation Blueprint
Explorer (https://github.com/astutespruce/secas-blueprint) project. However,
some datasets in this tool are at the national rather than regional level, and are
specifically prepared here.

## States

State boundaries for the continental U.S., Puerto Rico, and U.S. Virgin Islands are prepared
using `analysis/prep/prep_states.py.`.

State boundaries from US Census TIGER (2025 version) are sourced from the
Blueprint Explorer source directory.

## Southeast Conservation Blueprint Indicators

These datasets were prepared as part of the Southeast Blueprint Explorer data
preparation process (`secas-blueprint/analysis/prep/prepare_base_blueprint.py`).

These are 30 meter data aligned to the Southeast Blueprint extent, which is slightly
(a few meters) off the alignment of the master extent used in this tool (based on NLCD).

Value labels were modified to be appropriate as column names.

## Sea-level rise

These datasets were prepared as part of the Southeast Blueprint Explorer data
preparation process (`secas-blueprint/analysis/prep/prepare_slr.py`).

These data were rasterized from polygon data to a 30 meter resolution aligned to
the Base Blueprint extent used in this tool. Only polygons and holes that are
bigger than 1/2 the area of a 30 meter pixel were retained during processing.

NOTE: because these were extracted from the Southeast Blueprint Explorer, these
data are only available for Southeastern states, Puerto Rico, and U.S. Virgin Islands.

## Urbanization data

These datasets were prepared as part of the Southeast Blueprint Explorer data
preparation process (`secas-blueprint/analysis/prep/prepare_urban.py`).

These are 30 meter data aligned to the Base Blueprint extent used in this tool.

## NLCD land cover by inundation frequency

Data are prepared using `analysis/prep/prepare_inundation_frequency.py`.

See `source_data/inundation_frequency/README.md` for more information.

NOTE: these data are only available in the Southeast Blueprint extent.

## NLCD land cover and impervious surface data

These datasets were prepared using `analysis/prep/prep_nlcd.py`.

These are 30 meter data aligned to the Base Blueprint extent used in this tool.

## LANDFIRE Existing Vegetation Type

The LANDFIRE EVT was prepared using `analysis/prep/prep_landfire.py`.

## Protected areas

This dataset builds off data as part of the Southeast Blueprint Explorer data
preparation process, but includes GAP status for use here.

The protected areas dataset was prepared using `analysis/prep/prep_protected_areas.py`.

## SARP Aquatic Barrier and Network Metrics

Data are prepared using `analysis/prep/prep_sarp_huc12_stats.py`.

These metrics are prepared as part of the National Aquatic Barrier Inventory &
Prioritization Tool. See `source_data/sarp/README.md` for more information.
