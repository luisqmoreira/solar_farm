import pytest


def test_create_grid_from_small_bbox_smoke():
    pytest.importorskip("geopandas")
    from solar_suitability.geo import create_grid_from_bbox

    grid = create_grid_from_bbox(
        {"west": -8.0, "south": 38.0, "east": -7.99, "north": 38.01},
        cell_size_m=500,
        analysis_crs="EPSG:3763",
    )

    assert len(grid) > 0
    assert grid.crs.to_string() == "EPSG:3763"
