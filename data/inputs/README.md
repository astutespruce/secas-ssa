## Southeast Conservation Blueprint Indicators

These datasets were prepared as part of the Southeast Blueprint Explorer data
preparation process (`secas-blueprint/analysis/prep/prepare_base_blueprint.py`).

These are 30 meter data aligned to the Base Blueprint extent used in this tool.

Value labels were modified to be appropriate as column names.

## Sea-level rise

These datasets were prepared from the same source data as the Southeast Blueprint
Explorer. See `secas-blueprint/source_data/slr/README.md` for more information.

These data were prepared using `analysis/prep/prepare_slr.py`

These data were rasterized from polygon data to a 30 meter resolution aligned to
the Base Blueprint extent used in this tool. Only polygons and holes that are
bigger than 1/2 the area of a 30 meter pixel were retained during processing.

## Urbanization data

These datasets were prepared as part of the Southeast Blueprint Explorer data
preparation process (`secas-blueprint/analysis/prep/prepare_urban.py`).

These are 30 meter data aligned to the Base Blueprint extent used in this tool.
