"""
Generates figures from simulation results.
Saves to outputs/figures/simulation/.

Usage:
    python -m simulation.analysis
"""

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulation.config import REGIME_COLORS, REPRESENTATIVE_COUNTRIES

FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures" / "simulation"


def load_results() -> dict:
    """Load simulation results from JSON."""
    results_path = PROJECT_ROOT / "outputs" / "simulation_results.json"
    with open(results_path) as f:
        return json.load(f)


def setup_style():
    """Configure matplotlib for clean plots."""
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
    })


def figure_1_phase_diagram(data: dict):
    """Equilibrium mean attitude vs. shock magnitude, one line per country."""
    results = data["results"]
    shocks = data["metadata"]["shock_magnitudes_gini_points"]

    fig, ax = plt.subplots(figsize=(9, 6))

    for code, r in results.items():
        regime = r["regime"]
        color = REGIME_COLORS.get(regime, "#333333")

        means = []
        sds = []
        for shock in shocks:
            shock_key = f"{shock:.1f}"
            means.append(r["shocks"][shock_key]["mean"])
            sds.append(r["shocks"][shock_key]["sd_across_reps"])

        means = np.array(means)
        sds = np.array(sds)

        ax.plot(shocks, means, "o-", color=color, linewidth=2, markersize=5,
                label=f"{code} ({regime})")
        ax.fill_between(shocks, means - sds, means + sds, color=color, alpha=0.15)

    ax.axhline(y=3.5, color="#999999", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(shocks[-1] + 0.3, 3.5, "Majority\nthreshold",
            fontsize=8, color="#999999", va="center")

    ax.set_xlabel("Gini Shock Magnitude (percentage points)")
    ax.set_ylabel("Equilibrium Mean Attitude (1-5 scale)")
    ax.set_title("Redistribution Attitude Equilibria Under Inequality Shocks")
    ax.set_xlim(-0.5, shocks[-1] + 3)
    ax.set_ylim(2.5, 5.0)
    ax.legend(loc="upper left", frameon=False)

    path = FIGURE_DIR / "sim_01_phase_diagram.png"
    fig.savefig(path)
    plt.close(fig)



def figure_2_regime_comparison(data: dict):
    """Attitude distributions at baseline vs. 10pp shock, one panel per country."""
    results = data["results"]
    countries = list(results.keys())

    fig, axes = plt.subplots(1, len(countries), figsize=(16, 3.5), sharey=True)

    # Using summary stats to draw approximate normal distributions
    for i, code in enumerate(countries):
        ax = axes[i]
        r = results[code]
        regime = r["regime"]
        color = REGIME_COLORS.get(regime, "#333333")

        base_mean = r["shocks"]["0.0"]["mean"]
        base_sd = r["shocks"]["0.0"]["mean_within_sd"]

        shock_key = "10.0"
        shock_mean = r["shocks"][shock_key]["mean"]
        shock_sd = r["shocks"][shock_key]["mean_within_sd"]

        x = np.linspace(1, 5, 200)

        base_dist = np.exp(-0.5 * ((x - base_mean) / max(base_sd, 0.1)) ** 2)
        base_dist = base_dist / base_dist.max()

        shock_dist = np.exp(-0.5 * ((x - shock_mean) / max(shock_sd, 0.1)) ** 2)
        shock_dist = shock_dist / shock_dist.max()

        ax.fill_between(x, base_dist, alpha=0.3, color="#888888", label="Baseline")
        ax.fill_between(x, shock_dist, alpha=0.4, color=color, label="+10pp")
        ax.plot(x, base_dist, color="#888888", linewidth=1)
        ax.plot(x, shock_dist, color=color, linewidth=1.5)

        ax.axvline(base_mean, color="#888888", linestyle=":", linewidth=1)
        ax.axvline(shock_mean, color=color, linestyle="--", linewidth=1.2)

        ax.set_title(f"{code}\n{regime}", fontsize=10)
        ax.set_xlim(1, 5)
        ax.set_xlabel("Attitude")
        if i == 0:
            ax.set_ylabel("Density (normalized)")
            ax.legend(fontsize=7, frameon=False, loc="upper left")
        ax.set_yticks([])

    fig.suptitle("Attitude Distribution Shifts by Welfare Regime Type",
                 fontsize=13, y=1.05)
    fig.tight_layout()

    path = FIGURE_DIR / "sim_02_regime_comparison.png"
    fig.savefig(path)
    plt.close(fig)



def figure_3_tipping_heatmap(data: dict):
    """Heatmap of shift magnitude by initial Gini vs. shock size."""
    results = data["results"]
    shocks = [s for s in data["metadata"]["shock_magnitudes_gini_points"] if s > 0]

    sorted_countries = sorted(
        results.items(), key=lambda x: x[1]["gini_raw"]
    )
    country_codes = [c[0] for c in sorted_countries]
    gini_values = [c[1]["gini_raw"] for c in sorted_countries]
    regimes = [c[1]["regime"] for c in sorted_countries]

    shift_matrix = np.zeros((len(shocks), len(country_codes)))
    for j, (code, r) in enumerate(sorted_countries):
        for i, shock in enumerate(shocks):
            shock_key = f"{shock:.1f}"
            shift_matrix[i, j] = r["shocks"][shock_key]["shift_from_baseline"]

    fig, ax = plt.subplots(figsize=(8, 5))

    im = ax.imshow(
        shift_matrix, aspect="auto", cmap="RdYlBu_r",
        interpolation="nearest"
    )

    ax.set_xticks(range(len(country_codes)))
    ax.set_xticklabels(
        [f"{code}\n({gini:.0f})" for code, gini in zip(country_codes, gini_values)],
        fontsize=9,
    )
    ax.set_yticks(range(len(shocks)))
    ax.set_yticklabels([f"+{s:.0f}pp" for s in shocks])
    ax.set_xlabel("Country (Initial Gini)")
    ax.set_ylabel("Shock Magnitude")
    ax.set_title("Tipping Vulnerability by Initial Inequality Level")

    for i in range(len(shocks)):
        for j in range(len(country_codes)):
            val = shift_matrix[i, j]
            text_color = "white" if abs(val) > 0.3 else "black"
            ax.text(j, i, f"{val:+.2f}", ha="center", va="center",
                    fontsize=8, color=text_color)

    tipping = data["metadata"]["tipping_threshold"]
    for i in range(len(shocks)):
        for j in range(len(country_codes)):
            if abs(shift_matrix[i, j]) >= tipping:
                ax.plot(j, i, "k*", markersize=10)

    cbar = fig.colorbar(im, ax=ax, label="Shift from Baseline", shrink=0.8)

    fig.tight_layout()
    path = FIGURE_DIR / "sim_03_tipping_heatmap.png"
    fig.savefig(path)
    plt.close(fig)



def figure_4_income_attitude_scatter(data: dict):
    """Income vs. attitude at baseline and after 10pp shock for the most shifted country."""
    from simulation.config import build_config
    from simulation.model import Country, SimulationParams

    config = build_config()
    results = data["results"]

    # Find country with the largest absolute shift at 10pp
    target_code = max(
        results.items(),
        key=lambda x: abs(x[1]["shocks"]["10.0"]["shift_from_baseline"])
    )[0]

    sim_params = SimulationParams(
        n_agents=1000,
        max_timesteps=500,
        convergence_threshold=0.001,
        social_influence_strength=0.05,
        n_neighbors=15,
        majority_threshold=3.5,
        noise_scale=0.1,
    )

    rng_base = np.random.default_rng(42)
    country_base = Country(
        target_code, config.country_params[target_code],
        config, sim_params, rng_base
    )
    country_base.run_to_convergence()
    income_base = country_base.income.copy()
    attitude_base = country_base.attitude.copy()

    rng_shock = np.random.default_rng(42)
    country_shock = Country(
        target_code, config.country_params[target_code],
        config, sim_params, rng_shock
    )
    country_shock.apply_gini_shock(10.0, config)
    country_shock.run_to_convergence()
    income_shock = country_shock.income.copy()
    attitude_shock = country_shock.attitude.copy()

    regime = results[target_code]["regime"]
    color = REGIME_COLORS.get(regime, "#d62728")

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(income_base, attitude_base, alpha=0.08, s=8,
               color="#aaaaaa", label="Baseline", rasterized=True)
    ax.scatter(income_shock, attitude_shock, alpha=0.12, s=8,
               color=color, label="+10pp Gini shock", rasterized=True)

    def add_regression_line(x, y, color, linestyle, label):
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 10:
            return
        coeffs = np.polyfit(x[mask], y[mask], 1)
        x_line = np.linspace(x[mask].min(), x[mask].max(), 100)
        y_line = np.polyval(coeffs, x_line)
        ax.plot(x_line, y_line, color=color, linestyle=linestyle,
                linewidth=2.5, label=f"{label} (slope={coeffs[0]:.3f})")

    add_regression_line(income_base, attitude_base, "#555555", "-", "Baseline fit")
    add_regression_line(income_shock, attitude_shock, color, "--", "Post-shock fit")

    ax.set_xlabel("Income (centered)")
    ax.set_ylabel("Redistribution Attitude (1-5)")
    ax.set_title(
        f"How Inequality Shocks Change the Income-Attitude Relationship\n"
        f"{target_code} ({regime}), +10pp Gini Shock"
    )
    ax.set_ylim(1, 5)
    ax.legend(frameon=False, loc="upper right")

    fig.tight_layout()
    path = FIGURE_DIR / "sim_04_income_attitude_scatter.png"
    fig.savefig(path)
    plt.close(fig)



def main():
    """Generate all figures from simulation results."""
    setup_style()

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print("\nLoading simulation results...")
    data = load_results()
    print(f"  {len(data['results'])} countries, "
          f"{len(data['metadata']['shock_magnitudes_gini_points'])} shock levels")

    print("\nGenerating figures...")
    figure_1_phase_diagram(data)
    figure_2_regime_comparison(data)
    figure_3_tipping_heatmap(data)
    figure_4_income_attitude_scatter(data)

    print(f"\nAll figures saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
