from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DownloadResult:
    source: str
    status: str
    output: str | None
    message: str


def download_sources(
    sources: dict[str, Any],
    *,
    root: str | Path = ".",
    selected: set[str] | None = None,
    allow_large: bool = False,
    dry_run: bool = False,
) -> list[DownloadResult]:
    root_path = Path(root)
    results: list[DownloadResult] = []
    for source_id, definition in sources.items():
        if selected and source_id not in selected:
            continue
        results.append(_download_one(source_id, definition, root_path, allow_large=allow_large, dry_run=dry_run))
    return results


def write_manifest(results: list[DownloadResult], path: str | Path) -> None:
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps([result.__dict__ for result in results], indent=2) + "\n",
        encoding="utf-8",
    )


def _download_one(
    source_id: str,
    definition: dict[str, Any],
    root: Path,
    *,
    allow_large: bool,
    dry_run: bool,
) -> DownloadResult:
    kind = definition.get("kind")
    output = definition.get("output")

    if kind == "manual":
        return DownloadResult(
            source_id,
            "manual",
            output,
            f"Manual download required: {definition.get('landing_page', 'no landing page configured')}",
        )

    if kind == "api_template":
        return DownloadResult(
            source_id,
            "template",
            output,
            "API template configured; build step samples it per grid centroid rather than downloading one bulk file.",
        )

    if definition.get("large") and not allow_large:
        return DownloadResult(source_id, "skipped_large", output, "Pass --allow-large to download this large source.")

    if kind == "protected_planet_api":
        token_env = definition.get("token_env", "PROTECTED_PLANET_TOKEN")
        token = os.environ.get(token_env)
        if not token:
            return DownloadResult(source_id, "missing_token", output, f"Set {token_env} to download this source.")
        url = definition["endpoint"]
        return _download_url(source_id, url, output, root, dry_run=dry_run, params={"token": token})

    if kind == "url":
        return _download_url(source_id, definition["url"], output, root, dry_run=dry_run)

    return DownloadResult(source_id, "unsupported", output, f"Unsupported source kind: {kind}")


def _download_url(
    source_id: str,
    url: str,
    output: str | None,
    root: Path,
    *,
    dry_run: bool,
    params: dict[str, str] | None = None,
) -> DownloadResult:
    if not output:
        return DownloadResult(source_id, "error", None, "No output path configured")

    output_path = root / output
    if dry_run:
        return DownloadResult(source_id, "dry_run", str(output_path), f"Would download {url}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError("requests is required for downloads; install the project dependencies first") from exc

    with requests.get(url, params=params, stream=True, timeout=60) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)

    return DownloadResult(source_id, "downloaded", str(output_path), f"Downloaded {url}")
