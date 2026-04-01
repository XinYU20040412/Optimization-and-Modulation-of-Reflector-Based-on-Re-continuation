from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .benchmark import run_benchmark
from .constants import GeometryConfig, SamplingConfig
from .data_loader import load_node_cloud
from .ray_models import build_profiles, compute_acceptance_vectorized
from .visualization import create_cover_gif, create_dashboard, create_parameter_sweep_gif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="2021A optimized visualization pipeline")
    parser.add_argument("--work-step", type=float, default=2e-4, help="x-step for working parabola")
    parser.add_argument("--base-step", type=float, default=2e-4, help="x-step for baseline sphere")
    parser.add_argument("--benchmark-points", type=int, default=60000, help="points for speed benchmark")
    parser.add_argument("--cover-frames", type=int, default=120, help="frames for GitHub cover GIF")
    parser.add_argument("--sweep-frames", type=int, default=90, help="frames for parameter sweep GIF")
    parser.add_argument("--seed", type=int, default=2026, help="seed for synthetic fallback cloud")
    return parser


def run_pipeline(args: argparse.Namespace) -> dict:
    project_root = Path(__file__).resolve().parent.parent

    geo = GeometryConfig()
    sampling = SamplingConfig(
        work_step=args.work_step,
        base_step=args.base_step,
        benchmark_points=args.benchmark_points,
    )

    node_cloud = load_node_cloud(
        project_root=project_root,
        working_radius=sampling.work_x_max,
        sphere_radius=geo.sphere_radius,
        seed=args.seed,
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

    images_dir = project_root / "outputs" / "images"
    gifs_dir = project_root / "outputs" / "gifs"
    images_dir.mkdir(parents=True, exist_ok=True)
    gifs_dir.mkdir(parents=True, exist_ok=True)

    dashboard_path = images_dir / "dashboard.png"
    cover_gif_path = gifs_dir / "github_cover.gif"
    sweep_gif_path = gifs_dir / "process_sweep.gif"

    create_dashboard(
        work=work_result,
        baseline=baseline_result,
        node_cloud=node_cloud,
        benchmark=benchmark,
        geo=geo,
        out_file=dashboard_path,
    )
    create_cover_gif(
        work=work_result,
        baseline=baseline_result,
        out_file=cover_gif_path,
        frames=args.cover_frames,
    )
    create_parameter_sweep_gif(
        geo=geo,
        out_file=sweep_gif_path,
        frames=args.sweep_frames,
    )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data_source": node_cloud.source,
        "geometry": asdict(geo),
        "sampling": asdict(sampling),
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
            "github_cover_gif": cover_gif_path.relative_to(project_root).as_posix(),
            "process_sweep_gif": sweep_gif_path.relative_to(project_root).as_posix(),
        },
    }

    report_path = project_root / "outputs" / "summary.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    report = run_pipeline(args)

    gain = report["acceptance_ratio"]["absolute_gain"]
    print("[Done] Dashboard:", report["artifacts"]["dashboard_png"])
    print("[Done] Cover GIF:", report["artifacts"]["github_cover_gif"])
    print("[Done] Sweep GIF:", report["artifacts"]["process_sweep_gif"])
    print(f"[Metric] Absolute gain: {gain:.6f}")


if __name__ == "__main__":
    main()
