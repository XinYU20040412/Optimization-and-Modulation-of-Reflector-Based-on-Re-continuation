from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import Q2Config


@dataclass
class Q2AdjustmentResult:
    """Adjusted coordinates and actuator outputs for question 2."""

    node_names: np.ndarray
    adjusted_xyz: np.ndarray
    flex_length: np.ndarray
    theta: np.ndarray
    peak_coordinate: np.ndarray
    working_mask: np.ndarray


def build_transform_matrix(config: Q2Config) -> np.ndarray:
    """Construct the same rotation matrix used by the original MATLAB script."""
    a = np.deg2rad(config.azimuth_deg)
    b = np.pi / 2.0 - np.deg2rad(config.elevation_deg)

    rot_y = np.array(
        [
            [np.cos(b), 0.0, np.sin(b)],
            [0.0, 1.0, 0.0],
            [-np.sin(b), 0.0, np.cos(b)],
        ],
        dtype=np.float64,
    )
    rot_z = np.array(
        [
            [np.cos(a), -np.sin(a), 0.0],
            [np.sin(a), np.cos(a), 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    return rot_y @ rot_z


def to_local(points_xyz: np.ndarray, transform: np.ndarray) -> np.ndarray:
    """Apply inverse transform in batch, equivalent to MATLAB tran_mat\point."""
    return np.linalg.solve(transform, points_xyz.T).T


def to_global(points_xyz: np.ndarray, transform: np.ndarray) -> np.ndarray:
    """Transform local coordinates back to global frame."""
    return (transform @ points_xyz.T).T


def apply_q2_adjustment(
    node_names: np.ndarray,
    xyz_global: np.ndarray,
    radius: float,
    delta_poly: np.ndarray,
    delta_peak: float,
    config: Q2Config,
) -> Q2AdjustmentResult:
    """Apply radial actuator deformation and return adjusted working-area nodes."""
    transform = build_transform_matrix(config)
    xyz_local = to_local(xyz_global, transform=transform)

    rho = np.sqrt(xyz_local[:, 0] ** 2 + xyz_local[:, 1] ** 2)
    working_mask = rho <= config.working_radius

    work_nodes = xyz_local[working_mask].copy()
    work_names = node_names[working_mask]
    work_rho = np.sqrt(work_nodes[:, 0] ** 2 + work_nodes[:, 1] ** 2)

    theta = np.arcsin(np.clip(work_rho / radius, 0.0, 1.0))
    flex = np.polyval(delta_poly, theta)

    safe_rho = np.where(work_rho < 1e-10, 1.0, work_rho)
    radial_scale = flex * np.sin(theta)

    # Bugfix-1: denominator must be sqrt(x^2 + y^2), not sqrt(x^2 + y^2 of y only).
    work_nodes[:, 0] = work_nodes[:, 0] + radial_scale * (work_nodes[:, 0] / safe_rho)
    work_nodes[:, 1] = work_nodes[:, 1] + radial_scale * (work_nodes[:, 1] / safe_rho)
    work_nodes[:, 2] = work_nodes[:, 2] - flex * np.cos(theta)

    # Bugfix-2: inverse transform must use adjusted local nodes, not original raw nodes.
    adjusted_global = to_global(work_nodes, transform=transform)

    peak_local = np.array([[0.0, 0.0, -(radius + delta_peak)]], dtype=np.float64)
    peak_global = to_global(peak_local, transform=transform)[0]

    return Q2AdjustmentResult(
        node_names=work_names,
        adjusted_xyz=adjusted_global,
        flex_length=flex,
        theta=theta,
        peak_coordinate=peak_global,
        working_mask=working_mask,
    )
