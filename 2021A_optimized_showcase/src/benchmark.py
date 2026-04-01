from __future__ import annotations

import time
from dataclasses import asdict

import numpy as np

from .constants import GeometryConfig, SamplingConfig
from .ray_models import (
    compute_acceptance_loop,
    compute_acceptance_vectorized,
    parabola_profile,
    sphere_profile,
)


def _best_of(callable_obj, repeats: int = 3) -> float:
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        callable_obj()
        elapsed = time.perf_counter() - t0
        if elapsed < best:
            best = elapsed
    return best


def run_benchmark(geo: GeometryConfig, sampling: SamplingConfig) -> dict:
    n = sampling.benchmark_points

    x_work = np.linspace(0.0, sampling.work_x_max, n, dtype=np.float64)
    x_base = np.linspace(0.0, sampling.base_x_max, n, dtype=np.float64)

    y_work = parabola_profile(x_work, geo)
    y_base = sphere_profile(x_base, geo)

    work_loop = _best_of(
        lambda: compute_acceptance_loop(
            x=x_work,
            y=y_work,
            h0=geo.h0,
            half_window=geo.receiver_half_window,
            label="working-loop",
        )
    )
    work_vec = _best_of(
        lambda: compute_acceptance_vectorized(
            x=x_work,
            y=y_work,
            h0=geo.h0,
            half_window=geo.receiver_half_window,
            label="working-vectorized",
        )
    )

    base_loop = _best_of(
        lambda: compute_acceptance_loop(
            x=x_base,
            y=y_base,
            h0=geo.h0,
            half_window=geo.receiver_half_window,
            label="baseline-loop",
        )
    )
    base_vec = _best_of(
        lambda: compute_acceptance_vectorized(
            x=x_base,
            y=y_base,
            h0=geo.h0,
            half_window=geo.receiver_half_window,
            label="baseline-vectorized",
        )
    )

    return {
        "config": asdict(sampling),
        "working": {
            "loop_seconds": work_loop,
            "vectorized_seconds": work_vec,
            "speedup": work_loop / work_vec,
        },
        "baseline": {
            "loop_seconds": base_loop,
            "vectorized_seconds": base_vec,
            "speedup": base_loop / base_vec,
        },
    }
