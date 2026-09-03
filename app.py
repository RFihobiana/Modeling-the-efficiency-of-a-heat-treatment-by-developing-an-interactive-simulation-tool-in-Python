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

st.markdown(
    """
    ### Quick guide (for everyone)

    This tool shows how heating (time + temperature) can reduce the number of microbes in food. Use the sliders to try different cooking temperatures and times. Advanced technical settings are tucked under "Advanced settings".

    - "Initial microbes": an estimate of how many microorganisms are present before heating (per serving). Leave the default if you're unsure.
    - "Temperature" and "Time": pick the cooking temperature and how long you hold it.
    - "Final survivors": an estimate of how many microbes may remain after the treatment.
    - "Log10 reduction": each "log" is a 10× reduction. 1-log = 90% removed, 2-log = 99% removed, 5-log = 99.999% removed.
    """
)

with st.sidebar:
    st.header("Controls")
    # Friendly inputs
    N0 = st.number_input(
        "Initial microbes (approx., per serving)",
        value=1e6,
        format="%.0f",
        help="Approximate number of microorganisms in the food before heating. Typical household users can leave this as the default.",
    )
    T = st.slider("Temperature (°C)", min_value=40.0, max_value=100.0, value=72.0)
    t_max = st.slider("Heating time (minutes)", min_value=1, max_value=240, value=60)

    st.markdown("---")
    st.subheader("Presets (everyday examples)")
    preset = st.selectbox(
        "Choose a friendly preset",
        options=[
            "Default (general)",
            "Gentle (home cooking)",
            "Conservative (extra safety)",
            "Strict (industrial-style)",
        ],
        help="Presets set recommended values for how resistant the target microbes are. These are illustrative only.",
    )

    # Map presets to D_ref, T_ref, z
    if preset == "Gentle (home cooking)":
        D_ref, T_ref, z = 5.0, 70.0, 10.0
    elif preset == "Conservative (extra safety)":
        D_ref, T_ref, z = 10.0, 70.0, 8.0
    elif preset == "Strict (industrial-style)":
        D_ref, T_ref, z = 0.5, 70.0, 12.0
    else:
        D_ref, T_ref, z = 5.0, 70.0, 10.0

    with st.expander("Advanced settings (for experts)"):
        D_ref = st.number_input("D_ref (min)", value=float(D_ref), step=0.1, help="D-value: minutes at reference temperature to reduce survivors by 10×.")
        T_ref = st.number_input("T_ref (°C)", value=float(T_ref), step=0.1, help="Reference temperature for the D-value.")
        z = st.number_input("z-value (°C)", value=float(z), step=0.1, help="z-value: temperature change that changes D by 10×.")
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

    st.plotly_chart(fig, width="stretch")

    # Log reduction plot
    fig2 = px.line(df, x="time_min", y="log_reduction", template="plotly_white", labels={"time_min": "Time (min)", "log_reduction": "Log10 reduction"})
    fig2.update_traces(line=dict(color="#2ca02c", width=3))
    st.plotly_chart(fig2, width="stretch")

with col2:
    st.metric("Estimated survivors after heating (N)", f"{N_end:.3g}")
    st.metric("Reduction (log10)", f"{log_red:.2f}")
    st.metric("Time to 5-log reduction (min)", f"{time_5log:.1f}")

    st.download_button("Download curve CSV", data=df.to_csv(index=False), file_name="survival_curve.csv")

    st.markdown("---")
    st.markdown("### What these numbers mean (plain language)")
    st.write(
        "- `Estimated survivors after heating`: how many microorganisms might remain per serving after the chosen treatment.\n"
        "- `Reduction (log10)`: how many 10× reductions occurred (e.g., 5-log means ~99.999% removed).\n"
        "- Use higher temperature or longer time to reduce more microbes."
    )

st.markdown("---")
st.markdown("## Model details")
st.write(
    "This model uses a log-linear inactivation model with D- and z-values: ``N(t)=N0*10^(-t/D(T))`` and ``D(T)=D_ref*10^((T_ref-T)/z)``."
)
