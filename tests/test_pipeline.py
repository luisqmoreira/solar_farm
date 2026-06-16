import pandas as pd

from solar_suitability.config import load_model_config
from solar_suitability.pipeline import prepare_scored_cells


def test_prepare_scored_cells_applies_threshold_exclusions():
    config = load_model_config("config/model.yml")
    cells = pd.DataFrame(
        [
            {
                "cell_id": "ok",
                "lat": 38.0,
                "lon": -8.0,
                "area_ha": 50,
                "mean_pvout_kwh_kwp_year": 1700,
                "slope_degrees": 2,
                "aspect_degrees": 180,
                "nearest_grid_m": 1000,
                "nearest_road_m": 500,
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
                "cell_id": "steep",
                "lat": 38.1,
                "lon": -8.1,
                "area_ha": 50,
                "mean_pvout_kwh_kwp_year": 1650,
                "slope_degrees": 20,
                "aspect_degrees": 180,
                "nearest_grid_m": 1000,
                "nearest_road_m": 500,
                "corine_class": 211,
                "outside_mainland": False,
                "protected_area": False,
                "water_or_wetland": False,
                "built_or_urban": False,
                "slope_too_steep": False,
                "unsuitable_landcover": False,
                "buffered_road_or_building": False,
            },
        ]
    )

    scored = prepare_scored_cells(cells, config)

    steep = scored[scored["cell_id"] == "steep"].iloc[0]
    ok = scored[scored["cell_id"] == "ok"].iloc[0]
    assert bool(steep["slope_too_steep"]) is True
    assert steep["suitability_score"] == 0
    assert ok["suitability_score"] > 0
