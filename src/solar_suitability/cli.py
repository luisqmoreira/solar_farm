from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

from solar_suitability.build import RealPipelineNotImplemented, build_real_outputs, build_sample_outputs
from solar_suitability.config import load_model_config, load_sources_config
from solar_suitability.download import download_sources, write_manifest
from solar_suitability.geo import missing_real_datasets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="solar-suitability")
    parser.add_argument("--model-config", default="config/model.yml")
    parser.add_argument("--sources-config", default="config/sources.yml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser("download", help="Download configured open-data sources.")
    download_parser.add_argument("--source", action="append", help="Download only this source id; can be repeated.")
    download_parser.add_argument("--allow-large", action="store_true", help="Allow large configured downloads.")
    download_parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded.")
    download_parser.add_argument("--manifest", default="data/raw/download_manifest.json")

    build_parser = subparsers.add_parser("build", help="Build suitability outputs.")
    build_mode = build_parser.add_mutually_exclusive_group()
    build_mode.add_argument("--sample", action="store_true", help="Build from bundled sample records.")
    build_mode.add_argument("--real", action="store_true", help="Attempt the full real-data GIS build.")
    build_parser.add_argument("--output-dir", default="outputs")

    app_parser = subparsers.add_parser("app", help="Run the Streamlit exploration app.")
    app_parser.add_argument("--server-port", default="8501")

    doctor_parser = subparsers.add_parser("doctor", help="Check MVP and real-data readiness.")
    doctor_parser.add_argument("--output-dir", default="outputs")

    args = parser.parse_args(argv)

    if args.command == "download":
        sources_config = load_sources_config(args.sources_config)
        selected = set(args.source) if args.source else None
        results = download_sources(
            sources_config["sources"],
            selected=selected,
            allow_large=args.allow_large,
            dry_run=args.dry_run,
        )
        write_manifest(results, args.manifest)
        for result in results:
            print(f"{result.source}: {result.status} - {result.message}")
        print(f"Manifest written to {args.manifest}")
        return 0

    if args.command == "build":
        model_config = load_model_config(args.model_config)
        if not args.real:
            paths = build_sample_outputs(model_config, args.output_dir)
        else:
            sources_config = load_sources_config(args.sources_config)
            try:
                paths = build_real_outputs(sources_config, model_config, output_dir=args.output_dir)
            except (FileNotFoundError, RealPipelineNotImplemented) as exc:
                print(str(exc), file=sys.stderr)
                return 2
        for name, path in paths.items():
            print(f"{name}: {path}")
        return 0

    if args.command == "doctor":
        model_config = load_model_config(args.model_config)
        sources_config = load_sources_config(args.sources_config)
        return run_doctor(model_config, sources_config, Path(args.output_dir))

    if args.command == "app":
        app_path = Path(__file__).parent / "app" / "streamlit_app.py"
        _ensure_local_streamlit_activation()
        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(args.server_port),
            "--browser.gatherUsageStats",
            "false",
            "--server.headless",
            "true",
            "--server.showEmailPrompt",
            "false",
        ]
        env = {
            **os.environ,
            "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
            "STREAMLIT_SERVER_HEADLESS": "true",
            "STREAMLIT_SERVER_SHOW_EMAIL_PROMPT": "false",
        }
        return subprocess.call(command, env=env)

    parser.error(f"Unknown command: {args.command}")
    return 2


def run_doctor(model_config: dict, sources_config: dict, output_dir: Path) -> int:
    package_checks = {
        "pandas": "pandas",
        "streamlit": "streamlit",
        "plotly": "plotly",
        "pyarrow": "pyarrow",
        "yaml": "PyYAML",
        "requests": "requests",
        "pytest": "pytest",
    }
    geo_checks = {
        "geopandas": "geopandas",
        "rasterio": "rasterio",
        "pyproj": "pyproj",
        "shapely": "shapely",
    }
    grid_outputs = [output_dir / "suitability_grid.parquet", output_dir / "suitability_grid.csv"]
    required_outputs = [
        output_dir / "candidate_sites.geojson",
        output_dir / "layer_summary.csv",
        output_dir / "methodology_report.md",
    ]

    print("Solar Suitability Doctor")
    print("========================")
    print(f"Region: {model_config['region']['name']}")
    print(f"Output directory: {output_dir}")
    print("")

    print("MVP dependencies")
    mvp_ready = True
    for module, label in package_checks.items():
        installed = importlib.util.find_spec(module) is not None
        mvp_ready = mvp_ready and installed
        print(f"  {'OK' if installed else 'MISSING'} {label}")

    print("")
    print("Optional real-GIS dependencies")
    for module, label in geo_checks.items():
        installed = importlib.util.find_spec(module) is not None
        print(f"  {'OK' if installed else 'MISSING'} {label}")

    print("")
    print("Output files")
    grid_ready = any(path.exists() for path in grid_outputs)
    for path in grid_outputs:
        exists = path.exists()
        print(f"  {'OK' if exists else 'MISSING'} {path}")
    outputs_ready = grid_ready
    for path in required_outputs:
        exists = path.exists()
        outputs_ready = outputs_ready and exists
        print(f"  {'OK' if exists else 'MISSING'} {path}")

    print("")
    print("Real-data sources")
    missing_sources = missing_real_datasets(sources_config)
    if missing_sources:
        for dataset in missing_sources:
            print(f"  MISSING {dataset.key}: {dataset.path}")
    else:
        print("  OK configured source files are present")

    print("")
    if mvp_ready and outputs_ready:
        print("MVP status: ready. Run `solar-suitability app`.")
        return 0

    print("MVP status: action needed.")
    if not mvp_ready:
        print("Install dependencies with `python -m pip install -r requirements.txt`.")
    if not outputs_ready:
        print("Create demo outputs with `solar-suitability build --sample`.")
    return 1


def _ensure_local_streamlit_activation() -> None:
    credentials_path = Path(".streamlit") / "credentials.toml"
    config_path = Path(".streamlit") / "config.toml"
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    if not credentials_path.exists():
        credentials_path.write_text("[general]\nemail = \"\"\n", encoding="utf-8")
    if not config_path.exists():
        config_path.write_text(
            "[browser]\ngatherUsageStats = false\n\n[server]\nheadless = true\nshowEmailPrompt = false\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    raise SystemExit(main())
