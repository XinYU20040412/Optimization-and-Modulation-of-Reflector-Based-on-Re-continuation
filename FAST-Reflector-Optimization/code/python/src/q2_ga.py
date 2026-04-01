from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .constants import GAConfig, PlotStyle


@dataclass
class GAResult:
    """Container for genetic optimization outputs."""

    delta_r: np.ndarray
    best_rmse: float
    final_equation: np.ndarray
    avg_rmse_history: np.ndarray
    best_rmse_history: np.ndarray


def _calc_rmse_batch(population: np.ndarray, xs: np.ndarray, ys: np.ndarray, radius: float, h0_scale: float) -> np.ndarray:
    """Vectorized RMSE calculation for a full population."""
    a = (1.0 - h0_scale) * radius

    delta_peak = population[:, :1]
    delta_surface = population[:, 1:]

    p = 2.0 * (radius - a + delta_peak)
    p = np.where(np.abs(p) < 1e-12, 1e-12, p)

    xs2 = xs[None, :] + delta_surface * (xs[None, :] / radius)
    ys2 = ys[None, :] - delta_surface * (ys[None, :] / radius)
    ys_ideal = (xs2**2 - p**2 - 2.0 * a * p) / (2.0 * p)

    rmse = np.sqrt(np.mean((ys_ideal - ys2) ** 2, axis=1))
    return rmse


def _initialize_population(config: GAConfig, chromosome_len: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(config.lower_bound, config.upper_bound, size=(config.population_size, chromosome_len))


def _mutate_population(
    population: np.ndarray,
    config: GAConfig,
    iteration_idx: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Mutation strength decays over generations to improve final convergence."""
    decay = (1.0 - iteration_idx / config.iterations) ** 2
    mutate_mask = rng.random(population.shape) < config.mutation_rate
    delta = rng.random(population.shape) * decay
    direction = np.where(rng.random(population.shape) < 0.5, -1.0, 1.0)

    mutated = np.where(mutate_mask, population * (1.0 + direction * delta), population)
    return np.clip(mutated, config.lower_bound, config.upper_bound)


def _crossover_population(population: np.ndarray, config: GAConfig, rng: np.random.Generator) -> np.ndarray:
    crossed = population.copy()
    pop_size, chromosome_len = crossed.shape

    for idx in range(pop_size):
        if rng.random() > config.crossover_rate:
            continue

        mate = int(rng.integers(0, pop_size))
        if mate == idx:
            continue

        point = int(rng.integers(1, chromosome_len))
        tail_a = crossed[idx, point:].copy()
        crossed[idx, point:] = crossed[mate, point:]
        crossed[mate, point:] = tail_a

    return crossed


def _replace_worse(population: np.ndarray, fitness: np.ndarray, best_individual: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    max_fit = float(np.max(fitness))
    min_fit = float(np.min(fitness))
    threshold = (max_fit - min_fit) * 0.2 + min_fit

    replace_mask = fitness < threshold
    if np.any(replace_mask):
        population[replace_mask, :] = best_individual[None, :]
        fitness[replace_mask] = np.max(fitness)

    return population, fitness


def save_convergence_plot(avg_rmse: np.ndarray, best_rmse: np.ndarray, out_file: Path) -> None:
    style = PlotStyle()
    fig, ax = plt.subplots(figsize=(10.5, 5.4), facecolor=style.bg)
    ax.set_facecolor(style.panel)

    generations = np.arange(1, avg_rmse.size + 1)
    ax.plot(generations, avg_rmse, color=style.warning, lw=2.1, label="Average RMSE")
    ax.plot(generations, best_rmse, color=style.accent, lw=2.4, label="Best RMSE")

    for spine in ax.spines.values():
        spine.set_color(style.muted)
    ax.tick_params(colors=style.text)
    ax.xaxis.label.set_color(style.text)
    ax.yaxis.label.set_color(style.text)
    ax.title.set_color(style.text)

    ax.set_xlabel("Generation")
    ax.set_ylabel("RMSE")
    ax.set_title("Question-2 Genetic Optimization Convergence")
    ax.grid(alpha=0.28, color=style.muted)
    ax.legend(facecolor=style.panel, edgecolor=style.muted, labelcolor=style.text)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=220, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def run_genetic_optimization(
    angles: np.ndarray,
    radius: float,
    config: GAConfig,
    convergence_path: Path,
    h0_scale: float,
) -> GAResult:
    """Ported and modularized GA from legacy MATLAB question-2 implementation."""
    xs = radius * np.sin(angles)
    ys = -radius * np.cos(angles)

    chromosome_len = angles.size + 1
    rng = np.random.default_rng(config.random_seed)

    population = _initialize_population(config, chromosome_len=chromosome_len, rng=rng)

    avg_rmse_history = np.zeros(config.iterations, dtype=np.float64)
    best_rmse_history = np.zeros(config.iterations, dtype=np.float64)

    best_individual = population[0].copy()
    best_fitness = -np.inf

    for generation in range(config.iterations):
        population = _mutate_population(population, config=config, iteration_idx=generation, rng=rng)
        population = _crossover_population(population, config=config, rng=rng)

        rmse = _calc_rmse_batch(population, xs=xs, ys=ys, radius=radius, h0_scale=h0_scale)
        fitness = -rmse

        idx = int(np.argmax(fitness))
        if fitness[idx] > best_fitness:
            best_fitness = float(fitness[idx])
            best_individual = population[idx].copy()

        population, fitness = _replace_worse(population, fitness, best_individual)

        avg_rmse_history[generation] = float(np.mean(-fitness))
        best_rmse_history[generation] = float(-np.max(fitness))

    delta_r = best_individual
    best_rmse = float(-best_fitness)

    xs2 = xs + delta_r[1:] * (xs / radius)
    ys2 = ys - delta_r[1:] * (ys / radius)
    final_equation = np.polyfit(xs2, ys2, deg=4)

    save_convergence_plot(avg_rmse=avg_rmse_history, best_rmse=best_rmse_history, out_file=convergence_path)

    return GAResult(
        delta_r=delta_r,
        best_rmse=best_rmse,
        final_equation=final_equation,
        avg_rmse_history=avg_rmse_history,
        best_rmse_history=best_rmse_history,
    )
