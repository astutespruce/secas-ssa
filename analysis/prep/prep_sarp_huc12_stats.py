from pathlib import Path

import numpy as np
import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.constants import DATA_CRS
from api.settings import DATA_DIR

src_dir = Path("source_data/sarp/")

df = read_dataframe(src_dir / "huc12_stats.fgb", use_arrow=True).to_crs(DATA_CRS)

states = read_dataframe(DATA_DIR / "inputs/boundaries/states.fgb", columns=[], use_arrow=True)
bnd = shapely.coverage_union_all(states.geometry.values)
ix = np.unique(shapely.STRtree(df.geometry.values).query(bnd, predicate="intersects"))
df = df.take(ix).sort_values(by="geometry")
write_dataframe(df, "data/inputs/boundaries/sarp_huc12_stats.fgb")
