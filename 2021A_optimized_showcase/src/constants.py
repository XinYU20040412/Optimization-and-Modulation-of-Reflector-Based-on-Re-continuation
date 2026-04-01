from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeometryConfig:
    """Core geometry parameters inherited from the original scripts."""

    parabola_c3: float = 1.29916e-6
    parabola_c2: float = 0.001551445
    parabola_c1: float = 0.005647238

    sphere_radius: float = 300.0
    h0_scale: float = 0.466
    h0_radius_ref: float = 300.4
    h0_bias: float = 0.3786
    receiver_half_window: float = 0.5

    @property
    def h0(self) -> float:
        return self.h0_scale * self.h0_radius_ref + self.h0_bias


@dataclass(frozen=True)
class SamplingConfig:
    """Sampling density for analysis and benchmark."""

    work_x_max: float = 150.0
    base_x_max: float = 250.0

    work_step: float = 2e-4
    base_step: float = 2e-4

    benchmark_points: int = 60000


@dataclass(frozen=True)
class PlotStyle:
    """Unified visual style tuned for GitHub presentation."""

    bg: str = "#0b132b"
    panel: str = "#1c2541"
    text: str = "#f8f9fa"
    accent: str = "#5bc0be"
    accent_alt: str = "#f4d35e"
    warning: str = "#ee964b"
    good: str = "#3ddc97"
    muted: str = "#8da1b9"
