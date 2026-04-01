from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class NodeCloud:
    source: str
    xyz: np.ndarray
    in_working_area: np.ndarray


def _try_read_csv(path: Path) -> pd.DataFrame:
    encodings = ("utf-8-sig", "gbk", "gb18030")
    last_error: Exception | None = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as exc:  # pragma: no cover
            last_error = exc
    if last_error is None:
        raise RuntimeError(f"Failed to read {path}")
    raise last_error


def _extract_xyz(df: pd.DataFrame) -> np.ndarray:
    columns = {str(c).strip().lower(): c for c in df.columns}

    if {"x", "y", "z"}.issubset(columns.keys()):
        xyz = df[[columns["x"], columns["y"], columns["z"]]]
    elif df.shape[1] >= 4:
        xyz = df.iloc[:, 1:4]
    elif df.shape[1] >= 3:
        xyz = df.iloc[:, :3]
    else:
        raise ValueError("CSV must contain at least 3 numeric columns for x/y/z.")

    xyz = xyz.apply(pd.to_numeric, errors="coerce").dropna()
    return xyz.to_numpy(dtype=np.float64)


def _candidate_paths(project_root: Path) -> Iterable[Path]:
    local_data = project_root / "data"
    legacy_root = project_root.parent

    names = ("附件1.csv", "attachment1.csv", "Attachment1.csv")
    for base in (local_data, legacy_root):
        for name in names:
            yield base / name

    patterns = ("*附件1*.csv", "*attachment1*.csv", "*Attachment1*.csv")
    for base in (local_data, legacy_root):
        if base.exists():
            for pattern in patterns:
                for candidate in sorted(base.glob(pattern)):
                    yield candidate


def discover_attachment_csv(project_root: Path) -> Path | None:
    seen: set[Path] = set()
    for path in _candidate_paths(project_root):
        if path in seen:
            continue
        seen.add(path)
        if path.exists() and path.is_file():
            return path
    return None


def synthesize_node_cloud(
    working_radius: float,
    sphere_radius: float,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    points: list[np.ndarray] = []
    ring_count = 42

    for ring_idx in range(1, ring_count + 1):
        ring_r = working_radius * ring_idx / ring_count
        count = max(24, int(2 * np.pi * ring_r / 2.5))

        theta = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)
        jitter = rng.normal(loc=0.0, scale=0.15, size=count)

        rr = np.clip(ring_r + jitter, 0.0, working_radius)
        x = rr * np.cos(theta)
        y = rr * np.sin(theta)
        z = -np.sqrt(np.clip(sphere_radius * sphere_radius - x * x - y * y, 0.0, None))
        points.append(np.column_stack((x, y, z)))

    return np.concatenate(points, axis=0)


def load_node_cloud(
    project_root: Path,
    working_radius: float,
    sphere_radius: float,
    seed: int = 2026,
) -> NodeCloud:
    candidate = discover_attachment_csv(project_root)
    if candidate is not None:
        df = _try_read_csv(candidate)
        xyz = _extract_xyz(df)
        source = f"real_data:{candidate.name}"
    else:
        xyz = synthesize_node_cloud(working_radius=working_radius, sphere_radius=sphere_radius, seed=seed)
        source = "synthetic_fallback"

    in_working = (xyz[:, 0] ** 2 + xyz[:, 1] ** 2) <= (working_radius ** 2)
    return NodeCloud(source=source, xyz=xyz, in_working_area=in_working)
