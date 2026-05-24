"""Streamlit dashboard components for Smart Factory predictive maintenance."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def kpi_row(df: pd.DataFrame, test_mae: float | None) -> None:
    n_engines = df["unit_number"].nunique()
    avg_rul = df["RUL"].mean() if "RUL" in df.columns else 0
    high_risk = (df["RUL"] <= 30).sum() if "RUL" in df.columns else 0
    cols = st.columns(5)
    cols[0].metric("Engines Monitored", f"{n_engines}")
    cols[1].metric("Avg RUL (cycles)", f"{avg_rul:.0f}")
    cols[2].metric("High Risk (RUL≤30)", f"{high_risk}")
    cols[3].metric("Model Test MAE", f"{test_mae:.1f}" if test_mae else "N/A")
    cols[4].metric("Total Readings", f"{len(df):,}")


def sensor_trend_chart(df: pd.DataFrame, sensor: str) -> go.Figure:
    roll_col = f"{sensor}_roll20"
    plot_df = df.sort_values("time_in_cycles")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df["time_in_cycles"], y=plot_df[sensor], mode="lines", name=sensor, opacity=0.5))
    if roll_col in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df["time_in_cycles"], y=plot_df[roll_col], mode="lines", name=f"{sensor} roll20"))
    fig.update_layout(title=f"{sensor} over lifecycle", xaxis_title="Cycle", yaxis_title="Reading")
    return fig


def feature_importance_chart(fi: pd.DataFrame) -> go.Figure:
    top = fi.head(12)
    fig = px.bar(top, x="perm_importance_mean", y="feature", orientation="h", title="Permutation Feature Importance")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig
