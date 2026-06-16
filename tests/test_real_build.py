from solar_suitability.cli import main


def test_real_build_returns_clear_nonzero_status(capsys):
    exit_code = main(["build", "--real"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Required geospatial datasets are missing" in captured.err or "full GIS overlay is not implemented" in captured.err
