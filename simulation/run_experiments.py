"""
Runs batch Gini shock simulations for 5 representative countries.
Saves results to outputs/simulation_results.json.

Usage:
    python -m simulation.run_experiments
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulation.config import (
    SimulationConfig,
    build_config,
    REPRESENTATIVE_COUNTRIES,
)
from simulation.model import SimulationParams, run_single_experiment


SHOCK_MAGNITUDES = [0.0, 3.0, 5.0, 10.0, 15.0]  # raw Gini points
N_REPLICATIONS = 50
N_AGENTS = 1000
TIPPING_THRESHOLD = 0.5  # shift in mean attitude that counts as tipping


def run_all_experiments() -> dict:
    """Run the full experiment grid and return results."""
    config = build_config()

    sim_params = SimulationParams(
        n_agents=N_AGENTS,
        max_timesteps=500,
        convergence_threshold=0.001,
        social_influence_strength=0.05,
        n_neighbors=15,
        majority_threshold=3.5,
        noise_scale=0.1,
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
        print(f"\n  {country_code} ({regime}): Gini={cp['gini']}, "
              f"intercept={cp['random_intercept']:.3f}")

        country_results = {
            "regime": regime,
            "gini_raw": cp["gini"],
            "random_intercept": cp["random_intercept"],
            "shocks": {},
        }

        baseline_means = []

        for shock in SHOCK_MAGNITUDES:
            shock_key = f"{shock:.1f}"
            rep_results = []

            for rep in range(N_REPLICATIONS):
                seed = int(country_code.encode().hex(), 16) % (2**31) + rep * 1000 + int(shock * 100)
                result = run_single_experiment(
                    country_code, shock, config, sim_params, seed
                )
                rep_results.append(result)
                completed += 1

            means = [r["final_mean"] for r in rep_results]
            sds = [r["final_sd"] for r in rep_results]
            pcts = [r["pct_above_threshold"] for r in rep_results]

            agg = {
                "mean": float(np.mean(means)),
                "sd_across_reps": float(np.std(means)),
                "mean_within_sd": float(np.mean(sds)),
                "pct_above_threshold": float(np.mean(pcts)),
                "gini_raw": rep_results[0]["gini_raw"],
                "gini_z": rep_results[0]["gini_z"],
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
            print(f"    Shock +{shock:5.1f}pp: mean={agg['mean']:.3f}, "
                  f"shift={agg['shift_from_baseline']:+.3f}, "
                  f"tipped={agg['tipped']}  [{pct:.0f}%]")

        results[country_code] = country_results

    elapsed = time.time() - start_time
    print(f"\n  Completed {completed} runs in {elapsed:.1f}s")

    return results


def build_output(results: dict) -> dict:
    """Package results with metadata for JSON output."""
    return {
        "metadata": {
            "description": "Gini shock experiments across 5 welfare regime types",
            "n_agents_per_country": N_AGENTS,
            "n_replications": N_REPLICATIONS,
            "convergence_threshold": 0.001,
            "max_timesteps": 500,
            "social_influence_strength": 0.05,
            "majority_threshold": 3.5,
            "tipping_threshold": TIPPING_THRESHOLD,
            "shock_magnitudes_gini_points": SHOCK_MAGNITUDES,
            "representative_countries": REPRESENTATIVE_COUNTRIES,
        },
        "results": results,
    }


def print_summary(output: dict):
    """Print human-readable summary of results."""
    results = output["results"]

    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  SIMULATION RESULTS SUMMARY")
    lines.append("=" * 60)

    lines.append("")
    lines.append("Baseline equilibrium attitudes (mean across 50 replications):")
    for code, r in results.items():
        regime = r["regime"]
        lines.append(
            f"  {code} ({regime}): {r['baseline_mean']:.3f} "
            f"(Gini = {r['gini_raw']})"
        )

    lines.append("")
    lines.append(f"Tipping results (shift > {TIPPING_THRESHOLD} from baseline):")
    for shock in SHOCK_MAGNITUDES:
        if shock == 0.0:
            continue
        shock_key = f"{shock:.1f}"
        tipped = [
            code for code, r in results.items()
            if r["shocks"][shock_key]["tipped"]
        ]
        label = f"  {shock:.0f}pp shock: "
        if tipped:
            lines.append(label + ", ".join(tipped))
        else:
            lines.append(label + "none")

    lines.append("")
    lines.append("Detailed shifts by shock magnitude:")
    header = f"  {'Country':<6} {'Regime':<28} " + "  ".join(
        f"{s:>6.0f}pp" for s in SHOCK_MAGNITUDES if s > 0
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
    max_shift_country = max(
        results.items(),
        key=lambda x: abs(x[1]["shocks"]["15.0"]["shift_from_baseline"])
    )
    min_shift_country = min(
        results.items(),
        key=lambda x: abs(x[1]["shocks"]["15.0"]["shift_from_baseline"])
    )
    lines.append(
        f"Key finding: {max_shift_country[0]} ({max_shift_country[1]['regime']}) "
        f"shows the largest response to inequality shocks "
        f"(+{max_shift_country[1]['shocks']['15.0']['shift_from_baseline']:.3f} at 15pp), "
        f"while {min_shift_country[0]} ({min_shift_country[1]['regime']}) "
        f"shows the smallest "
        f"({min_shift_country[1]['shocks']['15.0']['shift_from_baseline']:+.3f})."
    )

    lines.append("")
    any_tipped = any(
        r["shocks"]["15.0"]["tipped"] for r in results.values()
    )
    if any_tipped:
        tipped_countries = [
            code for code, r in results.items() if r["shocks"]["15.0"]["tipped"]
        ]
        lines.append(
            f"Effect size note: The income x Gini interaction (beta = "
            f"{0.012:.3f}) produces discontinuous tipping at 15pp shocks "
            f"in {', '.join(tipped_countries)}."
        )
    else:
        max_shift = max(
            abs(r["shocks"]["15.0"]["shift_from_baseline"])
            for r in results.values()
        )
        lines.append(
            f"Effect size note: The income x Gini interaction (beta = "
            f"{0.012:.3f}) produces gradual drift (max shift = "
            f"{max_shift:.3f}) rather than discontinuous tipping across "
            f"the tested shock range. This is consistent with the modest "
            f"coefficient magnitude."
        )

    summary_text = "\n".join(lines)
    print(summary_text)
    return summary_text


def main():
    """Main entry point."""
    results = run_all_experiments()

    output = build_output(results)

    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "simulation_results.json"
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to: {results_path}")

    summary_text = print_summary(output)

    summary_path = output_dir / "simulation_summary.txt"
    with open(summary_path, "w") as f:
        f.write(summary_text)
    print(f"  Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
