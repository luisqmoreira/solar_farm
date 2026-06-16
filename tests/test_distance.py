from solar_suitability.distance import haversine_m, nearest_distance_m


def test_haversine_distance_for_one_degree_longitude_near_equator():
    distance = haversine_m(0, 0, 0, 1)

    assert 111_000 < distance < 112_000


def test_nearest_distance_returns_closest_target():
    distance = nearest_distance_m(38.0, -8.0, [(38.0, -8.2), (38.0, -8.01)])

    assert distance is not None
    assert distance < 1_000
