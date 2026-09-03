"""Streamlit app for interactive heat-treatment simulation visualization."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src import simulation as sim


st.set_page_config(page_title="Heat-treatment simulator", layout="wide")

st.title("Heat-treatment Efficiency Simulator")

with st.sidebar:
    st.header("Simulation parameters")
    N0 = st.number_input("Initial count (N0)", value=1e6, format="%.0f")
    T = st.slider("Temperature (°C)", min_value=40.0, max_value=100.0, value=72.0)
    t_max = st.slider("Max time (min)", min_value=1, max_value=240, value=60)
    D_ref = st.number_input("D_ref (min)", value=5.0, step=0.1)
    T_ref = st.number_input("T_ref (°C)", value=70.0, step=0.1)
    z = st.number_input("z-value (°C)", value=10.0, step=0.1)
    points = st.slider("Curve resolution (points)", min_value=50, max_value=2000, value=400)

times = np.linspace(0, t_max, int(points))
N = sim.survival_curve(N0=N0, D_ref=D_ref, T_ref=T_ref, z=z, times=times, T=T)

# Metrics
N_end = float(N[-1])
log_red = sim.log_reduction(N0, N_end)
time_5log = sim.time_to_log_reduction(5.0, D_ref, T_ref, T, z)

df = pd.DataFrame({"time_min": times, "N": N})
df["log_reduction"] = np.log10(N0 / df["N"])

col1, col2 = st.columns([3, 1])

with col1:
    # Survivor curve (log y) with filled area and nicer styling
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["time_min"],
            y=df["N"],
            mode="lines",
            name=f"Survivors at {T} °C",
            line=dict(color="#1f77b4", width=3),
            hovertemplate="Time: %{x:.2f} min<br>N: %{y:.2e}<extra></extra>",
        )
    )
    # filled area under curve (for visual weight)
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([df["time_min"], df["time_min"][::-1]]),
            y=np.concatenate([df["N"], np.full_like(df["N"], df["N"].min())[::-1]]),
            fill="toself",
            fillcolor="rgba(31,119,180,0.12)",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.update_layout(
        yaxis_type="log",
        template="plotly_white",
        margin=dict(l=40, r=10, t=50, b=40),
        xaxis_title="Time (min)",
        yaxis_title="Survivors (N)",
    )
    # highlight key point for final survivors
    fig.add_trace(
        go.Scatter(
            x=[df["time_min"].iloc[-1]],
            y=[df["N"].iloc[-1]],
            mode="markers+text",
            marker=dict(size=8, color="#ff7f0e"),
            text=[f"{df['N'].iloc[-1]:.2e}"],
            textposition="top right",
            showlegend=False,
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Log reduction plot
    fig2 = px.line(df, x="time_min", y="log_reduction", template="plotly_white", labels={"time_min": "Time (min)", "log_reduction": "Log10 reduction"})
    fig2.update_traces(line=dict(color="#2ca02c", width=3))
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.metric("Final survivors (N)", f"{N_end:.3g}")
    st.metric("Log10 reduction", f"{log_red:.2f}")
    st.metric("Time to 5-log reduction (min)", f"{time_5log:.1f}")

    st.download_button("Download curve CSV", data=df.to_csv(index=False), file_name="survival_curve.csv")

st.markdown("---")
st.markdown("## Model details")
st.write(
    "This model uses a log-linear inactivation model with D- and z-values: ``N(t)=N0*10^(-t/D(T))`` and ``D(T)=D_ref*10^((T_ref-T)/z)``."
)
