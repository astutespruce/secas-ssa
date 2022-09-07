from itertools import product
import json
from pathlib import Path

import numpy as np


DATA_CRS = "EPSG:5070"
GEO_CRS = "EPSG:4326"

# metric to imperial units
M2_ACRES = 0.000247105
M_MILES = 0.000621371
AREA_PRECISION = 2

# 32 is OK for regional level maps; 16 is more typical for big areas like ACF
OVERVIEW_FACTORS = [2, 4, 8, 16, 32]

# Use 480m cells for mask
MASK_FACTOR = 16

SECAS_STATES = [
    "AL",
    "AR",
    "FL",
    "GA",
    "KY",
    "LA",
    "MS",
    "MO",
    "MS",
    "NC",
    "OK",
    # "PR",  # no meaningful data available
    "SC",
    "TN",
    "TX",
    "VA",
    # "USVI",  # no meaningful data available
    "WV",
]

NLCD_YEARS = [2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019]


URBAN_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
# values are number of runs out of 50 that are predicted to urbanize
# 51 = urban as of 2019 (NLCD)
# NOTE: index 0 = not predicted to urbanize
URBAN_PROBABILITIES = np.append(np.arange(0, 51) / 50.0, np.array([1.0]))
URBAN_BINS = np.arange(0, len(URBAN_PROBABILITIES))
URBAN_THRESHOLD = 25  # >= 50% probability

# depth in feet
SLR_DEPTHS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SLR_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
SLR_PROJ_SCENARIOS = {
    "l": "Low",
    "il": "Intermediate-low",
    "i": "Intermediate",
    "ih": "Intermediate-high",
    "h": "High",
}
SLR_PROJ_COLUMNS = [
    f"{decade}_{scenario}"
    for decade, scenario in product(SLR_YEARS, SLR_PROJ_SCENARIOS)
]

SLR_COLORS = [
    "#00094E",
    "#031386",
    "#0821BD",
    "#1136E0",
    "#1E50EE",
    "#2D6BFC",
    "#2D8CFC",
    "#2CADFC",
    "#47D4FC",
    "#7DF5FD",
    "#B3FEF7",
]


# color are (R,G,B) tuples
# Original codes
NLCD_CODES = {
    # 0: NODATA,
    11: {"label": "Open water", "color": (70, 107, 159)},
    12: {"label": "Perennial ice/snow", "color": (209, 222, 248)},
    21: {"label": "Developed (open space)", "color": (222, 197, 197)},
    22: {"label": "Developed (low intensity)", "color": (217, 146, 130)},
    23: {"label": "Developed (medium intensity)", "color": (235, 0, 0)},
    24: {"label": "Developed (high intensity)", "color": (171, 0, 0)},
    31: {"label": "Barren land", "color": (179, 172, 159)},
    41: {"label": "Deciduous forest", "color": (104, 171, 95)},
    42: {"label": "Evergreen forest", "color": (28, 95, 44)},
    43: {"label": "Mixed forest", "color": (181, 197, 143)},
    52: {"label": "Shrub/scrub", "color": (204, 184, 121)},
    71: {"label": "Grassland/herbaceous", "color": (223, 223, 194)},
    81: {"label": "Pasture/hay", "color": (220, 217, 57)},
    82: {"label": "Cultivated crops", "color": (171, 108, 40)},
    90: {"label": "Woody wetlands", "color": (184, 217, 235)},
    95: {"label": "Emergent herbaceous wetlands", "color": (108, 159, 184)},
}

NLCD_INDEXES = {i: e for i, e in enumerate(NLCD_CODES.values())}

json_dir = Path("constants")
DATASETS = json.loads(open(json_dir / "datasets.json").read())
