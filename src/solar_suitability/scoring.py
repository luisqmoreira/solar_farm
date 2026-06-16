from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


DEFAULT_EXCLUSION_FLAGS = (
    "outside_mainland",
    "protected_area",
    "water_or_wetland",
    "built_or_urban",
    "slope_too_steep",
    "unsuitable_landcover",
    "buffered_road_or_building",
)


def normalize_values(values: Sequence[float | int | None], *, higher_is_better: bool = True) -> list[float]:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return [0.0 for _ in values]

    min_value = min(numeric)
    max_value = max(numeric)
    if max_value == min_value:
        return [1.0 if value is not None else 0.0 for value in values]

    normalized: list[float] = []
    for value in values:
        if value is None:
            normalized.append(0.0)
            continue
        score = (float(value) - min_value) / (max_value - min_value)
        normalized.append(score if higher_is_better else 1 - score)
    return normalized


def has_exclusion(record: Mapping[str, Any], flags: Iterable[str] = DEFAULT_EXCLUSION_FLAGS) -> bool:
    return any(bool(record.get(flag, False)) for flag in flags)


def weighted_score(record: Mapping[str, Any], weights: Mapping[str, float]) -> float:
    total_weight = sum(float(value) for value in weights.values() if value > 0)
    if total_weight <= 0:
        raise ValueError("weights must sum to a positive value")

    score = 0.0
    for field, weight in weights.items():
        score += float(record.get(field, 0.0) or 0.0) * float(weight)
    return max(0.0, min(1.0, score / total_weight))


def score_records(
    records: Sequence[Mapping[str, Any]],
    weights: Mapping[str, float],
    *,
    exclusion_flags: Iterable[str] = DEFAULT_EXCLUSION_FLAGS,
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for record in records:
        row = dict(record)
        excluded = has_exclusion(row, exclusion_flags)
        row["excluded"] = excluded
        row["suitability_score"] = 0.0 if excluded else weighted_score(row, weights)
        scored.append(row)
    return scored


def landcover_score(corine_class: int | str | None, preferred_classes: Iterable[int]) -> float:
    if corine_class is None:
        return 0.0
    try:
        code = int(corine_class)
    except (TypeError, ValueError):
        return 0.0
    return 1.0 if code in {int(item) for item in preferred_classes} else 0.35


def aspect_south_score(aspect_degrees: float | int | None) -> float:
    if aspect_degrees is None:
        return 0.0
    distance = abs((float(aspect_degrees) - 180 + 180) % 360 - 180)
    return max(0.0, 1.0 - distance / 180.0)
