"""
Trust in Parliament Model Analysis: Education x Corruption Interaction

Tests whether the education-trust relationship depends on country-level corruption,
mirroring the income x Gini interaction from the redistribution models.

Usage:
    python -m scripts.trust_model_analysis
"""

import json
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config


def load_data():
    """Load analysis dataset, supplement with trstprl from raw ESS, merge corruption."""
    df = pd.read_csv(config.PROCESSED_DATA_DIR / "analysis_data.csv", low_memory=False)

    # trstprl was consumed into political_trust composite during processing
    raw, _ = pyreadstat.read_dta(str(config.ESS_FILE), usecols=["idno", "cntry", "trstprl"])
    raw = raw.rename(columns={"cntry": "country"})
    if "trstprl" in df.columns:
        df = df.drop(columns=["trstprl"])
    df = df.merge(raw, on=["idno", "country"], how="left")
    df["trstprl"] = pd.to_numeric(df["trstprl"], errors="coerce")
    df.loc[df["trstprl"] > 10, "trstprl"] = np.nan

    # Load corruption CPI
    corr = pd.read_csv(config.EXTERNAL_DATA_DIR / "corruption_cpi_2018.csv")
    df = df.merge(corr, on="country", how="left")

    # Z-score corruption (higher CPI = less corrupt)
    mean_cpi = df.groupby("country")["cpi_score"].first().mean()
    std_cpi = df.groupby("country")["cpi_score"].first().std()
    df["corruption_z"] = (df["cpi_score"] - mean_cpi) / std_cpi

    return df


L1_PREDICTORS = ["income_c", "education_c", "age_c", "female", "employed",
                 "ideology_c", "meritocracy_index_c"]
L2_BASIC = ["gini_z", "gdp_per_capita_z", "unemployment_rate_z"]
DV = "trstprl"


def _model_vars(extra_l2=None, interaction=None):
    """Build formula string and required columns."""
    predictors = list(L1_PREDICTORS)
    l2 = list(L2_BASIC) + (extra_l2 or [])
    formula = f"{DV} ~ " + " + ".join(predictors + l2)
    if interaction:
        formula += f" + {interaction}"
    cols = [DV] + predictors + l2 + ["country"]
    return formula, cols


def run_model(df, formula, cols, re_formula=None, label=""):
    """Fit a MixedLM and return result + summary dict."""
    subset = df[cols].dropna()
    n_ind = len(subset)
    n_countries = subset["country"].nunique()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if re_formula:
            # Try random slope; fall back to intercept-only if boundary
            try:
                model = smf.mixedlm(formula, data=subset, groups=subset["country"],
                                    re_formula=re_formula)
                result = model.fit(reml=True)
                # Check for boundary convergence (nan SEs on random effects)
                re_params = [p for p in result.params.index if "Group" in str(p) or "Var" in str(p)]
                if any(np.isnan(result.bse.get(p, 0)) for p in re_params if p in result.bse):
                    raise ValueError("Boundary convergence")
                re_spec = f"random slope ({re_formula.replace('~', '').strip()})"
            except (ValueError, np.linalg.LinAlgError):
                model = smf.mixedlm(formula, data=subset, groups=subset["country"])
                result = model.fit(reml=True)
                re_spec = "random intercept only (slope hit boundary)"
        else:
            model = smf.mixedlm(formula, data=subset, groups=subset["country"])
            result = model.fit(reml=True)
            re_spec = "random intercept only"

    tau = result.cov_re.iloc[0, 0]
    sigma2 = result.scale
    icc = tau / (tau + sigma2)

    info = {
        "label": label, "n_ind": n_ind, "n_countries": n_countries,
        "icc": icc, "tau": tau, "sigma2": sigma2,
        "loglik": result.llf, "re_spec": re_spec,
        "result": result, "subset": subset,
    }
    return info


def extract_coef(result, param):
    """Pull coefficient, SE, p-value, CI for a parameter."""
    coef = result.fe_params.get(param, np.nan)
    se = result.bse.get(param, np.nan)
    pval = result.pvalues.get(param, np.nan)
    ci_lo = coef - 1.96 * se
    ci_hi = coef + 1.96 * se
    return {"coef": coef, "se": se, "pval": pval, "ci": [ci_lo, ci_hi]}


def plot_caterpillar(result, save_path):
    """Country random intercepts for trust."""
    re = result.random_effects
    countries = sorted(re.keys(), key=lambda c: re[c].iloc[0])
    intercepts = [re[c].iloc[0] for c in countries]
    names = [config.COUNTRY_NAMES.get(c, c) for c in countries]

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.barh(range(len(countries)), intercepts, color="#1f77b4", alpha=0.7)
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(names, fontsize=9)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Random intercept (deviation from grand mean)")
    ax.set_title("Trust in Parliament: Country Random Intercepts")
    plt.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {save_path}")


def plot_education_corruption_interaction(result, df_subset, save_path):
    """Predicted trust as a function of education at low/mean/high corruption."""
    params = result.fe_params
    corruption_vals = df_subset["corruption_z"].quantile([0.25, 0.5, 0.75]).values
    labels = ["Low corruption (25th pctl)", "Mean corruption", "High corruption (75th pctl)"]
    colors = ["#2ca02c", "#1f77b4", "#d62728"]

    # Education range (centered)
    ed_range = np.linspace(df_subset["education_c"].quantile(0.05),
                           df_subset["education_c"].quantile(0.95), 100)

    # Predicted trust = intercept + education_c*b + corruption_z*b + education_c:corruption_z*b
    # (other predictors at mean = 0 since centered)
    intercept = params.get("Intercept", 0)
    b_ed = params.get("education_c", 0)
    b_corr = params.get("corruption_z", 0)
    b_interact = params.get("education_c:corruption_z", 0)

    fig, ax = plt.subplots(figsize=(8, 6))
    for corr_val, label, color in zip(corruption_vals, labels, colors):
        predicted = intercept + b_ed * ed_range + b_corr * corr_val + b_interact * ed_range * corr_val
        ax.plot(ed_range, predicted, label=label, color=color, linewidth=2)

    ax.set_xlabel("Education (centered, years)")
    ax.set_ylabel("Predicted trust in parliament")
    ax.set_title("Education x Corruption Interaction")
    ax.legend()
    ax.set_ylim(0, 10)
    plt.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {save_path}")


def plot_random_slopes(result, save_path):
    """Education slopes by country."""
    re = result.random_effects
    # Random effects include intercept and education_c slope
    countries = list(re.keys())
    fixed_slope = result.fe_params.get("education_c", 0)

    slopes = []
    for c in countries:
        re_vals = re[c]
        if len(re_vals) > 1:
            slopes.append((c, fixed_slope + re_vals.iloc[1]))
        else:
            slopes.append((c, fixed_slope))

    slopes.sort(key=lambda x: x[1])
    names = [config.COUNTRY_NAMES.get(c, c) for c, _ in slopes]
    vals = [s for _, s in slopes]

    fig, ax = plt.subplots(figsize=(8, 10))
    colors = ["#d62728" if v < 0 else "#2ca02c" for v in vals]
    ax.barh(range(len(slopes)), vals, color=colors, alpha=0.7)
    ax.set_yticks(range(len(slopes)))
    ax.set_yticklabels(names, fontsize=9)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.axvline(fixed_slope, color="gray", linewidth=0.8, linestyle="--", label=f"Fixed slope ({fixed_slope:.3f})")
    ax.set_xlabel("Education slope (effect on trust)")
    ax.set_title("Trust in Parliament: Random Slopes for Education")
    ax.legend()
    plt.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {save_path}")


def extract_simulation_parameters(models, df):
    """Build simulation parameter JSON from trust model results."""
    best = models["T7"] if "T7" in models else models["T5"]
    result = best["result"]
    subset = best["subset"]

    # Fixed effects
    fixed = {}
    for param in result.fe_params.index:
        fixed[param] = {
            "coef": float(result.fe_params[param]),
            "se": float(result.bse.get(param, np.nan)),
            "pval": float(result.pvalues.get(param, np.nan)),
            "ci_95": [float(result.fe_params[param] - 1.96 * result.bse.get(param, 0)),
                      float(result.fe_params[param] + 1.96 * result.bse.get(param, 0))],
        }

    # Random effects
    tau = float(result.cov_re.iloc[0, 0])
    sigma2 = float(result.scale)

    # Country parameters
    country_params = {}
    country_data = df.groupby("country").first()
    for c in result.random_effects:
        re_vals = result.random_effects[c]
        cp = {
            "random_intercept": float(re_vals.iloc[0]),
            "cpi_score": float(country_data.loc[c, "cpi_score"]) if c in country_data.index else None,
            "corruption_z": float(country_data.loc[c, "corruption_z"]) if c in country_data.index else None,
            "gini": float(country_data.loc[c, "gini"]) if c in country_data.index and pd.notna(country_data.loc[c, "gini"]) else None,
            "regime": config.COUNTRY_TO_REGIME_ESPING.get(c, "Unknown"),
        }
        if len(re_vals) > 1:
            cp["random_slope_education"] = float(re_vals.iloc[1])
        country_params[c] = cp

    # Key interaction
    interact = extract_coef(result, "education_c:corruption_z")

    params = {
        "model": best["label"],
        "dv": "trstprl",
        "n_individuals": best["n_ind"],
        "n_countries": best["n_countries"],
        "fixed_effects": fixed,
        "education_corruption_interaction": {
            "coef": float(interact["coef"]),
            "se": float(interact["se"]),
            "pval": float(interact["pval"]),
            "ci_95": [float(x) for x in interact["ci"]],
        },
        "random_effects": {
            "tau": tau, "sigma2": sigma2,
            "icc_null": float(models["T1"]["icc"]),
            "icc_final": float(best["icc"]),
        },
        "country_parameters": country_params,
    }
    return params


def main():
    df = load_data()

    # Check corruption merge
    n_with_corr = df["cpi_score"].notna().sum()
    n_countries_corr = df.loc[df["cpi_score"].notna(), "country"].nunique()
    print(f"  {len(df):,} observations, {df['country'].nunique()} countries")
    print(f"  Corruption data: {n_countries_corr} countries matched")

    # Spot-check CPI values
    print("\n  CPI spot check:")
    for c in ["DK", "BG", "DE", "RS"]:
        val = df.loc[df["country"] == c, "cpi_score"].iloc[0] if c in df["country"].values else "missing"
        print(f"    {c}: {val}")

    models = {}

    # T1: Null model
    print("\n" + "=" * 70)
    print("  MODEL T1: Null (intercept only)")
    print("=" * 70)
    subset_null = df[[DV, "country"]].dropna()
    m1 = smf.mixedlm(f"{DV} ~ 1", data=subset_null, groups=subset_null["country"])
    r1 = m1.fit(reml=True)
    tau1 = r1.cov_re.iloc[0, 0]
    sig1 = r1.scale
    icc1 = tau1 / (tau1 + sig1)
    print(f"  N = {len(subset_null):,}, {subset_null['country'].nunique()} countries")
    print(f"  ICC = {icc1:.4f} ({icc1*100:.1f}%)")
    print(f"  tau = {tau1:.4f}, sigma2 = {sig1:.4f}")
    print(f"  LogLik = {r1.llf:.1f}")
    models["T1"] = {"label": "T1: Null", "n_ind": len(subset_null),
                     "n_countries": subset_null["country"].nunique(),
                     "icc": icc1, "tau": tau1, "sigma2": sig1,
                     "loglik": r1.llf, "result": r1, "subset": subset_null}

    # T2: Individual predictors
    print("\n" + "=" * 70)
    print("  MODEL T2: Individual predictors")
    print("=" * 70)
    l1_str = " + ".join(L1_PREDICTORS)
    formula_t2 = f"{DV} ~ {l1_str}"
    cols_t2 = [DV] + L1_PREDICTORS + ["country"]
    info_t2 = run_model(df, formula_t2, cols_t2, label="T2: Individual predictors")
    models["T2"] = info_t2
    print(f"  N = {info_t2['n_ind']:,}, {info_t2['n_countries']} countries")
    print(f"  ICC = {info_t2['icc']:.4f} ({info_t2['icc']*100:.1f}%)")
    print(f"  LogLik = {info_t2['loglik']:.1f}")
    ed = extract_coef(info_t2["result"], "education_c")
    print(f"  education_c: coef = {ed['coef']:.4f}, SE = {ed['se']:.4f}, p = {ed['pval']:.4f}")

    # T3: Add country-level predictors including corruption
    print("\n" + "=" * 70)
    print("  MODEL T3: + Country-level predictors (incl. corruption)")
    print("=" * 70)
    formula_t3, cols_t3 = _model_vars(extra_l2=["corruption_z"])
    info_t3 = run_model(df, formula_t3, cols_t3, label="T3: + Country-level")
    models["T3"] = info_t3
    print(f"  N = {info_t3['n_ind']:,}, {info_t3['n_countries']} countries")
    print(f"  ICC = {info_t3['icc']:.4f} ({info_t3['icc']*100:.1f}%)")
    print(f"  LogLik = {info_t3['loglik']:.1f}")
    corr = extract_coef(info_t3["result"], "corruption_z")
    print(f"  corruption_z: coef = {corr['coef']:.4f}, SE = {corr['se']:.4f}, p = {corr['pval']:.4f}")
    for v in L2_BASIC + ["corruption_z"]:
        c = extract_coef(info_t3["result"], v)
        sig = "***" if c["pval"] < 0.001 else "**" if c["pval"] < 0.01 else "*" if c["pval"] < 0.05 else ""
        print(f"    {v:<25} {c['coef']:>8.4f} ({c['se']:.4f}) p={c['pval']:.4f} {sig}")

    # T4: Random slope for education
    print("\n" + "=" * 70)
    print("  MODEL T4: + Random slope for education")
    print("=" * 70)
    formula_t4, cols_t4 = _model_vars(extra_l2=["corruption_z"])
    info_t4 = run_model(df, formula_t4, cols_t4, re_formula="~education_c",
                        label="T4: Random slope (education)")
    models["T4"] = info_t4
    print(f"  N = {info_t4['n_ind']:,}, {info_t4['n_countries']} countries")
    print(f"  ICC = {info_t4['icc']:.4f} ({info_t4['icc']*100:.1f}%)")
    print(f"  LogLik = {info_t4['loglik']:.1f}")
    print(f"  RE spec: {info_t4['re_spec']}")
    if "random slope" in info_t4["re_spec"]:
        r4 = info_t4["result"]
        slope_var = r4.cov_re.iloc[1, 1] if r4.cov_re.shape[0] > 1 else None
        if slope_var is not None:
            print(f"  Education slope variance: {slope_var:.6f}")

    # T5: Education x Corruption interaction (THE KEY MODEL)
    print("\n" + "=" * 70)
    print("  MODEL T5: Education x Corruption (KEY TEST)")
    print("=" * 70)
    formula_t5, cols_t5 = _model_vars(extra_l2=["corruption_z"],
                                       interaction="education_c:corruption_z")
    # Use random slope if T4 succeeded with it
    re_t5 = "~education_c" if "random slope" in info_t4["re_spec"] else None
    info_t5 = run_model(df, formula_t5, cols_t5, re_formula=re_t5,
                        label="T5: Education x Corruption")
    models["T5"] = info_t5
    interact_t5 = extract_coef(info_t5["result"], "education_c:corruption_z")
    print(f"  N = {info_t5['n_ind']:,}, {info_t5['n_countries']} countries")
    print(f"  ICC = {info_t5['icc']:.4f} ({info_t5['icc']*100:.1f}%)")
    print(f"  LogLik = {info_t5['loglik']:.1f}")
    print(f"  RE spec: {info_t5['re_spec']}")
    print(f"\n  >>> education_c:corruption_z")
    print(f"      coef = {interact_t5['coef']:.6f}")
    print(f"      SE   = {interact_t5['se']:.6f}")
    print(f"      p    = {interact_t5['pval']:.6f}")
    print(f"      95% CI = [{interact_t5['ci'][0]:.4f}, {interact_t5['ci'][1]:.4f}]")
    t5_sig = interact_t5["pval"] < 0.05
    print(f"      {'SIGNIFICANT' if t5_sig else 'NOT SIGNIFICANT'} at alpha = 0.05")

    # Print all fixed effects for T5
    print(f"\n  Full fixed effects (T5):")
    for param in info_t5["result"].fe_params.index:
        c = extract_coef(info_t5["result"], param)
        sig = "***" if c["pval"] < 0.001 else "**" if c["pval"] < 0.01 else "*" if c["pval"] < 0.05 else ""
        print(f"    {param:<30} {c['coef']:>10.4f} ({c['se']:.4f}) p={c['pval']:.4f} {sig}")

    # T6: Education x Gini interaction
    print("\n" + "=" * 70)
    print("  MODEL T6: Education x Gini")
    print("=" * 70)
    formula_t6, cols_t6 = _model_vars(extra_l2=["corruption_z"],
                                       interaction="education_c:gini_z")
    re_t6 = "~education_c" if "random slope" in info_t4["re_spec"] else None
    info_t6 = run_model(df, formula_t6, cols_t6, re_formula=re_t6,
                        label="T6: Education x Gini")
    models["T6"] = info_t6
    interact_t6 = extract_coef(info_t6["result"], "education_c:gini_z")
    print(f"  N = {info_t6['n_ind']:,}, {info_t6['n_countries']} countries")
    print(f"  LogLik = {info_t6['loglik']:.1f}")
    print(f"  education_c:gini_z: coef = {interact_t6['coef']:.6f}, SE = {interact_t6['se']:.6f}, p = {interact_t6['pval']:.4f}")
    t6_sig = interact_t6["pval"] < 0.05

    # T7: Full model (all significant interactions from T5-T6)
    print("\n" + "=" * 70)
    print("  MODEL T7: Full model")
    print("=" * 70)
    interactions = []
    if t5_sig:
        interactions.append("education_c:corruption_z")
    if t6_sig:
        interactions.append("education_c:gini_z")

    if interactions:
        interact_str = " + ".join(interactions)
        formula_t7, cols_t7 = _model_vars(extra_l2=["corruption_z"],
                                           interaction=interact_str)
        re_t7 = "~education_c" if "random slope" in info_t4["re_spec"] else None
        info_t7 = run_model(df, formula_t7, cols_t7, re_formula=re_t7,
                            label="T7: Full model")
        models["T7"] = info_t7
        print(f"  N = {info_t7['n_ind']:,}, {info_t7['n_countries']} countries")
        print(f"  ICC = {info_t7['icc']:.4f} ({info_t7['icc']*100:.1f}%)")
        print(f"  LogLik = {info_t7['loglik']:.1f}")
        print(f"  Interactions included: {interactions}")

        print(f"\n  Full fixed effects (T7):")
        for param in info_t7["result"].fe_params.index:
            c = extract_coef(info_t7["result"], param)
            sig = "***" if c["pval"] < 0.001 else "**" if c["pval"] < 0.01 else "*" if c["pval"] < 0.05 else ""
            print(f"    {param:<30} {c['coef']:>10.4f} ({c['se']:.4f}) p={c['pval']:.4f} {sig}")
    else:
        print("  No significant interactions from T5/T6. T7 = T3 (no interactions).")
        models["T7"] = models["T3"]

    # Summary table
    print("\n\n" + "=" * 90)
    print("  TRUST MODEL RESULTS SUMMARY")
    print("=" * 90)
    print(f"\n  {'Model':<40} {'ICC':>7} {'LogLik':>10} {'Key coef':>30}")
    print("  " + "-" * 87)
    for key in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        m = models[key]
        label = m["label"]
        icc_str = f"{m['icc']*100:.1f}%"
        ll_str = f"{m['loglik']:.1f}"
        if key == "T1":
            extra = ""
        elif key == "T2":
            e = extract_coef(m["result"], "education_c")
            extra = f"education: {e['coef']:.4f} (p={e['pval']:.4f})"
        elif key == "T3":
            c = extract_coef(m["result"], "corruption_z")
            extra = f"corruption: {c['coef']:.4f} (p={c['pval']:.4f})"
        elif key == "T4":
            extra = f"RE: {m['re_spec']}"
        elif key == "T5":
            i = interact_t5
            extra = f"ed x corr: {i['coef']:.4f} (p={i['pval']:.4f})"
        elif key == "T6":
            i = interact_t6
            extra = f"ed x gini: {i['coef']:.4f} (p={i['pval']:.4f})"
        elif key == "T7":
            if interactions:
                extra = f"interactions: {', '.join(interactions)}"
            else:
                extra = "no significant interactions"
        print(f"  {label:<40} {icc_str:>7} {ll_str:>10} {extra:>30}")

    headline = "SIGNIFICANT" if t5_sig else "NOT SIGNIFICANT"
    print(f"\n  HEADLINE: Education x Corruption interaction {headline} (p = {interact_t5['pval']:.4f})")

    # Save results table
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for key in ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]:
        m = models[key]
        row = {"model": key, "label": m["label"], "n_ind": m["n_ind"],
               "n_countries": m["n_countries"], "icc": m["icc"],
               "loglik": m["loglik"], "tau": m["tau"], "sigma2": m["sigma2"]}
        if key != "T1" and "result" in m:
            for param in m["result"].fe_params.index:
                row[f"{param}_coef"] = m["result"].fe_params[param]
                row[f"{param}_pval"] = m["result"].pvalues.get(param, np.nan)
        rows.append(row)
    pd.DataFrame(rows).to_csv(config.TABLES_DIR / "trust_model_results.csv", index=False)
    print(f"\n  Saved: {config.TABLES_DIR / 'trust_model_results.csv'}")

    # Figures
    fig_dir = config.FIGURES_DIR / "trust"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Use T3 for caterpillar (simple random intercept model with country-level predictors)
    plot_caterpillar(models["T3"]["result"], fig_dir / "trust_caterpillar.png")

    # Education x Corruption interaction plot (use T5 regardless of significance - still informative)
    plot_education_corruption_interaction(info_t5["result"], info_t5["subset"],
                                         fig_dir / "trust_education_corruption_interaction.png")

    # Random slopes (if T4 has actual random slopes)
    if "random slope" in info_t4["re_spec"]:
        plot_random_slopes(info_t4["result"], fig_dir / "trust_random_slopes_education.png")

    # Phase 3: Simulation parameters (only if T5 significant)
    if t5_sig:
        print("\n" + "=" * 70)
        print("  PHASE 3: SIMULATION PARAMETER EXTRACTION")
        print("=" * 70)
        params = extract_simulation_parameters(models, df)
        out_path = config.OUTPUT_DIR / "trust_simulation_parameters.json"
        with open(out_path, "w") as f:
            json.dump(params, f, indent=2)
        print(f"  Saved: {out_path}")

        best_key = "T7" if "T7" in models and models["T7"]["label"] != models["T3"]["label"] else "T5"
        best = models[best_key]
        print(f"\n  === TRUST SIMULATION READINESS ===")
        print(f"  ICC: {models['T1']['icc']*100:.1f}% (vs 8.0% for redistribution)")
        print(f"  Education x Corruption: coef = {interact_t5['coef']:.4f}, p = {interact_t5['pval']:.4f}")
        print(f"  Mechanism: corruption shock -> education-trust slope steepens ->")
        print(f"    educated citizens lose trust disproportionately -> cascade")
        print(f"  Simulation viable: YES")
    else:
        print("\n" + "=" * 70)
        print("  PHASE 3: SIMULATION NOT VIABLE")
        print("=" * 70)
        print(f"  Education x Corruption interaction p = {interact_t5['pval']:.4f} (not significant)")
        print(f"  No simulation parameter extraction.")

    # Final comparison with redistribution
    print("\n\n" + "=" * 70)
    print("  REDISTRIBUTION vs TRUST COMPARISON")
    print("=" * 70)
    print(f"\n  {'':30} {'Redistribution':>18} {'Trust':>18}")
    print("  " + "-" * 66)
    print(f"  {'ICC':30} {'8.0%':>18} {models['T1']['icc']*100:.1f}%{' ':>12}")
    print(f"  {'Key interaction':30} {'income x Gini':>18} {'education x corruption':>18}")
    print(f"  {'Interaction p-value':30} {'0.002':>18} {interact_t5['pval']:.4f}{' ':>12}")
    print(f"  {'Interaction coef':30} {'0.012':>18} {interact_t5['coef']:.4f}{' ':>12}")
    print(f"  {'Mechanism':30} {'economic':>18} {'governance quality':>18}")
    sim_viable = "YES" if t5_sig else "NO"
    print(f"  {'Simulation viable':30} {'No (small effect)':>18} {sim_viable:>18}")


if __name__ == "__main__":
    main()
