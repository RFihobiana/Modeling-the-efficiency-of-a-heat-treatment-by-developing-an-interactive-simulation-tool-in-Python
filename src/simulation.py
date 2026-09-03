"""Heat-treatment kinetics simulation utilities.

Implements basic first-order microbial inactivation kinetics using D- and z-values.
"""
from __future__ import annotations

import numpy as np
from typing import Iterable


def D_at_T(D_ref: float, T_ref: float, T: float, z: float) -> float:
    """Compute the D-value at temperature T using the z-value rule.

    D_ref: D-value (minutes) at reference temperature T_ref (°C).
    T: target temperature (°C).
    z: z-value (°C) — temperature change required to change D by 10x.
    """
    return D_ref * 10 ** ((T_ref - T) / z)


def survival_curve(
    N0: float,
    D_ref: float,
    T_ref: float,
    z: float,
    times: Iterable[float],
    T: float,
) -> np.ndarray:
    """Return survivor counts N(t) for each time in `times` at constant temperature T.

    Uses the log-linear model: N(t) = N0 * 10^(-t / D(T)).
    """
    D_T = D_at_T(D_ref, T_ref, T, z)
    times_arr = np.asarray(list(times), dtype=float)
    return N0 * 10 ** (-times_arr / D_T)


def log_reduction(N0: float, N: float) -> float:
    """Compute log10 reduction achieved from N0 to N (log10(N0/N))."""
    if N <= 0 or N0 <= 0:
        return float("inf")
    return float(np.log10(N0 / N))


def time_to_log_reduction(target_log_reduction: float, D_ref: float, T_ref: float, T: float, z: float) -> float:
    """Compute time (minutes) required to reach a given log-reduction at temperature T.

    For linear log-inactivation: time = D(T) * target_log_reduction
    """
    D_T = D_at_T(D_ref, T_ref, T, z)
    return float(D_T * target_log_reduction)


if __name__ == "__main__":
    # quick demo
    import matplotlib.pyplot as plt

    N0 = 1e6
    D_ref = 5.0
    T_ref = 70.0
    z = 10.0
    T = 72.0
    times = np.linspace(0, 60, 200)
    N = survival_curve(N0, D_ref, T_ref, z, times, T)
    plt.semilogy(times, N)
    plt.xlabel("Time (min)")
    plt.ylabel("Survivors (N)")
    plt.title(f"Survival at {T} °C")
    plt.grid(True)
    plt.show()
