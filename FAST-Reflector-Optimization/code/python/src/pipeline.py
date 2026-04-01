from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .benchmark import run_benchmark
from .constants import GAConfig, GeometryConfig, Q2Config, SamplingConfig, VizConfig, config_from_mapping
from .data_loader import load_node_cloud
from .q2_pipeline import run_q2_pipeline
from .ray_models import build_profiles, compute_acceptance_vectorized
from .visualization import (
    create_acceptance_bar_chart,
    create_cover_gif,
    create_dashboard,
    create_parameter_sweep_gif,
    create_ray_path_gif,
    create_surface_morph_gif,
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_config_path(project_root: Path) -> Path:
    return project_root / "code" / "python" / "config" / "pipeline_config.json"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FAST reflector optimization full pipeline")
    parser.add_argument("--config", type=str, default=None, help="json config file path")
    parser.add_argument("--seed", type=int, default=2026, help="random seed for synthetic fallback")

    parser.add_argument("--work-step", type=float, default=None, help="optional override for working profile step")
    parser.add_argument("--base-step", type=float, default=None, help="optional override for baseline profile step")
    parser.add_argument("--benchmark-points", type=int, default=None, help="optional override for benchmark points")

    parser.add_argument("--cover-frames", type=int, default=None, help="optional override for process gif frames")
    parser.add_argument("--sweep-frames", type=int, default=None, help="optional override for h0 sweep frames")
    parser.add_argument("--morph-frames", type=int, default=None, help="optional override for 3d morph gif frames")
    parser.add_argument("--ray-frames", type=int, default=None, help="optional override for 2d ray gif frames")
    return parser


def _save_key_metrics_csv(
    out_file: Path,
    work_ratio: float,
    baseline_ratio: float,
    q2_best_rmse: float,
    q2_delta_peak: float,
) -> None:
    gain = work_ratio - baseline_ratio
    rel = gain / baseline_ratio * 100.0 if baseline_ratio > 0 else None

    df = pd.DataFrame(
        {
            "metric": [
                "working_ratio",
                "baseline_ratio",
                "absolute_gain",
                "relative_gain_percent",
                "q2_best_rmse",
                "q2_peak_stroke_m",
            ],
            "value": [work_ratio, baseline_ratio, gain, rel, q2_best_rmse, q2_delta_peak],
        }
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False, encoding="utf-8-sig")


def run_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    project_root = _project_root()

    config_path = Path(args.config) if args.config else _default_config_path(project_root)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    config = _load_json(config_path)

    geo = config_from_mapping(GeometryConfig, config.get("geometry"))
    sampling = config_from_mapping(SamplingConfig, config.get("sampling"))
    ga_cfg = config_from_mapping(GAConfig, config.get("ga"))
    q2_cfg = config_from_mapping(Q2Config, config.get("q2"))
    viz_cfg = config_from_mapping(VizConfig, config.get("visualization"))

    if args.work_step is not None:
        sampling = replace(sampling, work_step=args.work_step)
    if args.base_step is not None:
        sampling = replace(sampling, base_step=args.base_step)
    if args.benchmark_points is not None:
        sampling = replace(sampling, benchmark_points=args.benchmark_points)

    if args.cover_frames is not None:
        viz_cfg = replace(viz_cfg, cover_frames=args.cover_frames)
    if args.sweep_frames is not None:
        viz_cfg = replace(viz_cfg, sweep_frames=args.sweep_frames)
    if args.morph_frames is not None:
        viz_cfg = replace(viz_cfg, morph_frames=args.morph_frames)
    if args.ray_frames is not None:
        viz_cfg = replace(viz_cfg, ray_frames=args.ray_frames)

    io_cfg = config.get("io", {})
    preferred_csv = io_cfg.get("attachment_csv", "results/data/sample_attachment1.csv")

    node_cloud = load_node_cloud(
        project_root=project_root,
        working_radius=q2_cfg.working_radius,
        sphere_radius=geo.sphere_radius,
        seed=args.seed,
        preferred_csv=preferred_csv,
    )

    results_dir = project_root / "results"
    images_dir = results_dir / "images"
    animations_dir = results_dir / "animations"
    data_dir = results_dir / "data"

    images_dir.mkdir(parents=True, exist_ok=True)
    animations_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    q2_result = run_q2_pipeline(
        node_cloud=node_cloud,
        geo=geo,
        q2_config=q2_cfg,
        ga_config=ga_cfg,
        out_data_dir=data_dir,
        out_image_dir=images_dir,
    )

    x_work, y_work, x_base, y_base = build_profiles(geo=geo, sampling=sampling)

    work_result = compute_acceptance_vectorized(
        x=x_work,
        y=y_work,
        h0=geo.h0,
        half_window=geo.receiver_half_window,
        label="working-parabola",
    )
    baseline_result = compute_acceptance_vectorized(
        x=x_base,
        y=y_base,
        h0=geo.h0,
        half_window=geo.receiver_half_window,
        label="baseline-sphere",
    )

    benchmark = run_benchmark(geo=geo, sampling=sampling)

    dashboard_path = images_dir / "dashboard.png"
    bar_chart_path = images_dir / "acceptance_comparison.png"

    morph_gif_path = animations_dir / "surface_morph.gif"
    ray_gif_path = animations_dir / "ray_path_2d.gif"
    cover_gif_path = animations_dir / "optimization_process.gif"
    sweep_gif_path = animations_dir / "h0_parameter_sweep.gif"

    create_dashboard(
        work=work_result,
        baseline=baseline_result,
        node_cloud=node_cloud,
        benchmark=benchmark,
        geo=geo,
        out_file=dashboard_path,
    )
    create_acceptance_bar_chart(work=work_result, baseline=baseline_result, out_file=bar_chart_path)

    create_surface_morph_gif(
        geo=geo,
        node_cloud=node_cloud,
        out_file=morph_gif_path,
        frames=viz_cfg.morph_frames,
    )
    create_ray_path_gif(
        work=work_result,
        baseline=baseline_result,
        geo=geo,
        out_file=ray_gif_path,
        frames=viz_cfg.ray_frames,
    )
    create_cover_gif(
        work=work_result,
        baseline=baseline_result,
        out_file=cover_gif_path,
        frames=viz_cfg.cover_frames,
    )
    create_parameter_sweep_gif(
        geo=geo,
        out_file=sweep_gif_path,
        frames=viz_cfg.sweep_frames,
    )

    key_metrics_path = data_dir / "key_metrics.csv"
    _save_key_metrics_csv(
        out_file=key_metrics_path,
        work_ratio=work_result.ratio,
        baseline_ratio=baseline_result.ratio,
        q2_best_rmse=q2_result.ga.best_rmse,
        q2_delta_peak=float(q2_result.ga.delta_r[0]),
    )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config_file": config_path.relative_to(project_root).as_posix() if config_path.exists() else "default",
        "data_source": node_cloud.source,
        "geometry": asdict(geo),
        "sampling": asdict(sampling),
        "q2": {
            "radius_estimate": q2_result.radius_estimate,
            "best_rmse": q2_result.ga.best_rmse,
            "peak_stroke_m": float(q2_result.ga.delta_r[0]),
            "final_equation": q2_result.ga.final_equation.tolist(),
            "ga_config": asdict(ga_cfg),
            "q2_config": asdict(q2_cfg),
        },
        "acceptance_ratio": {
            "working_parabola": work_result.ratio,
            "baseline_sphere": baseline_result.ratio,
            "absolute_gain": work_result.ratio - baseline_result.ratio,
            "relative_gain_percent": (work_result.ratio / baseline_result.ratio - 1.0) * 100.0
            if baseline_result.ratio > 0
            else None,
        },
        "benchmark": benchmark,
        "artifacts": {
            "dashboard_png": dashboard_path.relative_to(project_root).as_posix(),
            "acceptance_bar_png": bar_chart_path.relative_to(project_root).as_posix(),
            "surface_morph_gif": morph_gif_path.relative_to(project_root).as_posix(),
            "ray_path_gif": ray_gif_path.relative_to(project_root).as_posix(),
            "optimization_process_gif": cover_gif_path.relative_to(project_root).as_posix(),
            "h0_sweep_gif": sweep_gif_path.relative_to(project_root).as_posix(),
            "q2_data": {k: v.relative_to(project_root).as_posix() for k, v in q2_result.artifacts.items()},
            "key_metrics_csv": key_metrics_path.relative_to(project_root).as_posix(),
        },
    }

    summary_path = results_dir / "summary.json"
    summary_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    report = run_pipeline(args)
    gain = report["acceptance_ratio"]["absolute_gain"]

    print("[Done] dashboard:", report["artifacts"]["dashboard_png"])
    print("[Done] 3d morph gif:", report["artifacts"]["surface_morph_gif"])
    print("[Done] 2d ray gif:", report["artifacts"]["ray_path_gif"])
    print("[Done] summary:", "results/summary.json")
    print(f"[Metric] acceptance absolute gain: {gain:.6f}")


if __name__ == "__main__":
    main()
