# NLCD Annual Data product

NLCD land cover and percent impervious were downloaded from https://www.mrlc.gov/data
on 5/19/2026 for 1985-2020 and 10/6/2026 for 2025:

- 1985
- 2000
- 2015
- 2020
- 2025

These are processed separately from the NLCD legacy data product versions prepared
in the `secas-blueprint` project.

Data are processed using `analysis/prep/prep_nlcd.py`.

IMPORTANT: these data are not used for already urban areas in the FUTURES
projected urbanization data. That uses NLCD legacy 2021 as prepared in the
`secas-blueprint` project.
