from solar_suitability.cli import run_doctor
from solar_suitability.config import load_model_config, load_sources_config


def test_doctor_reports_missing_outputs(tmp_path, capsys):
    exit_code = run_doctor(load_model_config("config/model.yml"), load_sources_config("config/sources.yml"), tmp_path)
    captured = capsys.readouterr()

    assert exit_code in {0, 1}
    assert "Solar Suitability Doctor" in captured.out
    assert "Output files" in captured.out
