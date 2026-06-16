from solar_suitability.config import load_model_config, load_sources_config


def test_model_config_loads():
    config = load_model_config("config/model.yml")

    assert config["region"]["name"] == "mainland_portugal"
    assert config["grid"]["cell_size_m"] > 0
    assert sum(config["weights"].values()) > 0


def test_sources_config_loads():
    config = load_sources_config("config/sources.yml")

    assert "geofabrik_osm" in config["sources"]
    assert config["sources"]["protected_planet"]["token_env"] == "PROTECTED_PLANET_TOKEN"
