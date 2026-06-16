from pathlib import Path

from solar_suitability.build import build_sample_outputs
from solar_suitability.config import load_model_config


def test_build_sample_outputs(tmp_path: Path):
    config = load_model_config("config/model.yml")
    paths = build_sample_outputs(config, tmp_path)

    assert paths["candidates_geojson"].exists()
    assert paths["summary_csv"].exists()
    assert paths["report"].exists()
    assert paths["grid_csv"].exists()
