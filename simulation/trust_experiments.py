"""
Runs corruption shock simulations for 5 representative countries.
Saves results to outputs/trust_simulation_results.json.

Usage:
    python -m simulation.trust_experiments
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulation.trust_config import (
    TrustSimulationConfig,
    build_trust_config,
    REPRESENTATIVE_COUNTRIES,
)
from simulation.trust_model import TrustSimParams, run_single_trust_experiment


SHOCK_MAGNITUDES = [0.0, 5.0, 10.0, 15.0, 20.0]  # CPI point decreases
N_REPLICATIONS = 50
N_AGENTS = 1000
TIPPING_THRESHOLD = 1.0  # shift in mean trust that counts as tipping (0-10 scale)


def run_all_experiments():
    """Run the full experiment grid."""
    print("=" * 60)
    print("  Trust Simulation: Corruption Shock Experiments")
    print("=" * 60)

    print("\nLoading trust model parameters...")
    config = build_trust_config()
    print(f"  {len(config.country_params)} countries loaded")
    print(f"  CPI distribution: mean={config.corruption_mean:.1f}, SD={config.corruption_sd:.1f}")
    print(f"  Education x Corruption interaction: {config.education_corruption_interaction:.4f}")

    sim_params = TrustSimParams(
        n_agents=N_AGENTS,
        max_timesteps=500,
        convergence_threshold=0.001,
        social_influence_strength=0.05,
        n_neighbors=15,
        majority_threshold=5.0,
        noise_scale=0.1,
        feedback_strength=0.02,
    )

    results = {}
    total_runs = len(REPRESENTATIVE_COUNTRIES) * len(SHOCK_MAGNITUDES) * N_REPLICATIONS
    completed = 0
    start_time = time.time()

    for regime, country_code in REPRESENTATIVE_COUNTRIES.items():
        if country_code not in config.country_params:
            print(f"  WARNING: {country_code} not in parameters, skipping")
            continue

        cp = config.country_params[country_code]
        print(f"\n  {country_code} ({regime}): CPI={cp['cpi_score']}, "
              f"intercept={cp['random_intercept']:.3f}")

        country_results = {
            "regime": regime,
            "cpi_raw": cp["cpi_score"],
            "random_intercept": cp["random_intercept"],
            "shocks": {},
        }

        for shock in SHOCK_MAGNITUDES:
            shock_key = f"{shock:.1f}"
            rep_results = []

            for rep in range(N_REPLICATIONS):
                seed = int(country_code.encode().hex(), 16) % (2**31) + rep * 1000 + int(shock * 100)
                result = run_single_trust_experiment(
                    country_code, shock, config, sim_params, seed
                )
                rep_results.append(result)
                completed += 1

            means = [r["final_mean"] for r in rep_results]
            sds = [r["final_sd"] for r in rep_results]
            pcts = [r["pct_above_threshold"] for r in rep_results]
            drifts = [r["corruption_z_drift"] for r in rep_results]

            agg = {
                "mean": float(np.mean(means)),
                "sd_across_reps": float(np.std(means)),
                "mean_within_sd": float(np.mean(sds)),
                "pct_above_threshold": float(np.mean(pcts)),
                "cpi_raw": rep_results[0]["cpi_raw"],
                "corruption_z": rep_results[0]["corruption_z"],
                "mean_corruption_drift": float(np.mean(drifts)),
                "n_steps_mean": float(np.mean([r["n_steps"] for r in rep_results])),
            }

            if shock == 0.0:
                country_results["baseline_mean"] = agg["mean"]
                country_results["baseline_pct"] = agg["pct_above_threshold"]

            if "baseline_mean" in country_results:
                shift = agg["mean"] - country_results["baseline_mean"]
                agg["shift_from_baseline"] = float(shift)
                agg["tipped"] = abs(shift) >= TIPPING_THRESHOLD
            else:
                agg["shift_from_baseline"] = 0.0
                agg["tipped"] = False

            country_results["shocks"][shock_key] = agg

            elapsed = time.time() - start_time
            pct = completed / total_runs * 100
            print(f"    Shock -{shock:5.1f} CPI: mean={agg['mean']:.3f}, "
                  f"shift={agg['shift_from_baseline']:+.3f}, "
                  f"drift={agg['mean_corruption_drift']:+.3f}, "
                  f"tipped={agg['tipped']}  [{pct:.0f}%]")

        results[country_code] = country_results

    elapsed = time.time() - start_time
    print(f"\n  Completed {completed} runs in {elapsed:.1f}s")
    return results


def build_output(results):
    """Package results with metadata."""
    return {
        "metadata": {
            "description": "Corruption shock experiments across 5 welfare regime types",
            "dv": "trstprl (trust in parliament, 0-10)",
            "n_agents_per_country": N_AGENTS,
            "n_replications": N_REPLICATIONS,
            "convergence_threshold": 0.001,
            "max_timesteps": 500,
            "social_influence_strength": 0.05,
            "majority_threshold": 5.0,
            "feedback_strength": 0.02,
            "tipping_threshold": TIPPING_THRESHOLD,
            "shock_magnitudes_cpi_points": SHOCK_MAGNITUDES,
            "representative_countries": REPRESENTATIVE_COUNTRIES,
        },
        "results": results,
    }


def print_summary(output):
    """Print human-readable summary."""
    results = output["results"]
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("  TRUST SIMULATION RESULTS SUMMARY")
    lines.append("=" * 70)

    lines.append("")
    lines.append("Baseline trust levels (mean across 50 replications):")
    for code, r in results.items():
        lines.append(f"  {code} ({r['regime']}): {r['baseline_mean']:.3f} (CPI = {r['cpi_raw']})")

    lines.append("")
    lines.append(f"Tipping results (shift > {TIPPING_THRESHOLD:.1f} from baseline):")
    for shock in SHOCK_MAGNITUDES:
        if shock == 0.0:
            continue
        shock_key = f"{shock:.1f}"
        tipped = [code for code, r in results.items() if r["shocks"][shock_key]["tipped"]]
        label = f"  -{shock:.0f} CPI shock: "
        lines.append(label + (", ".join(tipped) if tipped else "none"))

    lines.append("")
    lines.append("Detailed shifts by shock magnitude:")
    header = f"  {'Country':<6} {'Regime':<28} " + "  ".join(
        f"{s:>7.0f}" for s in SHOCK_MAGNITUDES if s > 0
    )
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    for code, r in results.items():
        shifts = []
        for shock in SHOCK_MAGNITUDES:
            if shock == 0.0:
                continue
            shock_key = f"{shock:.1f}"
            s = r["shocks"][shock_key]["shift_from_baseline"]
            shifts.append(f"{s:+7.3f}")
        lines.append(f"  {code:<6} {r['regime']:<28} {'  '.join(shifts)}")

    lines.append("")
    lines.append("Feedback-driven corruption drift (z-score change):")
    for code, r in results.items():
        drift_20 = r["shocks"]["20.0"]["mean_corruption_drift"]
        lines.append(f"  {code}: {drift_20:+.4f} at -20 CPI shock")

    lines.append("")
    # Comparison with redistribution
    lines.append("=" * 70)
    lines.append("  REDISTRIBUTION vs TRUST SIMULATION COMPARISON")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  {'':30} {'Redistribution':>18} {'Trust':>18}")
    lines.append("  " + "-" * 66)
    lines.append(f"  {'ICC':30} {'8.0%':>18} {'18.1%':>18}")
    lines.append(f"  {'Key interaction':30} {'income x Gini':>18} {'ed x corruption':>18}")
    lines.append(f"  {'Interaction p-value':30} {'0.002':>18} {'<0.001':>18}")
    lines.append(f"  {'Interaction coef':30} {'0.012':>18} {'0.050':>18}")
    lines.append(f"  {'Mechanism':30} {'economic':>18} {'governance':>18}")

    # Check if any tipping occurred
    any_tipped = any(
        r["shocks"]["20.0"]["tipped"] for r in results.values()
    )
    max_shift = max(abs(r["shocks"]["20.0"]["shift_from_baseline"]) for r in results.values())
    lines.append(f"  {'Max shift (largest shock)':30} {'~0.33':>18} {max_shift:>18.3f}")
    lines.append(f"  {'Tipping observed':30} {'No':>18} {'Yes' if any_tipped else 'No':>18}")
    lines.append(f"  {'Feedback loop':30} {'No':>18} {'Yes':>18}")

    summary_text = "\n".join(lines)
    print(summary_text)
    return summary_text


def main():
    results = run_all_experiments()
    output = build_output(results)

    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "trust_simulation_results.json"
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to: {results_path}")

    summary_text = print_summary(output)

    summary_path = output_dir / "trust_simulation_summary.txt"
    with open(summary_path, "w") as f:
        f.write(summary_text)
    print(f"  Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
