from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .constants import GAConfig, GeometryConfig, Q2Config
from .data_loader import NodeCloud
from .q2_ga import GAResult, run_genetic_optimization
from .q2_geometry import Q2AdjustmentResult, apply_q2_adjustment


@dataclass
class Q2PipelineResult:
    """Outputs and artifact paths for question-2 module."""

    ga: GAResult
    adjustment: Q2AdjustmentResult
    radius_estimate: float
    artifacts: dict


def _save_csv_outputs(adjustment: Q2AdjustmentResult, out_data_dir: Path) -> dict:
    out_data_dir.mkdir(parents=True, exist_ok=True)

    adjusted_path = out_data_dir / "q2_adjusted_nodes.csv"
    flex_path = out_data_dir / "q2_flex_lengths.csv"
    peak_path = out_data_dir / "q2_peak_coordinate.csv"

    pd.DataFrame(
        {
            "node": adjustment.node_names,
            "x": adjustment.adjusted_xyz[:, 0],
            "y": adjustment.adjusted_xyz[:, 1],
            "z": adjustment.adjusted_xyz[:, 2],
        }
    ).to_csv(adjusted_path, index=False, encoding="utf-8-sig")

    pd.DataFrame(
        {
            "node": adjustment.node_names,
            "theta_rad": adjustment.theta,
            "flex_length_m": adjustment.flex_length,
        }
    ).to_csv(flex_path, index=False, encoding="utf-8-sig")

    pd.DataFrame(
        {
            "x": [adjustment.peak_coordinate[0]],
            "y": [adjustment.peak_coordinate[1]],
            "z": [adjustment.peak_coordinate[2]],
        }
    ).to_csv(peak_path, index=False, encoding="utf-8-sig")

    return {
        "adjusted_nodes_csv": adjusted_path,
        "flex_lengths_csv": flex_path,
        "peak_coordinate_csv": peak_path,
    }


def _save_ga_profile(angles: np.ndarray, ga: GAResult, out_data_dir: Path) -> Path:
    path = out_data_dir / "q2_ga_profile.csv"
    pd.DataFrame(
        {
            "angle_rad": angles,
            "delta_r_m": ga.delta_r[1:],
        }
    ).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def run_q2_pipeline(
    node_cloud: NodeCloud,
    geo: GeometryConfig,
    q2_config: Q2Config,
    ga_config: GAConfig,
    out_data_dir: Path,
    out_image_dir: Path,
) -> Q2PipelineResult:
    """Re-implement question-2 MATLAB pipeline in pure Python."""
    radius_estimate = float(np.mean(np.linalg.norm(node_cloud.xyz, axis=1)))
    angles = np.linspace(0.0, np.pi / 6.0, q2_config.angle_count, dtype=np.float64)

    convergence_path = out_image_dir / "q2_ga_convergence.png"
    ga_result = run_genetic_optimization(
        angles=angles,
        radius=radius_estimate,
        config=ga_config,
        convergence_path=convergence_path,
        h0_scale=geo.h0_scale,
    )

    adjustment = apply_q2_adjustment(
        node_names=node_cloud.node_names,
        xyz_global=node_cloud.xyz,
        radius=radius_estimate,
        delta_poly=ga_result.final_equation,
        delta_peak=float(ga_result.delta_r[0]),
        config=q2_config,
    )

    artifacts = _save_csv_outputs(adjustment=adjustment, out_data_dir=out_data_dir)
    ga_profile_path = _save_ga_profile(angles=angles, ga=ga_result, out_data_dir=out_data_dir)

    metrics_path = out_data_dir / "q2_metrics.json"
    metrics = {
        "radius_estimate": radius_estimate,
        "best_rmse": ga_result.best_rmse,
        "delta_peak": float(ga_result.delta_r[0]),
        "final_equation": ga_result.final_equation.tolist(),
        "working_node_count": int(adjustment.adjusted_xyz.shape[0]),
        "ga_config": asdict(ga_config),
        "q2_config": asdict(q2_config),
    }
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    artifacts.update(
        {
            "ga_profile_csv": ga_profile_path,
            "q2_metrics_json": metrics_path,
            "q2_convergence_png": convergence_path,
        }
    )

    return Q2PipelineResult(
        ga=ga_result,
        adjustment=adjustment,
        radius_estimate=radius_estimate,
        artifacts=artifacts,
    )
