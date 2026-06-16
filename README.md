# Identifying Locations for Solar Farms

This repository started as a data-science bootcamp project for exploring solar
farm potential in Portugal. The original notebooks are preserved as legacy work.
The current implementation adds a reproducible, scripted suitability model for
utility-scale solar siting in mainland Portugal.

## What The New Pipeline Does

The v2 pipeline separates four concepts that were mixed together in the original
project:

- solar resource / expected PV yield
- physical buildability
- environmental and land-use exclusions
- proximity to grid and access infrastructure

The default model is a transparent weighted score. Hard exclusions are applied
first; excluded cells always receive a final suitability score of `0`.

## Project Layout

```text
config/
  model.yml       # CRS, grid, exclusions, thresholds, weights
  sources.yml     # open-data source registry and download metadata
src/solar_suitability/
  cli.py          # download/build/app commands
  scoring.py      # transparent weighted scoring
  geo.py          # geospatial grid and distance hooks
  build.py        # output generation
  app/            # Streamlit exploration app
data/
  raw/            # downloaded source data, ignored by git
  interim/        # intermediate geospatial files, ignored by git
  processed/      # processed model inputs, ignored by git
outputs/          # generated model outputs, ignored by git
tests/            # unit and smoke tests
```

## Setup

For the runnable MVP:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The full real-GIS model will need heavier geospatial packages. Install them only
when working on that next phase:

```bash
python -m pip install -e ".[geo]"
```

If local GDAL wheels are not available on your platform, install GDAL/GEOS/PROJ
through your package manager or Conda before installing `.[geo]`.

## Commands

Preview configured data sources:

```bash
solar-suitability download --dry-run
```

Download public sources where a direct URL/API is available:

```bash
solar-suitability download --allow-large
```

Some sources are API-gated or portal-based:

- `PROTECTED_PLANET_TOKEN` is required for Protected Planet.
- CORINE Land Cover and DEM inputs may need manual download into the paths
  documented in `config/sources.yml`.

Check local readiness:

```bash
solar-suitability doctor
```

Build app-ready sample outputs. `build` defaults to the sample dataset, so both
commands below are equivalent:

```bash
solar-suitability build
solar-suitability build --sample
```

The full real-data build is intentionally deferred in this MVP. `--real` checks
for configured source files and then reports that the OSM/CORINE/DEM/protected
area overlay is the next implementation phase.

Run the app:

```bash
solar-suitability app
```

Expected outputs:

```text
outputs/candidate_sites.geojson
outputs/suitability_grid.parquet
outputs/suitability_grid.csv
outputs/layer_summary.csv
outputs/methodology_report.md
```

## Model Defaults

The first implementation uses mainland Portugal only and projects analysis to
`EPSG:3763`. The default grid size is `1 km`. Hard exclusions include protected
areas, water/wetlands, built or urban areas, excessive slope, unsuitable CORINE
classes, and road/building buffers.

Default weighted score:

- PV resource: `35%`
- grid distance: `20%`
- slope: `15%`
- aspect: `10%`
- road distance: `10%`
- land cover: `10%`

These defaults live in `config/model.yml` and are designed to be easy to audit
and adjust.

## Tests

```bash
pytest
```

The tests cover configuration loading, scoring normalization, exclusion
precedence, distance calculations, sample output generation, and app data
loading.

## Legacy Files

The notebooks and scripts from the original bootcamp project remain in the repo
for traceability. They use absolute local paths and index-based joins, so the new
pipeline should be treated as the maintained implementation path.
