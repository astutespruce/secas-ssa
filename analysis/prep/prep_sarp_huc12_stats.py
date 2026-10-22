import geopandas as gp
import numpy as np
import shapely
from pyogrio import read_dataframe, read_info, write_dataframe

from analysis.constants import DATA_CRS, SECAS_STATES
from api.settings import SHARED_DATA_DIR

crs = read_info("source_data/sarp/huc12_stats.fgb")["crs"]

states = gp.read_feather(SHARED_DATA_DIR / "inputs/boundaries/states.feather").to_crs(crs)
states = states.loc[states.id.isin(SECAS_STATES)]
read_mask = shapely.union_all(shapely.envelope(states.geometry.values))
df = read_dataframe("source_data/sarp/huc12_stats.fgb", use_arrow=True, mask=read_mask).to_crs(DATA_CRS)

states = states.to_crs(DATA_CRS)
ix = np.unique(shapely.STRtree(df.geometry.values).query(states.geometry.values, predicate="intersects")[1])
df = df.take(ix).sort_values(by="geometry")
write_dataframe(df, "data/inputs/sarp_huc12_stats.fgb")
