from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from .constants import GeometryConfig, PlotStyle
from .data_loader import NodeCloud
from .ray_models import AcceptanceResult, compute_acceptance_vectorized, parabola_profile, sphere_profile


def _downsample_indices(size: int, max_points: int) -> np.ndarray:
    if size <= max_points:
        return np.arange(size)
    return np.linspace(0, size - 1, max_points, dtype=int)


def _style_axes(ax, style: PlotStyle) -> None:
    ax.set_facecolor(style.panel)
    for spine in ax.spines.values():
        spine.set_color(style.muted)
    ax.tick_params(colors=style.text)
    ax.xaxis.label.set_color(style.text)
    ax.yaxis.label.set_color(style.text)
    ax.title.set_color(style.text)


def create_dashboard(
    work: AcceptanceResult,
    baseline: AcceptanceResult,
    node_cloud: NodeCloud,
    benchmark: dict,
    geo: GeometryConfig,
    out_file: Path,
) -> None:
    style = PlotStyle()

    fig = plt.figure(figsize=(16, 9), facecolor=style.bg)
    gs = fig.add_gridspec(2, 2, hspace=0.25, wspace=0.18)

    ax1 = fig.add_subplot(gs[0, 0])
    _style_axes(ax1, style)
    ax1.plot(work.x, work.y, color=style.accent, lw=2.2, label="Working Paraboloid")
    ax1.plot(baseline.x, baseline.y, color=style.accent_alt, lw=1.8, ls="--", label="Baseline Sphere")

    w_idx = np.flatnonzero(work.accepted_mask)
    b_idx = np.flatnonzero(baseline.accepted_mask)
    w_idx = w_idx[_downsample_indices(w_idx.size, 2400)] if w_idx.size else w_idx
    b_idx = b_idx[_downsample_indices(b_idx.size, 2400)] if b_idx.size else b_idx

    if w_idx.size:
        ax1.scatter(work.x[w_idx], work.y[w_idx], s=7, color=style.good, alpha=0.75, label="Accepted (Working)")
    if b_idx.size:
        ax1.scatter(
            baseline.x[b_idx],
            baseline.y[b_idx],
            s=7,
            color=style.warning,
            alpha=0.65,
            label="Accepted (Baseline)",
        )

    ax1.set_title("Profile and Accepted Reflection Points")
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.grid(alpha=0.25, color=style.muted)
    ax1.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    ax2 = fig.add_subplot(gs[0, 1])
    _style_axes(ax2, style)

    w_ds = _downsample_indices(work.x.size, 4000)
    b_ds = _downsample_indices(baseline.x.size, 4000)

    ax2.plot(work.x[w_ds], work.landing_y[w_ds], color=style.accent, lw=1.2, alpha=0.9, label="Landing Offset (Working)")
    ax2.plot(
        baseline.x[b_ds],
        baseline.landing_y[b_ds],
        color=style.accent_alt,
        lw=1.1,
        alpha=0.8,
        label="Landing Offset (Baseline)",
    )
    ax2.axhspan(
        -geo.receiver_half_window,
        geo.receiver_half_window,
        color=style.good,
        alpha=0.18,
        label="Receiver Window",
    )

    finite = np.concatenate(
        [
            work.landing_y[np.isfinite(work.landing_y)],
            baseline.landing_y[np.isfinite(baseline.landing_y)],
        ]
    )
    if finite.size:
        lim = float(np.nanpercentile(np.abs(finite), 95))
        lim = min(max(2.0, lim), 60.0)
        ax2.set_ylim(-lim, lim)

    ax2.set_title("Reflection Landing Offset Distribution")
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("Y = delta_x - x (m)")
    ax2.grid(alpha=0.25, color=style.muted)
    ax2.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    ax3 = fig.add_subplot(gs[1, 0])
    _style_axes(ax3, style)

    labels = ["Working Paraboloid", "Baseline Sphere"]
    loop_t = [benchmark["working"]["loop_seconds"], benchmark["baseline"]["loop_seconds"]]
    vec_t = [benchmark["working"]["vectorized_seconds"], benchmark["baseline"]["vectorized_seconds"]]

    x_pos = np.arange(len(labels))
    width = 0.35
    ax3.bar(x_pos - width / 2, loop_t, width=width, color=style.warning, alpha=0.85, label="Loop")
    ax3.bar(x_pos + width / 2, vec_t, width=width, color=style.good, alpha=0.85, label="Vectorized")

    for idx, (loop_time, vec_time) in enumerate(zip(loop_t, vec_t)):
        speedup = loop_time / vec_time if vec_time > 0 else np.nan
        ax3.text(idx, max(loop_time, vec_time) * 1.03, f"x{speedup:.1f}", ha="center", color=style.text, fontsize=11)

    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(labels, color=style.text)
    ax3.set_ylabel("time (s)")
    ax3.set_title("Performance Benchmark")
    ax3.grid(alpha=0.25, color=style.muted, axis="y")
    ax3.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    ax4 = fig.add_subplot(gs[1, 1], projection="3d")
    ax4.set_facecolor(style.panel)
    for axis in (ax4.xaxis, ax4.yaxis, ax4.zaxis):
        axis.label.set_color(style.text)
        axis.set_tick_params(colors=style.text)

    xyz = node_cloud.xyz
    mask = node_cloud.in_working_area
    in_idx = np.flatnonzero(mask)
    out_idx = np.flatnonzero(~mask)

    in_idx = in_idx[_downsample_indices(in_idx.size, 2200)] if in_idx.size else in_idx
    out_idx = out_idx[_downsample_indices(out_idx.size, 1500)] if out_idx.size else out_idx

    if in_idx.size:
        ax4.scatter(
            xyz[in_idx, 0],
            xyz[in_idx, 1],
            xyz[in_idx, 2],
            s=7,
            alpha=0.72,
            color=style.accent,
            label="Working Area",
        )
    if out_idx.size:
        ax4.scatter(
            xyz[out_idx, 0],
            xyz[out_idx, 1],
            xyz[out_idx, 2],
            s=7,
            alpha=0.58,
            color=style.warning,
            label="Outside Working Area",
        )

    ax4.set_title(f"Node Cloud Source: {node_cloud.source}", color=style.text)
    ax4.set_xlabel("x")
    ax4.set_ylabel("y")
    ax4.set_zlabel("z")
    ax4.view_init(elev=26, azim=40)
    ax4.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    fig.suptitle(
        "FAST Reflector Optimization Dashboard",
        fontsize=20,
        color=style.text,
        fontweight="bold",
    )

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=220, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def create_acceptance_bar_chart(work: AcceptanceResult, baseline: AcceptanceResult, out_file: Path) -> None:
    style = PlotStyle()

    fig, ax = plt.subplots(figsize=(8.4, 5.2), facecolor=style.bg)
    _style_axes(ax, style)

    labels = ["Working Paraboloid", "Baseline Sphere"]
    values = [work.ratio * 100.0, baseline.ratio * 100.0]
    colors = [style.accent, style.accent_alt]

    bars = ax.bar(labels, values, color=colors, alpha=0.9, width=0.58)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.3,
            f"{value:.3f}%",
            ha="center",
            color=style.text,
            fontsize=12,
            fontweight="bold",
        )

    gain = (work.ratio - baseline.ratio) / baseline.ratio * 100.0 if baseline.ratio > 0 else np.nan
    ax.set_ylim(0.0, max(values) * 1.35)
    ax.set_ylabel("Acceptance Ratio (%)")
    ax.set_title(f"Working vs Baseline Acceptance (Gain: {gain:.1f}%)")
    ax.grid(alpha=0.23, color=style.muted, axis="y")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=220, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def create_cover_gif(
    work: AcceptanceResult,
    baseline: AcceptanceResult,
    out_file: Path,
    frames: int = 120,
    fps: int = 20,
) -> None:
    style = PlotStyle()

    fig = plt.figure(figsize=(12, 6.4), facecolor=style.bg)
    gs = fig.add_gridspec(1, 2, wspace=0.18)
    ax_l = fig.add_subplot(gs[0, 0])
    ax_r = fig.add_subplot(gs[0, 1])

    _style_axes(ax_l, style)
    _style_axes(ax_r, style)

    ax_l.plot(work.x, work.y, color=style.accent, lw=2.2, label="Working Paraboloid")
    ax_l.plot(baseline.x, baseline.y, color=style.accent_alt, lw=1.8, ls="--", label="Baseline Sphere")
    ax_l.set_xlabel("x (m)")
    ax_l.set_ylabel("y (m)")
    ax_l.set_title("Reflection Path Scan")
    ax_l.grid(alpha=0.22, color=style.muted)

    marker_w, = ax_l.plot([], [], marker="o", ms=9, color=style.good)
    marker_b, = ax_l.plot([], [], marker="o", ms=8, color=style.warning)

    cum_w = np.cumsum(work.accepted_mask) / np.arange(1, work.x.size + 1)
    cum_b = np.cumsum(baseline.accepted_mask) / np.arange(1, baseline.x.size + 1)

    start_w = min(max(200, work.x.size // 700), work.x.size - 1)
    start_b = min(max(200, baseline.x.size // 700), baseline.x.size - 1)

    frame_idx_w = np.linspace(start_w, work.x.size - 1, frames, dtype=int)
    frame_idx_b = np.linspace(start_b, baseline.x.size - 1, frames, dtype=int)

    progress = np.linspace(0.0, 1.0, frames)
    cum_w_track = cum_w[frame_idx_w]
    cum_b_track = cum_b[frame_idx_b]

    ax_r.plot(progress, cum_w_track, color=style.accent, alpha=0.35, lw=1.0)
    ax_r.plot(progress, cum_b_track, color=style.accent_alt, alpha=0.35, lw=1.0)

    line_w, = ax_r.plot([], [], color=style.accent, lw=2.6, label="Working Paraboloid")
    line_b, = ax_r.plot([], [], color=style.accent_alt, lw=2.3, label="Baseline Sphere")

    cursor_w, = ax_r.plot([], [], marker="o", ms=8, color=style.good)
    cursor_b, = ax_r.plot([], [], marker="o", ms=8, color=style.warning)

    ax_r.set_xlim(0.0, 1.0)
    max_ratio = max(
        float(np.nanpercentile(cum_w_track, 98)),
        float(np.nanpercentile(cum_b_track, 98)),
    )
    ax_r.set_ylim(0.0, max(0.05, max_ratio * 1.25))
    ax_r.set_xlabel("Scan Progress")
    ax_r.set_ylabel("Cumulative Acceptance Ratio")
    ax_r.set_title("Optimization Process Comparison")
    ax_r.grid(alpha=0.22, color=style.muted)
    ax_r.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    title_text = fig.text(
        0.5,
        0.96,
        "2021A Reflector Optimization Showcase",
        ha="center",
        color=style.text,
        fontsize=16,
        fontweight="bold",
    )
    final_gain = cum_w_track[-1] - cum_b_track[-1]
    fig.text(
        0.5,
        0.915,
        f"Final Acceptance Gain: {final_gain:+.4f}",
        ha="center",
        color=style.accent,
        fontsize=11,
    )

    def update(frame: int):
        idx_w = frame_idx_w[frame]
        idx_b = frame_idx_b[frame]

        marker_w.set_data([work.x[idx_w]], [work.y[idx_w]])
        marker_b.set_data([baseline.x[idx_b]], [baseline.y[idx_b]])

        line_w.set_data(progress[: frame + 1], cum_w_track[: frame + 1])
        line_b.set_data(progress[: frame + 1], cum_b_track[: frame + 1])

        cursor_w.set_data([progress[frame]], [cum_w_track[frame]])
        cursor_b.set_data([progress[frame]], [cum_b_track[frame]])

        title_text.set_text("2021A Reflector Optimization Showcase")

        return marker_w, marker_b, line_w, line_b, cursor_w, cursor_b, title_text

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 // fps, blit=False)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_file, writer=PillowWriter(fps=fps))
    plt.close(fig)


def create_parameter_sweep_gif(
    geo: GeometryConfig,
    out_file: Path,
    frames: int = 90,
    fps: int = 16,
) -> None:
    style = PlotStyle()

    x_work = np.linspace(0.0, 150.0, 35000)
    x_base = np.linspace(0.0, 250.0, 35000)
    y_work = parabola_profile(x_work, geo)
    y_base = sphere_profile(x_base, geo)

    h_values = np.linspace(geo.h0 - 10.0, geo.h0 + 10.0, frames)
    r_work = np.zeros(frames)
    r_base = np.zeros(frames)

    for idx, h0 in enumerate(h_values):
        r_work[idx] = compute_acceptance_vectorized(
            x=x_work,
            y=y_work,
            h0=float(h0),
            half_window=geo.receiver_half_window,
            label="work",
        ).ratio
        r_base[idx] = compute_acceptance_vectorized(
            x=x_base,
            y=y_base,
            h0=float(h0),
            half_window=geo.receiver_half_window,
            label="base",
        ).ratio

    fig, ax = plt.subplots(figsize=(9.2, 5.6), facecolor=style.bg)
    _style_axes(ax, style)

    ax.plot(h_values, r_work, color=style.accent, lw=2.3, label="Working Paraboloid")
    ax.plot(h_values, r_base, color=style.accent_alt, lw=2.0, ls="--", label="Baseline Sphere")

    vline = ax.axvline(h_values[0], color=style.good, lw=2.0, alpha=0.9)
    p1, = ax.plot([], [], marker="o", ms=9, color=style.good)
    p2, = ax.plot([], [], marker="o", ms=8, color=style.warning)

    text = ax.text(
        0.02,
        0.95,
        "",
        transform=ax.transAxes,
        color=style.text,
        fontsize=11,
        verticalalignment="top",
    )

    ax.set_xlabel("receiver h0")
    ax.set_ylabel("acceptance ratio")
    ax.set_title("Receiver Height Parameter Sweep")
    ax.grid(alpha=0.24, color=style.muted)
    ax.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    def update(frame: int):
        h0 = h_values[frame]
        vline.set_xdata([h0, h0])
        p1.set_data([h0], [r_work[frame]])
        p2.set_data([h0], [r_base[frame]])
        text.set_text(
            f"h0={h0:.3f}\\nWorking={r_work[frame]:.4f}\\nBaseline={r_base[frame]:.4f}\\nDelta={r_work[frame]-r_base[frame]:+.4f}"
        )
        return vline, p1, p2, text

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 // fps, blit=False)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_file, writer=PillowWriter(fps=fps))
    plt.close(fig)


def create_surface_morph_gif(
    geo: GeometryConfig,
    node_cloud: NodeCloud,
    out_file: Path,
    frames: int = 84,
    fps: int = 16,
) -> None:
    """Create the 3D dynamic deformation GIF from baseline sphere to working paraboloid."""
    style = PlotStyle()

    r = np.linspace(0.0, 250.0, 80)
    theta = np.linspace(0.0, 2.0 * np.pi, 160)
    rr, tt = np.meshgrid(r, theta)

    xx = rr * np.cos(tt)
    yy = rr * np.sin(tt)

    sag_sphere = sphere_profile(rr, geo)
    sag_work_core = parabola_profile(np.minimum(rr, 150.0), geo)
    sag_work = np.where(rr <= 150.0, sag_work_core, sag_sphere)

    z_sphere = -sag_sphere
    z_work = -sag_work

    cloud_idx = np.flatnonzero(node_cloud.in_working_area)
    cloud_idx = cloud_idx[_downsample_indices(cloud_idx.size, 1200)] if cloud_idx.size else cloud_idx
    cloud_xyz = node_cloud.xyz[cloud_idx] if cloud_idx.size else np.empty((0, 3))

    fig = plt.figure(figsize=(10.6, 6.4), facecolor=style.bg)
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int):
        ax.cla()
        ax.set_facecolor(style.panel)

        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.label.set_color(style.text)
            axis.set_tick_params(colors=style.text)

        progress = frame / max(1, frames - 1)
        zz = (1.0 - progress) * z_sphere + progress * z_work

        ax.plot_surface(
            xx,
            yy,
            zz,
            cmap="Blues_r",
            linewidth=0,
            antialiased=True,
            alpha=0.95,
        )
        ax.plot_wireframe(
            xx[::8, ::8],
            yy[::8, ::8],
            zz[::8, ::8],
            color="#d9f0ff",
            linewidth=0.5,
            alpha=0.30,
        )

        if cloud_xyz.size:
            ax.scatter(
                cloud_xyz[:, 0],
                cloud_xyz[:, 1],
                cloud_xyz[:, 2],
                s=5,
                color=style.good,
                alpha=0.28,
                depthshade=False,
            )

        zoom = 250.0 - 100.0 * progress
        ax.set_xlim(-zoom, zoom)
        ax.set_ylim(-zoom, zoom)
        ax.set_zlim(-55.0, 5.0)

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(elev=20.0 + 8.0 * progress, azim=25.0 + 85.0 * progress)
        ax.set_title(
            f"FAST Surface Morphing: Baseline -> Working (progress={progress:.0%})",
            color=style.text,
            fontsize=13,
        )

        return ()

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 // fps, blit=False)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_file, writer=PillowWriter(fps=fps))
    plt.close(fig)


def _reflect_to_receiver(
    x: float,
    y: float,
    slope: float,
    receiver_h: float,
) -> tuple[float, float, bool]:
    """Return reflected x-hit at receiver line and if physically valid."""
    normal = np.array([-slope, 1.0], dtype=np.float64)
    norm = np.linalg.norm(normal)
    if norm < 1e-12:
        return np.nan, np.nan, False
    normal = normal / norm

    incoming = np.array([0.0, -1.0], dtype=np.float64)
    reflected = incoming - 2.0 * float(np.dot(incoming, normal)) * normal

    if reflected[1] <= 1e-10:
        return np.nan, np.nan, False

    t = (receiver_h - y) / reflected[1]
    if t <= 0:
        return np.nan, np.nan, False

    x_hit = x + t * reflected[0]
    return x_hit, t, True


def create_ray_path_gif(
    work: AcceptanceResult,
    baseline: AcceptanceResult,
    geo: GeometryConfig,
    out_file: Path,
    frames: int = 78,
    fps: int = 14,
) -> None:
    """Create 2D ray-principle animation with accepted and rejected rays highlighted."""
    style = PlotStyle()

    fig, ax = plt.subplots(figsize=(10.6, 6.2), facecolor=style.bg)

    x_line = np.linspace(0.0, 155.0, 34)
    y_work_line = parabola_profile(x_line, geo)
    slope_work = np.gradient(y_work_line, x_line)

    def update(frame: int):
        ax.cla()
        _style_axes(ax, style)

        ax.plot(work.x[::200], work.y[::200], color=style.accent, lw=2.2, label="Working Paraboloid")
        ax.plot(baseline.x[::200], baseline.y[::200], color=style.accent_alt, lw=1.7, ls="--", label="Baseline Sphere")

        ax.axhline(geo.h0, color=style.good, lw=1.6, alpha=0.9, label="Receiver Cabin Plane")
        ax.axvspan(-geo.receiver_half_window, geo.receiver_half_window, color=style.good, alpha=0.20)

        ray_count = 6 + int((frame / max(1, frames - 1)) * (x_line.size - 6))
        y_top = geo.h0 + 18.0

        for idx in range(ray_count):
            x0 = float(x_line[idx])
            y0 = float(y_work_line[idx])
            slope = float(slope_work[idx])

            hit_x, _, valid = _reflect_to_receiver(x=x0, y=y0, slope=slope, receiver_h=geo.h0)

            ax.plot([x0, x0], [y_top, y0], color="#9ad1ff", lw=1.0, alpha=0.75)

            if not valid or not np.isfinite(hit_x):
                continue

            hit_ok = abs(hit_x) <= geo.receiver_half_window
            color = style.good if hit_ok else "#ff6b6b"

            ax.plot([x0, hit_x], [y0, geo.h0], color=color, lw=1.25, alpha=0.92)

        ax.set_xlim(-8.0, 160.0)
        ax.set_ylim(-5.0, geo.h0 + 24.0)
        ax.set_xlabel("Reduced Planar Coordinate x (m)")
        ax.set_ylabel("Height y (m)")
        ax.set_title("Dimensionality-Reduced Ray Path: Incoming -> Reflection -> Receiver")
        ax.grid(alpha=0.25, color=style.muted)
        ax.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text, loc="upper left")

        ax.text(
            0.01,
            0.97,
            "Green: accepted rays | Red: rejected rays",
            transform=ax.transAxes,
            color=style.text,
            fontsize=10,
            va="top",
        )

        return ()

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 // fps, blit=False)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_file, writer=PillowWriter(fps=fps))
    plt.close(fig)
