# SECAS Southeast Species Status Landscape Assessment Tool - Local Development

## Architecture

This uses a data processing pipeline in Python to prepare all spatial data for use in this application.

The user interface is creating using GatsbyJS as a static web application.

The API is implemented in Python and provides summary reports for pre-defined summary units and user-defined areas.

## Data Analysis & API Development

Python dependencies are managed using `uv`. First,
[install uv](https://docs.astral.sh/uv/), then:

```bash
uv venv .venv --python 3.12
<source it according to your shell, e.g., source .venv/bin/activate.fish>
uv pip install -e .[dev]
```

To check for outdated dependencies and upgrade them:

```bash
uv pip list --outdated

# install latest version
uv sync --upgrade --all-extras
```

To update the requirements.txt file used to build these dependencies into the API
Docker container for deployment, run:

```bash
uv pip compile -U pyproject.toml -o ../secas-docker/docker/api/secas-ssa-requirements.txt
```


## User interface development

The user interface is developed using Javascript, executed in NodeJS during a
dedicated build step to build the user interface into static assets, which are
then rendered in the browser.

Install NodeJS using `nvm` using the instructions [here](https://github.com/nvm-sh/nvm).
The version of NodeJS is specified in `ui/.nvmrc`.

Once `nvm` is installed, activate the correct version of NodeJS using:

```bash
cd ui
nvm use
```

Note: this needs to be done each time an interpreter is opened for development.

The user interface is developed using SvelteJS and Typescript. While we don't
strictly require type annotations, we recommend using them where possible, and are
progressively adding type annotations throughout the codebase.

To run the user interface in development mode:

```bash
npm run dev -- --open
```

This will automatically open the development version in your browser.

To run a static build of the user interface:

```bash
npm run build
npm preview -- --open
```

To check for outdated dependencies and upgrade them:

```bash
npm install -g npm-check-updates
ncu -i --cooldown 3
```

Note: this uses a 3 day "cooldown" to prevent upgrading to very recently released
versions; modify this on a selective basis to pull in a newer version that resolves
a vulnerability.
