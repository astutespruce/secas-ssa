import warnings
from pathlib import Path

import shapely
from pyogrio import read_dataframe, write_dataframe

from analysis.lib.geometry import dissolve, make_valid

warnings.filterwarnings("ignore", message=".*polygon with more than 100 parts.*")

src_dir = Path("../secas-blueprint/source_data/protected_areas")
data_dir = Path("data")
out_dir = data_dir / "inputs/boundaries"
out_dir.mkdir(exist_ok=True)


################################################################################
### Compile protected areas
################################################################################

### Protected areas (PAD-US)
print("Processing PAD-US lands...")

# read specific states; data are already in EPSG:5070
states = read_dataframe(out_dir / "states.fgb", columns=["id"], read_geometry=False).sort_values("id").id.tolist()
states = ",".join(f"'{s}'" for s in states + ["UNKF"])
df = read_dataframe(
    src_dir / "pad_us4.1.gpkg",
    layer="PADUS4_1Combined_Proclamation_Marine_Fee_Designation_Easement",
    columns=[
        "Category",
        "State_Nm",
        "Unit_Nm",
        "Loc_Own",
        "Own_Name",
        "GAP_Sts",
        "Agg_Src",
        "Des_Tp",
    ],
    where=f"State_Nm in ({states})",
    use_arrow=True,
)

# drop BOEM lease block groups
df = df.loc[~df.Agg_Src.str.contains("_BOEM_")].drop(columns=["Agg_Src"])

# drop proclamation boundaries but retain military lands that only show up as proclamation
df = df.loc[(df.Category != "Proclamation") | (df.Des_Tp == "MIL")].reset_index(drop=True)

df = df.drop_duplicates()


print("making valid and exploding parts...")
df["geometry"] = make_valid(df.geometry.values)
df = df.explode(ignore_index=True)

# there may be some geometry errors after cleaning up above, keep only polys
df = df.loc[shapely.get_type_id(df.geometry.values) == 3].reset_index(drop=True)


# use more friendly attributes
df = df.rename(columns={"Unit_Nm": "name", "Loc_Own": "owner", "GAP_Sts": "gap_status"})


# cleanup names where easy
df["name"] = df.name.str.replace(".Wilderness Area", " (Wilderness Area)", regex=False)


df.loc[(df.owner == "Fee") & (df.Own_Name == "FWS"), "owner"] = "US Fish and Wildlife Service"

df["owner"] = (
    df.owner.replace("UNK", "")
    .str.replace("Unknown", "", regex=False, case=False)
    .replace("Unspecified", "")
    .replace("USDA FOREST SERVICE", "USDA Forest Service")
    .replace("NPS", "National Park Service")
    .replace("Private Owner", "Private")
    .replace("Private Owners", "Private")
    .replace("NGO", "Non-Governmental Organization")
    .replace("UNITED STATES ARMY", "US Army")
    .str.replace("United States of America", "US Federal Government", regex=False, case=False)
    .replace("United Sates of America", "US Federal Government")
    .replace("US Govt", "US Federal Government")
    .replace("United States Govt", "US Federal Government")
    .replace("US Goverment", "US Federal Government")
    .replace("USA", "US Federal Government")
    .replace("US Military Department", "US Department of Defence")
    # seriously Army Corps of Engineers, standardize your protected area ownership label!
    .replace("Corps of Engineers", "US Army Corps of Engineers")
    .replace("U S ARMY CORP OF ENGINEERS", "US Army Corps of Engineers")
    .replace("Army Corps of Engineers", "US Army Corps of Engineers")
    .replace("U.S. Army Corps of Engineers", "US Army Corps of Engineers")
    .replace("UNITED STATES ARMY CORPS OF ENGINEERS", "US Army Corps of Engineers")
    .replace("US Army Corp of Engineers", "US Army Corps of Engineers")
    .replace("US Corp of Engineers", "US Army Corps of Engineers")
    .replace("US Corps of Engineers", "US Army Corps of Engineers")
    .replace("US Engineer Corps", "US Army Corps of Engineers")
    .replace("US Engineers Corps", "US Army Corps of Engineers")
    .replace("USA Corp of Engineers", "US Army Corps of Engineers")
    .replace("USA CORP OF ENGINEERS", "US Army Corps of Engineers")
    .replace("US Military", "US Department of Defence")
    .replace("US DOE", "US Department of Energy")
    .replace("US", "US Federal Government")
    .replace("Fed", "US Federal Government")
    .replace("JNT", "Joint ownership")
    .replace("PVT", "Private")
    .replace("STAT", "State")
    .replace("TRIB", "Tribal")
    .replace("CONSERVATION EASE", "Conservation easement")
)


print("Dissolving overlapping features with same name / ownership")
df = dissolve(df, by=["name", "owner", "gap_status"])


df.owner.drop_duplicates().to_csv("/tmp/names.csv", index=False)


# Use FGB (instead of Feather) for more optimal reading by area of interest
print("Writing files")
write_dataframe(
    df[["name", "owner", "gap_status", "geometry"]].explode(ignore_index=True),
    out_dir / "protected_areas_with_gap_status.fgb",
)
