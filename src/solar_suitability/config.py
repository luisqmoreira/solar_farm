from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal runtimes
    yaml = None


class ConfigError(ValueError):
    """Raised when a configuration file is missing required model fields."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        if yaml is not None:
            data = yaml.safe_load(handle) or {}
        else:
            data = _parse_simple_yaml(handle.read())

    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file must contain a mapping: {config_path}")

    return data


def load_model_config(path: str | Path = "config/model.yml") -> dict[str, Any]:
    config = load_yaml(path)
    _require(config, "region.analysis_crs")
    _require(config, "grid.cell_size_m")
    _require(config, "thresholds.max_slope_degrees")
    _require(config, "weights")
    validate_weights(config["weights"])
    return config


def load_sources_config(path: str | Path = "config/sources.yml") -> dict[str, Any]:
    config = load_yaml(path)
    _require(config, "sources")
    if not isinstance(config["sources"], dict):
        raise ConfigError("sources must be a mapping of source id to source definition")
    return config


def validate_weights(weights: dict[str, Any]) -> None:
    if not weights:
        raise ConfigError("At least one scoring weight is required")

    invalid = {name: value for name, value in weights.items() if not isinstance(value, (int, float)) or value < 0}
    if invalid:
        raise ConfigError(f"Weights must be non-negative numbers: {invalid}")

    if sum(float(value) for value in weights.values()) <= 0:
        raise ConfigError("Weight sum must be greater than zero")


def _require(config: dict[str, Any], dotted_path: str) -> None:
    current: Any = config
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ConfigError(f"Missing required config key: {dotted_path}")
        current = current[part]


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = []
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        lines.append((indent, raw_line.strip()))

    def parse_block(index: int, indent: int):
        if index >= len(lines):
            return {}, index
        if lines[index][1].startswith("- "):
            values = []
            while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
                values.append(_parse_scalar(lines[index][1][2:].strip()))
                index += 1
            return values, index

        result: dict[str, Any] = {}
        while index < len(lines):
            current_indent, stripped = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ConfigError(f"Unexpected indentation near: {stripped}")
            if ":" not in stripped:
                raise ConfigError(f"Expected key/value line: {stripped}")

            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            index += 1
            if raw_value:
                result[key] = _parse_scalar(raw_value)
            else:
                child, index = parse_block(index, indent + 2)
                result[key] = child
        return result, index

    parsed, final_index = parse_block(0, 0)
    if final_index != len(lines) or not isinstance(parsed, dict):
        raise ConfigError("Could not parse YAML config without PyYAML")
    return parsed


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value
