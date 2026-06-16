from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from solar_suitability.build import build_real_outputs, build_sample_outputs
from solar_suitability.config import load_model_config, load_sources_config
from solar_suitability.download import download_sources, write_manifest


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
    build_parser.add_argument("--sample", action="store_true", help="Build from bundled sample records.")
    build_parser.add_argument("--output-dir", default="outputs")

    app_parser = subparsers.add_parser("app", help="Run the Streamlit exploration app.")
    app_parser.add_argument("--server-port", default="8501")

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
        if args.sample:
            paths = build_sample_outputs(model_config, args.output_dir)
        else:
            sources_config = load_sources_config(args.sources_config)
            paths = build_real_outputs(sources_config, model_config, output_dir=args.output_dir)
        for name, path in paths.items():
            print(f"{name}: {path}")
        return 0

    if args.command == "app":
        app_path = Path(__file__).parent / "app" / "streamlit_app.py"
        command = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(args.server_port)]
        return subprocess.call(command)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
