def get_dataset(zip_filename):
    """Gets singular geospatial dataset and layer for analysis.

    Validates rules:
    - There must be only one data source (.shp or .gdb) in the zip file.
    - There must be only one data layer in that data source.
    - The data source must contain the required files (.prj for shapefile; .
      dbf is not used so not required)

    Parameters
    ----------
    zip : str
        full path to zip file

    Returns
    -------
    (str, str)
        tuple of geospatial file within zip file, name of layer
    """

    with ZipFile(zip_filename) as zipfile:
        # exclude OS-specific hidden files and directories
        files = set(
            f for f in zipfile.namelist() if "__MACOSX" not in f or ".DS_Store" in f
        )

        geo_files = [f for f in files if f.endswith(".shp") or f.endswith(".gdb")]
        num_files = len(geo_files)

        if num_files == 0:
            log.error("Upload zip file does not contain shp or FGDB files")

            raise DataError("zip file must include a shapefile or FGDB")

        if num_files > 1:
            log.error(
                f"Upload zip file contains {num_files} shp or FGDB files:\n{geo_files}"
            )

            raise DataError("zip file must include only one shapefile or FGDB")

    filename = geo_files[0]

    if filename.endswith(".shp"):
        missing = []
        for ext in (".prj", ".shx"):
            if filename.replace(".shp", ext) not in files:
                missing.append(ext)

        if missing:
            log.error(f"Upload zip file contains .shp but not {','.join(missing)}")
            raise DataError("zip file must include .shp, .prj, and .shx files")

    # Validate that dataset is a polygon and has only a single layer
    layers = list_layers(f"zip://{zip_filename}/{filename}")

    if layers.shape[0] > 1:
        log.error(f"Upload data source contains multiple data layers\n{layers}")
        raise DataError("data source must contain only one data layer")

    if "Polygon" not in layers[0, 1]:
        log.error(f"Upload data source is not a polygon: {layers[0, 1]}")
        raise DataError("data source must be a Polygon type")

    return filename, layers[0, 0]
