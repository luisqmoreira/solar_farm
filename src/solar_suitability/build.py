from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from solar_suitability.geo import missing_real_datasets
from solar_suitability.pipeline import prepare_scored_cells


SAMPLE_RECORDS: list[dict[str, Any]] = [
    {
        "cell_id": "sample_beja_001",
        "name": "Beja north candidate",
        "lat": 38.05,
        "lon": -7.88,
        "area_ha": 64.0,
        "slope_degrees": 2.5,
        "aspect_degrees": 175,
        "nearest_grid_m": 3600,
        "nearest_road_m": 850,
        "mean_pvout_kwh_kwp_year": 1715,
        "corine_class": 211,
        "outside_mainland": False,
        "protected_area": False,
        "water_or_wetland": False,
        "built_or_urban": False,
        "slope_too_steep": False,
        "unsuitable_landcover": False,
        "buffered_road_or_building": False,
    },
    {
        "cell_id": "sample_evora_001",
        "name": "Evora east candidate",
        "lat": 38.59,
        "lon": -7.72,
        "area_ha": 41.0,
        "slope_degrees": 4.0,
        "aspect_degrees": 150,
        "nearest_grid_m": 1800,
        "nearest_road_m": 1400,
        "mean_pvout_kwh_kwp_year": 1685,
        "corine_class": 212,
        "outside_mainland": False,
        "protected_area": False,
        "water_or_wetland": False,
        "built_or_urban": False,
        "slope_too_steep": False,
        "unsuitable_landcover": False,
        "buffered_road_or_building": False,
    },
    {
        "cell_id": "sample_setubal_001",
        "name": "Setubal excluded example",
        "lat": 38.45,
        "lon": -8.72,
        "area_ha": 33.0,
        "slope_degrees": 7.0,
        "aspect_degrees": 100,
        "nearest_grid_m": 1200,
        "nearest_road_m": 950,
        "mean_pvout_kwh_kwp_year": 1605,
        "corine_class": 321,
        "outside_mainland": False,
        "protected_area": True,
        "water_or_wetland": False,
        "built_or_urban": False,
        "slope_too_steep": False,
        "unsuitable_landcover": False,
        "buffered_road_or_building": False,
    },
]


def build_sample_outputs(model_config: dict[str, Any], output_dir: str | Path = "outputs") -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    grid = prepare_scored_cells(pd.DataFrame(SAMPLE_RECORDS), model_config)

    paths = {
        "grid_parquet": output_path / "suitability_grid.parquet",
        "grid_csv": output_path / "suitability_grid.csv",
        "candidates_geojson": output_path / "candidate_sites.geojson",
        "summary_csv": output_path / "layer_summary.csv",
        "report": output_path / "methodology_report.md",
    }

    try:
        grid.to_parquet(paths["grid_parquet"], index=False)
    except Exception:
        grid.to_csv(paths["grid_csv"], index=False)
    else:
        grid.to_csv(paths["grid_csv"], index=False)

    candidate_rows = grid[~grid["excluded"]].copy()
    _write_candidates_geojson(candidate_rows.to_dict("records"), paths["candidates_geojson"])
    _write_layer_summary(grid, paths["summary_csv"])
    _write_methodology_report(model_config, grid, paths["report"], sample=True)
    return paths


def build_real_outputs(
    sources_config: dict[str, Any],
    model_config: dict[str, Any],
    *,
    root: str | Path = ".",
    output_dir: str | Path = "outputs",
) -> dict[str, Path]:
    missing = missing_real_datasets(sources_config, root)
    if missing:
        details = "\n".join(f"- {item.key}: expected {item.path} ({item.description})" for item in missing)
        raise FileNotFoundError(
            "Required geospatial datasets are missing. Run `solar-suitability download --allow-large` "
            "where possible and place manual sources at the documented paths:\n"
            f"{details}"
        )

    # Once the source files are present, this hook can be expanded into the
    # full raster/vector overlay. Until then, it returns deterministic outputs
    # so the app and tests remain usable in a clean clone.
    return build_sample_outputs(model_config, output_dir=output_dir)


def _write_candidates_geojson(records: list[dict[str, Any]], path: Path) -> None:
    features = []
    for record in records:
        properties = {key: value for key, value in record.items() if key not in {"lat", "lon"}}
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [record["lon"], record["lat"]]},
                "properties": properties,
            }
        )
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}, indent=2) + "\n", encoding="utf-8")


def _write_layer_summary(grid: pd.DataFrame, path: Path) -> None:
    rows = [
        ("cells_total", int(len(grid))),
        ("cells_excluded", int(grid["excluded"].sum())),
        ("candidate_cells", int((~grid["excluded"]).sum())),
        ("max_suitability_score", float(grid["suitability_score"].max())),
        ("mean_candidate_pvout", float(grid.loc[~grid["excluded"], "mean_pvout_kwh_kwp_year"].mean())),
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def _write_methodology_report(model_config: dict[str, Any], grid: pd.DataFrame, path: Path, *, sample: bool) -> None:
    mode = "sample fixture" if sample else "full source data"
    weights = "\n".join(f"- `{key}`: {value}" for key, value in model_config["weights"].items())
    exclusions = "\n".join(f"- `{flag}`" for flag in model_config.get("exclusion_flags", []))
    path.write_text(
        "\n".join(
            [
                "# Solar Suitability Methodology",
                "",
                f"Build mode: {mode}.",
                "",
                "The model applies hard exclusions before calculating a transparent weighted score.",
                "",
                "## Hard Exclusions",
                exclusions,
                "",
                "## Weights",
                weights,
                "",
                "## Output Summary",
                f"- Total cells: {len(grid)}",
                f"- Candidate cells: {(~grid['excluded']).sum()}",
                f"- Best score: {grid['suitability_score'].max():.3f}",
                "",
            ]
        ),
        encoding="utf-8",
    )
