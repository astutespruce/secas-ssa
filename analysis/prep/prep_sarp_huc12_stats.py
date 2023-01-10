import geopandas as gp

from analysis.constants import DATA_CRS


df = gp.read_feather("source_data/sarp/huc12_stats.feather").to_crs(DATA_CRS)

# add bounds for spatial indexing
df = df.join(df.bounds)

df.to_feather("data/inputs/sarp_huc12_stats.feather")
