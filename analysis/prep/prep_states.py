import warnings
from pathlib import Path

from pyogrio import read_dataframe, write_dataframe

from analysis.constants import DATA_CRS

warnings.filterwarnings("ignore", message=".*polygon with more than 100 parts.*")

NODATA = 255

src_dir = Path("../secas-blueprint/source_data/boundaries")
out_dir = Path("data/inputs/boundaries")
if not out_dir.exists():
    out_dir.mkdir(exist_ok=True)

# limit to CONUS and Caribbean
df = (
    read_dataframe(
        src_dir / "tl_2025_us_state.zip",
        columns=["STUSPS", "NAME"],
        where="STUSPS not in ('AK', 'AS', 'HI', 'MP')",
        use_arrow=True,
    )
    .rename(columns={"STUSPS": "id", "NAME": "state"})
    .to_crs(DATA_CRS)
)

write_dataframe(df, out_dir / "states.fgb")
