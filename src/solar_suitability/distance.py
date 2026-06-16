from __future__ import annotations

from math import asin, cos, radians, sin, sqrt


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6_371_000
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return 2 * radius_m * asin(sqrt(a))


def nearest_distance_m(lat: float, lon: float, targets: list[tuple[float, float]]) -> float | None:
    if not targets:
        return None
    return min(haversine_m(lat, lon, target_lat, target_lon) for target_lat, target_lon in targets)
