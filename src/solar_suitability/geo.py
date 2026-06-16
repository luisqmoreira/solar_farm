from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RequiredDataset:
    key: str
    path: Path
    description: str


def required_real_datasets(config: dict[str, Any], root: str | Path = ".") -> list[RequiredDataset]:
    root_path = Path(root)
    return [
        RequiredDataset(source_id, root_path / definition["output"], definition.get("description", source_id))
        for source_id, definition in config["sources"].items()
        if definition.get("required") and definition.get("kind") != "api_template"
    ]


def missing_real_datasets(config: dict[str, Any], root: str | Path = ".") -> list[RequiredDataset]:
    return [dataset for dataset in required_real_datasets(config, root) if not dataset.path.exists()]


def create_grid_from_bbox(bounds: dict[str, float], cell_size_m: int, analysis_crs: str):
    """Create a projected square-cell grid from lon/lat bounds."""
    import geopandas as gpd
    from pyproj import Transformer
    from shapely.geometry import box

    transformer = Transformer.from_crs("EPSG:4326", analysis_crs, always_xy=True)
    minx, miny = transformer.transform(bounds["west"], bounds["south"])
    maxx, maxy = transformer.transform(bounds["east"], bounds["north"])

    cells = []
    cell_id = 0
    y = miny
    while y < maxy:
        x = minx
        while x < maxx:
            cells.append({"cell_id": f"cell_{cell_id:07d}", "geometry": box(x, y, x + cell_size_m, y + cell_size_m)})
            cell_id += 1
            x += cell_size_m
        y += cell_size_m

    return gpd.GeoDataFrame(cells, crs=analysis_crs)


def distance_to_nearest(source_gdf, target_gdf, output_column: str):
    if target_gdf.empty:
        source_gdf[output_column] = None
        return source_gdf

    target_union = target_gdf.to_crs(source_gdf.crs).union_all()
    source_gdf[output_column] = source_gdf.geometry.centroid.distance(target_union)
    return source_gdf
