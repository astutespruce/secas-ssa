# SARP Aquatic Barrier and Network Metrics

The [National Aquatic Barrier Prioritization Tool](https://aquaticbarriers.org/)
created by the Southeast Aquatic Resources Partnership (SARP) includes data
describing aquatic barriers and the connectivity of aquatic networks.

Data were extracted from the data used for the Aquatic Barrier Prioritization
Tool v3.19.0 (7/30/2025) using this script:
https://github.com/astutespruce/sarp-connectivity/blob/main/analysis/export/export_secas_ssa_stats.py

Data include metrics at the HUC12 level:

- number of dams (excluding duplicates, errors, and dams removed for conservation)
- number of road / stream crossings
- percent of aquatic network that is considered altered
- total altered network miles
- total network miles

The aquatic network is derived from the NHD High Resolution dataset. Flowlines
are extracted except those that are:

- coastlines
- underground connectors
- long pipelines
- flowlines without associated drainage area

Flowlines are considered altered if they are identified by NHD as canal / ditch
type, are within a reservoir within the NHD waterbody or state-level waterbody
dataset, or overlap with riverine areas in the National Wetlands Inventory
that are marked as altered (e.g., diked, ditched, etc).

NOTE: some flowlines that are in fact altered are not included in the analysis
because they have no associated drainage area information; these include
irrigation canals that may have limited connections to the drainage-based aquatic
network. Thus the altered metric may underrepresent the true degree of aquatic
network alteration.
