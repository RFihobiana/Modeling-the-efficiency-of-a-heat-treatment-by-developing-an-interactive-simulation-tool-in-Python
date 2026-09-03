"""Streamlit app for interactive heat-treatment simulation visualization."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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

col1, col2 = st.columns([3, 1])

with col1:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.semilogy(times, N, label=f"T={T} °C")
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Survivors (N)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    fig2, ax2 = plt.subplots(figsize=(8, 2.5))
    ax2.plot(times, np.log10(N0 / N))
    ax2.set_xlabel("Time (min)")
    ax2.set_ylabel("Log10 reduction")
    ax2.grid(True)
    st.pyplot(fig2)

with col2:
    st.metric("Final survivors (N)", f"{N_end:.3g}")
    st.metric("Log10 reduction", f"{log_red:.2f}")
    st.metric("Time to 5-log reduction (min)", f"{time_5log:.1f}")

    st.download_button("Download curve CSV", data=pd.DataFrame({"time_min": times, "N": N}).to_csv(index=False), file_name="survival_curve.csv")

st.markdown("---")
st.markdown("## Model details")
st.write(
    "This model uses a log-linear inactivation model with D- and z-values: ``N(t)=N0*10^(-t/D(T))`` and ``D(T)=D_ref*10^((T_ref-T)/z)``."
)
