from solar_suitability.app.streamlit_app import load_grid
from solar_suitability.build import build_sample_outputs
from solar_suitability.config import load_model_config


def test_app_loads_sample_outputs(tmp_path):
    config = load_model_config("config/model.yml")
    build_sample_outputs(config, tmp_path)

    grid = load_grid(str(tmp_path))

    assert "suitability_score" in grid.columns
    assert len(grid) > 0
