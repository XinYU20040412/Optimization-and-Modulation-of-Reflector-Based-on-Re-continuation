from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import GeometryConfig, SamplingConfig


@dataclass
class AcceptanceResult:
    label: str
    x: np.ndarray
    y: np.ndarray
    landing_y: np.ndarray
    accepted_mask: np.ndarray
    ratio: float


def parabola_profile(x: np.ndarray, geo: GeometryConfig) -> np.ndarray:
    return geo.parabola_c3 * x**3 + geo.parabola_c2 * x**2 + geo.parabola_c1 * x


def sphere_profile(x: np.ndarray, geo: GeometryConfig) -> np.ndarray:
    inside = np.clip(geo.sphere_radius**2 - x**2, a_min=0.0, a_max=None)
    return geo.sphere_radius - np.sqrt(inside)


def build_profiles(geo: GeometryConfig, sampling: SamplingConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_work = np.arange(0.0, sampling.work_x_max, sampling.work_step, dtype=np.float64)
    x_base = np.arange(0.0, sampling.base_x_max, sampling.base_step, dtype=np.float64)

    y_work = parabola_profile(x_work, geo)
    y_base = sphere_profile(x_base, geo)
    return x_work, y_work, x_base, y_base


def _landing_y(x: np.ndarray, y: np.ndarray, h0: float) -> np.ndarray:
    dy_dx = np.gradient(y, x, edge_order=2)
    tan1 = dy_dx
    tan = (1.0 - tan1**2) / (2.0 * tan1)

    # Avoid unstable division near grazing reflection points.
    tan = np.where(np.abs(tan) < 1e-12, np.nan, tan)
    delta_x = (h0 - y) / tan
    return delta_x - x


def compute_acceptance_vectorized(
    x: np.ndarray,
    y: np.ndarray,
    h0: float,
    half_window: float,
    label: str,
) -> AcceptanceResult:
    landing = _landing_y(x, y, h0)
    mask = np.isfinite(landing) & (landing >= -half_window) & (landing <= half_window)
    ratio = float(np.mean(mask))
    return AcceptanceResult(label=label, x=x, y=y, landing_y=landing, accepted_mask=mask, ratio=ratio)


def compute_acceptance_loop(
    x: np.ndarray,
    y: np.ndarray,
    h0: float,
    half_window: float,
    label: str,
) -> AcceptanceResult:
    dy_dx = np.gradient(y, x, edge_order=2)
    landing = np.empty_like(x)
    mask = np.zeros_like(x, dtype=bool)

    for i in range(x.size):
        tan1 = dy_dx[i]
        tan = (1.0 - tan1 * tan1) / (2.0 * tan1)

        if abs(tan) < 1e-12:
            landing[i] = np.nan
            continue

        delta_h = h0 - y[i]
        delta_x = delta_h / tan
        yy = delta_x - x[i]
        landing[i] = yy

        if -half_window <= yy <= half_window:
            mask[i] = True

    ratio = float(np.mean(mask))
    return AcceptanceResult(label=label, x=x, y=y, landing_y=landing, accepted_mask=mask, ratio=ratio)
