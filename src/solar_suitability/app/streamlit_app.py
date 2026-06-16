from __future__ import annotations

from pathlib import Path

import pandas as pd


OUTPUT_DIR = Path("outputs")
EXPECTED_OUTPUTS = [
    "suitability_grid.parquet",
    "suitability_grid.csv",
    "candidate_sites.geojson",
    "layer_summary.csv",
    "methodology_report.md",
]


def load_grid(output_dir: str = "outputs") -> pd.DataFrame:
    root = Path(output_dir)
    parquet_path = root / "suitability_grid.parquet"
    csv_path = root / "suitability_grid.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()


def load_report(output_dir: str = "outputs") -> str:
    path = Path(output_dir) / "methodology_report.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def main() -> None:
    import plotly.express as px
    import streamlit as st

    st.set_page_config(page_title="Portugal Solar Suitability", layout="wide")
    grid = load_grid(str(OUTPUT_DIR))

    st.title("Mainland Portugal Solar Suitability")
    st.info(
        "Demo mode: this MVP uses bundled sample candidates so the app is runnable before the large GIS data "
        "pipeline is implemented. Use the real-data source registry as the next phase input."
    )

    if grid.empty:
        st.warning("No model outputs were found.")
        st.code("solar-suitability build --sample", language="bash")
        st.write("Expected files:")
        st.write([str(OUTPUT_DIR / name) for name in EXPECTED_OUTPUTS])
        return

    include_excluded = st.sidebar.checkbox("Show excluded cells", value=False)
    min_score = st.sidebar.slider("Minimum suitability score", 0.0, 1.0, 0.0, 0.05)
    layer = st.sidebar.selectbox(
        "Map layer",
        ["suitability_score", "mean_pvout_kwh_kwp_year", "nearest_grid_m", "nearest_road_m", "area_ha"],
    )

    view = grid.copy()
    if "excluded" in view.columns:
        view["excluded"] = view["excluded"].astype(bool)
    if "excluded" in view.columns and not include_excluded:
        view = view[~view["excluded"]]
    if "suitability_score" in view.columns:
        view = view[view["suitability_score"] >= min_score]

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Candidate cells", f"{len(view):,}")
    kpi_cols[1].metric("Best score", f"{grid['suitability_score'].max():.2f}")
    kpi_cols[2].metric("Mean PVOUT", _format_number(view.get("mean_pvout_kwh_kwp_year")))
    kpi_cols[3].metric("Mean area ha", _format_number(view.get("area_ha")))

    if view.empty:
        st.warning("No cells match the current filters. Lower the score threshold or show excluded cells.")
    else:
        fig = px.scatter_mapbox(
            view,
            lat="lat",
            lon="lon",
            color=layer,
            size="area_ha" if "area_ha" in view.columns else None,
            hover_name="name" if "name" in view.columns else "cell_id",
            hover_data=[
                column
                for column in ["suitability_score", "nearest_grid_m", "nearest_road_m", "mean_pvout_kwh_kwp_year"]
                if column in view.columns
            ],
            mapbox_style="open-street-map",
            zoom=6,
            height=560,
        )
        fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)

    table_cols = [
        column
        for column in [
            "name",
            "cell_id",
            "suitability_score",
            "area_ha",
            "mean_pvout_kwh_kwp_year",
            "nearest_grid_m",
            "nearest_road_m",
            "slope_degrees",
            "aspect_degrees",
            "corine_class",
            "excluded",
            "protected_area",
            "slope_too_steep",
            "unsuitable_landcover",
        ]
        if column in view.columns
    ]
    st.dataframe(
        view.sort_values("suitability_score", ascending=False)[table_cols],
        use_container_width=True,
        hide_index=True,
    )

    report = load_report(str(OUTPUT_DIR))
    with st.expander("Methodology report", expanded=False):
        if report:
            st.markdown(report)
        else:
            st.write("Run `solar-suitability build --sample` to generate the methodology report.")


def _format_number(series: pd.Series | None) -> str:
    if series is None or len(series.dropna()) == 0:
        return "n/a"
    return f"{series.mean():,.0f}"


if __name__ == "__main__":
    main()
