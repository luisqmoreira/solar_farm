from __future__ import annotations

from typing import Any

import pandas as pd

from solar_suitability.scoring import aspect_south_score, landcover_score, normalize_values, score_records


def prepare_scored_cells(cells: pd.DataFrame, model_config: dict[str, Any]) -> pd.DataFrame:
    """Convert raw cell metrics into normalized suitability scores."""
    scored = cells.copy()
    thresholds = model_config["thresholds"]
    landcover_config = model_config["landcover"]

    scored["pv_resource"] = normalize_values(scored["mean_pvout_kwh_kwp_year"].tolist(), higher_is_better=True)
    scored["slope"] = normalize_values(scored["slope_degrees"].tolist(), higher_is_better=False)
    scored["aspect"] = [aspect_south_score(value) for value in scored["aspect_degrees"]]
    scored["grid_distance"] = [
        _distance_score(value, thresholds["max_grid_distance_m"]) for value in scored["nearest_grid_m"]
    ]
    scored["road_distance"] = [
        _distance_score(value, thresholds["max_road_distance_m"]) for value in scored["nearest_road_m"]
    ]
    scored["landcover"] = [
        landcover_score(value, landcover_config["preferred_corine_classes"]) for value in scored["corine_class"]
    ]

    excluded_classes = {int(value) for value in landcover_config["excluded_corine_classes"]}
    scored["slope_too_steep"] = scored.get("slope_too_steep", False) | (
        scored["slope_degrees"] > thresholds["max_slope_degrees"]
    )
    scored["unsuitable_landcover"] = scored.get("unsuitable_landcover", False) | (
        scored["corine_class"].astype(int).isin(excluded_classes)
    )

    scored_records = score_records(
        scored.to_dict("records"),
        {key: float(value) for key, value in model_config["weights"].items()},
        exclusion_flags=model_config.get("exclusion_flags", ()),
    )
    return pd.DataFrame(scored_records).sort_values("suitability_score", ascending=False)


def _distance_score(distance_m: float | int | None, max_distance_m: float | int) -> float:
    if distance_m is None:
        return 0.0
    capped = min(float(distance_m), float(max_distance_m))
    return max(0.0, 1.0 - capped / float(max_distance_m))
