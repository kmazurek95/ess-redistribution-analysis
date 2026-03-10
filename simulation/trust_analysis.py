"""
Generates figures from trust simulation results.
Saves to outputs/figures/trust/simulation/.

Usage:
    python -m simulation.trust_analysis
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

from simulation.trust_config import REGIME_COLORS, REPRESENTATIVE_COUNTRIES

FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures" / "trust" / "simulation"


def load_results():
    results_path = PROJECT_ROOT / "outputs" / "trust_simulation_results.json"
    with open(results_path) as f:
        return json.load(f)


def setup_style():
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


def figure_1_phase_diagram(data):
    """Equilibrium trust vs. corruption shock magnitude."""
    results = data["results"]
    shocks = data["metadata"]["shock_magnitudes_cpi_points"]

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

    ax.axhline(y=5.0, color="#999999", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(shocks[-1] + 0.3, 5.0, "Midpoint\n(neutral trust)",
            fontsize=8, color="#999999", va="center")

    ax.set_xlabel("Corruption Shock (CPI point decrease)")
    ax.set_ylabel("Equilibrium Mean Trust (0-10 scale)")
    ax.set_title("Trust Equilibria Under Corruption Shocks")
    ax.set_xlim(-0.5, shocks[-1] + 3)
    ax.set_ylim(0, 10)
    ax.legend(loc="upper right", frameon=False)

    path = FIGURE_DIR / "trust_sim_01_phase_diagram.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")


def figure_2_regime_comparison(data):
    """Trust distributions at baseline vs. 15 CPI shock."""
    results = data["results"]
    countries = list(results.keys())

    fig, axes = plt.subplots(1, len(countries), figsize=(16, 3.5), sharey=True)

    for i, code in enumerate(countries):
        ax = axes[i]
        r = results[code]
        regime = r["regime"]
        color = REGIME_COLORS.get(regime, "#333333")

        base_mean = r["shocks"]["0.0"]["mean"]
        base_sd = r["shocks"]["0.0"]["mean_within_sd"]

        shock_mean = r["shocks"]["15.0"]["mean"]
        shock_sd = r["shocks"]["15.0"]["mean_within_sd"]

        x = np.linspace(0, 10, 200)

        base_dist = np.exp(-0.5 * ((x - base_mean) / max(base_sd, 0.1)) ** 2)
        base_dist = base_dist / base_dist.max()

        shock_dist = np.exp(-0.5 * ((x - shock_mean) / max(shock_sd, 0.1)) ** 2)
        shock_dist = shock_dist / shock_dist.max()

        ax.fill_between(x, base_dist, alpha=0.3, color="#888888", label="Baseline")
        ax.fill_between(x, shock_dist, alpha=0.4, color=color, label="-15 CPI")
        ax.plot(x, base_dist, color="#888888", linewidth=1)
        ax.plot(x, shock_dist, color=color, linewidth=1.5)

        ax.axvline(base_mean, color="#888888", linestyle=":", linewidth=1)
        ax.axvline(shock_mean, color=color, linestyle="--", linewidth=1.2)

        ax.set_title(f"{code}\n{regime}", fontsize=10)
        ax.set_xlim(0, 10)
        ax.set_xlabel("Trust")
        if i == 0:
            ax.set_ylabel("Density (normalized)")
            ax.legend(fontsize=7, frameon=False, loc="upper left")
        ax.set_yticks([])

    fig.suptitle("Trust Distribution Shifts by Welfare Regime Type",
                 fontsize=13, y=1.05)
    fig.tight_layout()

    path = FIGURE_DIR / "trust_sim_02_regime_comparison.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")


def figure_3_tipping_heatmap(data):
    """Heatmap of trust shift by initial CPI vs. shock size."""
    results = data["results"]
    shocks = [s for s in data["metadata"]["shock_magnitudes_cpi_points"] if s > 0]

    sorted_countries = sorted(results.items(), key=lambda x: x[1]["cpi_raw"])
    country_codes = [c[0] for c in sorted_countries]
    cpi_values = [c[1]["cpi_raw"] for c in sorted_countries]

    shift_matrix = np.zeros((len(shocks), len(country_codes)))
    for j, (code, r) in enumerate(sorted_countries):
        for i, shock in enumerate(shocks):
            shock_key = f"{shock:.1f}"
            shift_matrix[i, j] = r["shocks"][shock_key]["shift_from_baseline"]

    fig, ax = plt.subplots(figsize=(8, 5))

    im = ax.imshow(shift_matrix, aspect="auto", cmap="RdYlBu",
                   interpolation="nearest")

    ax.set_xticks(range(len(country_codes)))
    ax.set_xticklabels(
        [f"{code}\n(CPI {cpi:.0f})" for code, cpi in zip(country_codes, cpi_values)],
        fontsize=9,
    )
    ax.set_yticks(range(len(shocks)))
    ax.set_yticklabels([f"-{s:.0f} CPI" for s in shocks])
    ax.set_xlabel("Country (Initial CPI)")
    ax.set_ylabel("Shock Magnitude")
    ax.set_title("Trust Erosion by Initial Governance Quality")

    tipping = data["metadata"]["tipping_threshold"]
    for i in range(len(shocks)):
        for j in range(len(country_codes)):
            val = shift_matrix[i, j]
            text_color = "white" if abs(val) > 0.8 else "black"
            ax.text(j, i, f"{val:+.2f}", ha="center", va="center",
                    fontsize=8, color=text_color)
            if abs(val) >= tipping:
                ax.plot(j, i, "k*", markersize=10)

    fig.colorbar(im, ax=ax, label="Trust Shift from Baseline", shrink=0.8)
    fig.tight_layout()

    path = FIGURE_DIR / "trust_sim_03_tipping_heatmap.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")


def figure_4_education_trust_scatter(data):
    """Education vs. trust at baseline and after shock for most affected country."""
    from simulation.trust_config import build_trust_config
    from simulation.trust_model import TrustCountry, TrustSimParams

    config = build_trust_config()
    results = data["results"]

    target_code = max(
        results.items(),
        key=lambda x: abs(x[1]["shocks"]["15.0"]["shift_from_baseline"])
    )[0]

    sim_params = TrustSimParams(
        n_agents=1000, max_timesteps=500, convergence_threshold=0.001,
        social_influence_strength=0.05, n_neighbors=15, majority_threshold=5.0,
        noise_scale=0.1, feedback_strength=0.02,
    )

    rng_base = np.random.default_rng(42)
    country_base = TrustCountry(
        target_code, config.country_params[target_code], config, sim_params, rng_base
    )
    country_base.run_to_convergence()
    ed_base = country_base.education.copy()
    trust_base = country_base.attitude.copy()

    rng_shock = np.random.default_rng(42)
    country_shock = TrustCountry(
        target_code, config.country_params[target_code], config, sim_params, rng_shock
    )
    country_shock.apply_corruption_shock(15.0, config)
    country_shock.run_to_convergence()
    ed_shock = country_shock.education.copy()
    trust_shock = country_shock.attitude.copy()

    regime = results[target_code]["regime"]
    color = REGIME_COLORS.get(regime, "#d62728")

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(ed_base, trust_base, alpha=0.08, s=8,
               color="#aaaaaa", label="Baseline", rasterized=True)
    ax.scatter(ed_shock, trust_shock, alpha=0.12, s=8,
               color=color, label="-15 CPI shock", rasterized=True)

    def add_regression_line(x, y, color, linestyle, label):
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 10:
            return
        coeffs = np.polyfit(x[mask], y[mask], 1)
        x_line = np.linspace(x[mask].min(), x[mask].max(), 100)
        y_line = np.polyval(coeffs, x_line)
        ax.plot(x_line, y_line, color=color, linestyle=linestyle,
                linewidth=2.5, label=f"{label} (slope={coeffs[0]:.3f})")

    add_regression_line(ed_base, trust_base, "#555555", "-", "Baseline fit")
    add_regression_line(ed_shock, trust_shock, color, "--", "Post-shock fit")

    ax.set_xlabel("Education (centered, years)")
    ax.set_ylabel("Trust in Parliament (0-10)")
    ax.set_title(
        f"How Corruption Shocks Change the Education-Trust Relationship\n"
        f"{target_code} ({regime}), -15 CPI Shock"
    )
    ax.set_ylim(0, 10)
    ax.legend(frameon=False, loc="upper right")

    fig.tight_layout()
    path = FIGURE_DIR / "trust_sim_04_education_trust_scatter.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    setup_style()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print("\nLoading trust simulation results...")
    data = load_results()
    print(f"  {len(data['results'])} countries, "
          f"{len(data['metadata']['shock_magnitudes_cpi_points'])} shock levels")

    print("\nGenerating figures...")
    figure_1_phase_diagram(data)
    figure_2_regime_comparison(data)
    figure_3_tipping_heatmap(data)
    figure_4_education_trust_scatter(data)

    print(f"\nAll figures saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
