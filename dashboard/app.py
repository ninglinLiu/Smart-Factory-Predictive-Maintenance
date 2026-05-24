"""Streamlit dashboard for Smart Factory Predictive Maintenance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.styles import RISK_LABELS, band_color, band_label, rul_band


def _init_session_state(test_pred: pd.DataFrame) -> None:
    engines = sorted(test_pred["unit_number"].unique().tolist())
    defaults = {
        "risk_threshold": 30,
        "selected_engines": engines[:3],
        "sensor_choice": "sensor_11",
        "risk_band_filter": "All",
        "drill_engine": engines[0] if engines else 1,
        "life_stage_filter": "All",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _fleet_status_table(test_pred: pd.DataFrame, threshold: int) -> pd.DataFrame:
    df = test_pred[["unit_number", "true_RUL", "pred_final"]].copy()
    df["risk_band"] = df["pred_final"].apply(lambda x: rul_band(float(x), threshold))
    df["status"] = df["risk_band"].map(band_label)
    df["abs_error"] = (df["pred_final"] - df["true_RUL"]).abs()
    return df.sort_values("pred_final")


@st.cache_data(show_spinner="Loading data and model...")
def load_assets():
    train = pd.read_csv(ROOT / "data/processed/SmartFactory_modeling.csv")
    test_pred = pd.read_csv(ROOT / "outputs/test_predictions.csv")
    fi = pd.read_csv(ROOT / "outputs/feature_importance.csv")
    test_metrics = pd.read_csv(ROOT / "outputs/test_metrics.csv")
    recs = pd.read_csv(ROOT / "outputs/recommendations_table_a2.csv")
    model = joblib.load(ROOT / "models/final_model.pkl")
    meta = json.loads((ROOT / "models/final_model_metadata.json").read_text(encoding="utf-8"))
    return train, test_pred, fi, test_metrics, recs, model, meta


def render_shared_filters(test_pred: pd.DataFrame, train: pd.DataFrame) -> None:
    """Sidebar filters shared across pages (cross-filtering via session_state)."""
    st.sidebar.header("Global Filters")
    st.sidebar.caption("Filters apply across Fleet Overview and Engine Detail.")

    st.session_state.risk_threshold = st.sidebar.slider(
        "RUL risk threshold (cycles)",
        10,
        60,
        int(st.session_state.risk_threshold),
        help="Engines below this value are Critical (red band).",
    )
    st.session_state.risk_band_filter = st.sidebar.selectbox(
        "Risk band filter",
        ["All", "Critical", "Watch", "Healthy"],
        index=["All", "Critical", "Watch", "Healthy"].index(st.session_state.risk_band_filter),
        help="Colorblind-friendly bands: Critical / Watch / Healthy",
    )
    st.session_state.life_stage_filter = st.sidebar.selectbox(
        "Life-stage filter (train fleet)",
        ["All", "early", "mid", "late"],
        index=["All", "early", "mid", "late"].index(st.session_state.life_stage_filter),
        help="Filter training engines by lifecycle stage (EDA tertiles).",
    )

    engines = sorted(train["unit_number"].unique().tolist())
    st.session_state.selected_engines = st.sidebar.multiselect(
        "Engines to inspect",
        engines,
        default=[e for e in st.session_state.selected_engines if e in engines] or engines[:3],
    )
    st.session_state.sensor_choice = st.sidebar.selectbox(
        "Primary sensor",
        ["sensor_11", "sensor_4", "sensor_12", "sensor_7", "sensor_15"],
        index=["sensor_11", "sensor_4", "sensor_12", "sensor_7", "sensor_15"].index(
            st.session_state.sensor_choice
        ),
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Risk legend (colorblind-friendly)**")
    for key, (label, color, desc) in RISK_LABELS.items():
        st.sidebar.markdown(
            f"<span style='color:{color};font-weight:bold;'>{label}</span> — {desc}",
            unsafe_allow_html=True,
        )


def _apply_risk_filter(fleet: pd.DataFrame) -> pd.DataFrame:
    band_map = {"Critical": "red", "Watch": "yellow", "Healthy": "green"}
    if st.session_state.risk_band_filter != "All":
        fleet = fleet[fleet["risk_band"] == band_map[st.session_state.risk_band_filter]]
    return fleet


def page_fleet_overview(train, test_pred, test_metrics, meta):
    st.header("Fleet Overview")
    threshold = st.session_state.risk_threshold
    fleet = _fleet_status_table(test_pred, threshold)
    fleet = _apply_risk_filter(fleet)

    final_mae = test_metrics.loc[test_metrics["model"] == "Final", "MAE"].iloc[0]
    high_risk = int((test_pred["pred_final"] < threshold).sum())
    mean_rul = test_pred["pred_final"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Engines Monitored", str(len(test_pred)), help="NASA FD001 test fleet")
    c2.metric("Mean Predicted RUL", f"{mean_rul:.0f} cycles")
    c3.metric("Critical (below threshold)", str(high_risk))
    c4.metric("Model Test MAE", f"{final_mae:.1f} cycles", help=f"Model: {meta['model_name']}")
    c5.metric("Features Used", str(meta["n_features"]))

    st.subheader("Risk Distribution (color-coded bands)")
    plot_df = test_pred.copy()
    plot_df["band"] = plot_df["pred_final"].apply(lambda x: band_label(rul_band(float(x), threshold)))
    fig = px.histogram(
        plot_df,
        x="pred_final",
        color="band",
        nbins=20,
        title="Predicted RUL at Last Cycle — by Risk Band",
        labels={"pred_final": "Predicted RUL (cycles)", "band": "Status"},
        color_discrete_map={"Healthy": "#0072B2", "Watch": "#E69F00", "Critical": "#D55E00"},
        category_orders={"band": ["Healthy", "Watch", "Critical"]},
    )
    fig.add_vline(x=threshold, line_dash="dash", line_color="#333", annotation_text="Threshold")
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.subheader("Actual vs Predicted (click point → drill-down)")
        fig2 = px.scatter(
            fleet,
            x="true_RUL",
            y="pred_final",
            color="status",
            hover_data=["unit_number", "abs_error"],
            color_discrete_map={"Healthy": "#0072B2", "Watch": "#E69F00", "Critical": "#D55E00"},
            title="Test Set Accuracy (filtered fleet)",
        )
        max_v = max(fleet["true_RUL"].max(), fleet["pred_final"].max()) if len(fleet) else 1
        fig2.add_trace(
            go.Scatter(x=[0, max_v], y=[0, max_v], mode="lines", name="Perfect", line=dict(dash="dash", color="#666"))
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.subheader("Fleet Risk Table — drill-down")
        st.dataframe(
            fleet[["unit_number", "pred_final", "true_RUL", "status", "abs_error"]].rename(
                columns={
                    "unit_number": "Engine",
                    "pred_final": "Pred RUL",
                    "true_RUL": "True RUL",
                    "abs_error": "Abs Error",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
        engine_options = fleet["unit_number"].tolist() or test_pred["unit_number"].tolist()
        st.session_state.drill_engine = st.selectbox(
            "Drill-down: select engine for Engine Detail page",
            engine_options,
            index=engine_options.index(st.session_state.drill_engine)
            if st.session_state.drill_engine in engine_options
            else 0,
        )
        if st.button("Go to Engine Detail for selected engine"):
            st.session_state.selected_engines = [st.session_state.drill_engine]
            st.info(f"Switch to **Engine Detail** in the left navigation to inspect Engine {st.session_state.drill_engine}.")


def page_engine_detail(train, test_pred, model, meta):
    st.header("Engine Detail")
    threshold = st.session_state.risk_threshold
    sensor_choice = st.session_state.sensor_choice
    selected = st.session_state.selected_engines

    if st.session_state.drill_engine not in selected:
        selected = [st.session_state.drill_engine] + [e for e in selected if e != st.session_state.drill_engine]

    if st.session_state.life_stage_filter != "All":
        stage_engines = train.loc[train["life_stage"] == st.session_state.life_stage_filter, "unit_number"].unique()
        selected = [e for e in selected if e in stage_engines]
        if not selected:
            st.warning("No selected engines match the life-stage filter.")
            return

    if not selected:
        st.warning("Select at least one engine in the sidebar.")
        return

    features = meta["features"]
    for uid in selected[:5]:
        eng = train[train["unit_number"] == uid]
        if eng.empty:
            continue
        preds = model.predict(eng[features])
        last_rul = float(preds[-1])
        band = rul_band(last_rul, threshold)
        color = band_color(band)
        label = band_label(band)

        st.markdown(
            f"### Engine {uid} — **{label}** "
            f"<span style='color:{color};'>(predicted RUL {last_rul:.0f} cycles)</span>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=eng["time_in_cycles"], y=eng[sensor_choice], name=sensor_choice, line=dict(color="#0072B2"))
            )
            roll_col = f"{sensor_choice}_roll20"
            if roll_col in eng.columns:
                fig.add_trace(
                    go.Scatter(
                        x=eng["time_in_cycles"],
                        y=eng[roll_col],
                        name="20-cycle rolling mean",
                        line=dict(dash="dash", color="#E69F00"),
                    )
                )
            fig.update_layout(title=f"{sensor_choice} trend", xaxis_title="Cycle", yaxis_title="Sensor value")
            st.plotly_chart(fig, use_container_width=True, key=f"sensor_{uid}")

        with col2:
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(x=eng["time_in_cycles"], y=preds, name="Predicted RUL", line=dict(color="#D55E00"))
            )
            fig2.add_hline(y=threshold, line_dash="dot", line_color="#E69F00", annotation_text="Critical threshold")
            fig2.add_hline(y=60, line_dash="dot", line_color="#0072B2", annotation_text="Healthy band (≥60)")
            fig2.update_layout(title="Predicted RUL trajectory", xaxis_title="Cycle", yaxis_title="RUL (cycles)")
            st.plotly_chart(fig2, use_container_width=True, key=f"rul_{uid}")

        if band == "red":
            st.error(
                f"MAINTENANCE: Schedule inspection for Engine {uid} — RUL {last_rul:.0f} < {threshold} cycles (Critical)."
            )
        elif band == "yellow":
            st.warning(f"WATCH: Engine {uid} entering degradation window (RUL {last_rul:.0f} cycles).")
        else:
            st.success(f"HEALTHY: Engine {uid} — RUL {last_rul:.0f} cycles.")


def page_model_insights(fi, test_pred, meta):
    st.header("Model Insights")
    threshold = st.session_state.risk_threshold
    fleet = _apply_risk_filter(_fleet_status_table(test_pred, threshold))

    st.subheader("Feature Importance (permutation)")
    top = fi.head(15)
    fig = px.bar(
        top,
        x="perm_importance_mean",
        y="feature",
        orientation="h",
        title="Top 15 features — final Random Forest model",
        color_discrete_sequence=["#0072B2"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Error Analysis — filtered fleet worst predictions")
    if fleet.empty:
        st.info("No engines match current risk-band filter.")
    else:
        worst = fleet.nlargest(10, "abs_error")[["unit_number", "true_RUL", "pred_final", "status", "abs_error"]]
        st.dataframe(worst, use_container_width=True, hide_index=True)

    st.subheader("What-if sensitivity")
    offset = st.slider("Hypothetical sensor_11 offset", -5.0, 5.0, 0.0, 0.1)
    st.info(
        f"Offset {offset:+.1f} on sensor_11 would require model re-inference in production. "
        "Use this panel to discuss sensor sensitivity with stakeholders."
    )


def page_recommendations(recs):
    st.header("Business Recommendations")
    st.caption("Linked to modelling outputs — prioritised for Maintenance Director and Plant Manager.")
    for _, row in recs.iterrows():
        badge = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(row["priority"], "⚪")
        with st.expander(f"{badge} {row['id']}: {row['title']} [{row['priority']}]"):
            st.markdown(f"**Problem:** {row['problem']}")
            st.markdown(f"**Solution:** {row['solution']}")
            st.markdown(f"**Expected Impact:** {row['expected_impact']}")
            st.markdown(f"**Implementation:** {row['implementation']}")
            st.markdown(f"**Timeline:** {row['timeline']} | **Owner:** {row['owner']}")
            st.markdown(f"**Evidence:** {row['evidence']}")


def main():
    st.set_page_config(page_title="Smart Factory Predictive Maintenance", layout="wide", page_icon="🏭")

    try:
        train, test_pred, fi, test_metrics, recs, model, meta = load_assets()
    except Exception as e:
        st.error(f"Failed to load assets. Run `python scripts/run_assignment2_pipeline.py` first.\n\n{e}")
        st.stop()

    _init_session_state(test_pred)
    render_shared_filters(test_pred, train)

    st.title("Smart Factory Predictive Maintenance Dashboard")
    st.caption("NASA C-MAPSS FD001 — Assignment 2 | Colorblind-friendly R/Y/G risk bands")

    def render_fleet_overview():
        page_fleet_overview(train, test_pred, test_metrics, meta)

    def render_engine_detail():
        page_engine_detail(train, test_pred, model, meta)

    def render_model_insights():
        page_model_insights(fi, test_pred, meta)

    def render_recommendations():
        page_recommendations(recs)

    pg = st.navigation(
        {
            "Dashboard": [
                st.Page(render_fleet_overview, title="Fleet Overview", icon="📊", url_path="fleet-overview"),
                st.Page(render_engine_detail, title="Engine Detail", icon="🔧", url_path="engine-detail"),
                st.Page(render_model_insights, title="Model Insights", icon="🧠", url_path="model-insights"),
                st.Page(render_recommendations, title="Recommendations", icon="📋", url_path="recommendations"),
            ]
        }
    )
    pg.run()


if __name__ == "__main__":
    main()
