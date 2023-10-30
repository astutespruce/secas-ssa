# Inundation Frequency

This dataset was obtained from Yvonne Allen (USFWS) on 2/9/2023.

The data are delivered as 2 parts: most of the Southeast, and Texas / Oklahoma.
These are combined in a GDAL VRT so that values from the Texas / Oklohoma dataset
are used where the 2 datasets overlap.

These are warped and clipped to match the inland portion of the contiguous
Southeast Base Blueprint.

Values are originally the number of times a given pixel was recorded as inundated
within the period of record. These were binned based on guidance from Yvonne
Allen into 5 bins:

- <= 5: very low
- 6-10: low
- 11-50: moderate
- 51-90: high
- 91-100: very high

These binned values are then combined with NLCD 2021 land cover classes and
coded so that each NLCD class has a value for each of the 5 inundation frequency
values (if the combination occurs).
