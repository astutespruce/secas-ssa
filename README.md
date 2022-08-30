# Species Status Landscape Assessment Tool - Pilot

This pilot application is intended to support
[Species Status Assessments](https://www.fws.gov/project/species-status-assessment)
conducted by the U.S. Fish and Wildlife Service in the Southeastern U.S. by
providing summaries of standardized landscape-level indicators for each population
unit of a given species.

It directly leverages related work on the
[SECAS Southeast Conservation Blueprint Explorer](https://github.com/astutespruce/secas-blueprint)
which is available online at https://blueprint.geoplatform.gov/southeast/

## Architecture

This uses a data processing pipeline in Python to prepare all spatial data for use in this application.

The user interface is creating using GatsbyJS as a static web application.

The API is implemented in Python and provides summary reports for pre-defined summary units and user-defined areas.

## Development

Python dependencies are managed using `poetry`. First, install poetry, then
`poetry install` to install most of them.

## Credits

This project is developed under a grant from the U.S. Fish and Wildlife Service
to support the [Southeast Conservation Adaptation Strategy](https://secassoutheast.org/).
