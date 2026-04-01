from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Mapping, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class GeometryConfig:
    """Core geometry parameters inherited from the legacy scripts."""

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
    """Sampling density for acceptance-ratio analysis and benchmark."""

    work_x_max: float = 150.0
    base_x_max: float = 250.0

    work_step: float = 2e-4
    base_step: float = 2e-4

    benchmark_points: int = 60000


@dataclass(frozen=True)
class GAConfig:
    """Genetic-algorithm configuration for question-2 optimization."""

    population_size: int = 240
    iterations: int = 320
    mutation_rate: float = 0.20
    crossover_rate: float = 0.35
    lower_bound: float = -0.6
    upper_bound: float = 0.6
    random_seed: int = 2026


@dataclass(frozen=True)
class Q2Config:
    """Question-2 geometry and transformation settings."""

    angle_count: int = 100
    working_radius: float = 150.0
    azimuth_deg: float = 36.7595
    elevation_deg: float = 78.169


@dataclass(frozen=True)
class VizConfig:
    """Animation and rendering settings for GitHub-facing assets."""

    cover_frames: int = 120
    sweep_frames: int = 90
    morph_frames: int = 84
    ray_frames: int = 78


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


def config_from_mapping(cls: type[T], raw: Mapping[str, Any] | None) -> T:
    """Build a dataclass from possibly noisy json mappings."""
    if not raw:
        return cls()

    valid_keys = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in raw.items() if k in valid_keys}
    return cls(**filtered)
