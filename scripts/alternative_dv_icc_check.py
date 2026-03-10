"""
Alternative DV ICC Check: Trust in Parliament and Democratic Satisfaction

Runs null models and cross-level interaction models for two alternative DVs
to contextualize the redistribution ICC (7.7%) from notebook 03.

Usage:
    python -m scripts.alternative_dv_icc_check
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config


def load_data():
    """Load analysis dataset and supplement with trstprl from raw ESS."""
    df = pd.read_csv(config.PROCESSED_DATA_DIR / "analysis_data.csv", low_memory=False)

    # trstprl was consumed into political_trust composite during processing
    # Load it directly from the raw Stata file
    import pyreadstat
    raw, _ = pyreadstat.read_dta(
        str(config.ESS_FILE),
        usecols=["idno", "cntry", "trstprl"],
    )
    raw = raw.rename(columns={"cntry": "country"})

    # Merge on idno + country; drop any pre-existing trstprl column
    if "trstprl" in df.columns:
        df = df.drop(columns=["trstprl"])
    df = df.merge(raw, on=["idno", "country"], how="left")

    # Force numeric (Stata reader returns mixed int/float as object)
    df["trstprl"] = pd.to_numeric(df["trstprl"], errors="coerce")
    # ESS codes 77/88/99 as missing
    df.loc[df["trstprl"] > 10, "trstprl"] = np.nan

    return df


def run_null_model(df, dv, dv_label):
    """Run intercept-only mixed model and extract ICC components."""
    subset = df[[dv, "country"]].dropna()
    n_ind = len(subset)
    n_countries = subset["country"].nunique()

    model = smf.mixedlm(f"{dv} ~ 1", data=subset, groups=subset["country"])
    result = model.fit(reml=True)

    tau = result.cov_re.iloc[0, 0]
    sigma2 = result.scale
    icc = tau / (tau + sigma2)

    print(f"\n{'='*60}")
    print(f"  Null Model: {dv_label} ({dv})")
    print(f"{'='*60}")
    print(f"  N individuals: {n_ind:,}")
    print(f"  N countries:   {n_countries}")
    print(f"  tau (between): {tau:.4f}")
    print(f"  sigma2 (within): {sigma2:.4f}")
    print(f"  ICC:           {icc:.4f} ({icc*100:.1f}%)")

    return {"dv": dv, "label": dv_label, "icc": icc, "n_ind": n_ind,
            "n_countries": n_countries, "tau": tau, "sigma2": sigma2}


def run_interaction_model(df, dv, dv_label):
    """Run income x Gini cross-level interaction model mirroring M5 from notebook 03."""
    # Exclude political_trust_c when DV is trstprl (trstprl is a component of political_trust)
    l1_predictors = ["income_c", "education_c", "age_c", "female", "employed",
                     "ideology_c", "political_trust_c", "meritocracy_index_c"]
    if dv == "trstprl":
        l1_predictors = [v for v in l1_predictors if v != "political_trust_c"]

    model_vars = [dv] + l1_predictors + ["gini_z", "gdp_per_capita_z", "unemployment_rate_z", "country"]
    subset = df[model_vars].dropna()

    l1_str = " + ".join(l1_predictors)
    formula = (f"{dv} ~ {l1_str} + "
               f"gini_z + gdp_per_capita_z + unemployment_rate_z + income_c:gini_z")

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Try with random slope for income first (matches M5)
        try:
            model = smf.mixedlm(formula, data=subset, groups=subset["country"],
                                 re_formula="~income_c")
            result = model.fit(reml=True)
            se = result.bse.get("income_c:gini_z", np.nan)
            # If SE is nan, the random slope hit boundary - fall back to random intercept
            if np.isnan(se):
                raise ValueError("Boundary convergence")
            re_spec = "random slope for income"
        except (ValueError, np.linalg.LinAlgError):
            # Fall back to random intercept only
            model = smf.mixedlm(formula, data=subset, groups=subset["country"])
            result = model.fit(reml=True)
            re_spec = "random intercept only"

    coef = result.fe_params.get("income_c:gini_z", np.nan)
    pval = result.pvalues.get("income_c:gini_z", np.nan)
    se = result.bse.get("income_c:gini_z", np.nan)

    print(f"\n  Income x Gini interaction model for {dv_label} ({re_spec}):")
    print(f"    N = {len(subset):,} in {subset['country'].nunique()} countries")
    print(f"    income_c:gini_z  coef = {coef:.6f}, SE = {se:.6f}, p = {pval:.4f}")
    print(f"    {'Significant' if pval < 0.05 else 'Not significant'} at alpha = 0.05")
    print(f"\n    Full fixed effects:")
    for param in result.fe_params.index:
        c = result.fe_params[param]
        p = result.pvalues[param]
        s = result.bse[param]
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"      {param:<25} {c:>10.4f} ({s:.4f}){sig}")

    return {"coef": coef, "se": se, "pval": pval, "n_ind": len(subset),
            "n_countries": subset["country"].nunique(), "re_spec": re_spec}


def main():
    df = load_data()
    print(f"  {len(df):,} observations, {df['country'].nunique()} countries")

    # Reference: redistribution ICC from notebook 03
    redist = run_null_model(df, "redist_support", "Redistribution (gincdif)")
    trust = run_null_model(df, "trstprl", "Trust in parliament")
    demsat = run_null_model(df, "stfdem", "Satisfaction with democracy")

    # Run interaction model if trust ICC > redistribution ICC
    trust_interaction = None
    if trust["icc"] > redist["icc"]:
        trust_interaction = run_interaction_model(df, "trstprl", "Trust in parliament")

    # Comparison table
    lines = []
    lines.append("")
    lines.append("=" * 80)
    lines.append("  ALTERNATIVE DV ICC COMPARISON")
    lines.append("=" * 80)
    lines.append("")
    header = f"  {'DV':<30} {'ICC':>8} {'N_ind':>10} {'N_countries':>12} {'tau':>10} {'sigma2':>10}"
    lines.append(header)
    lines.append("  " + "-" * 78)
    for r in [redist, trust, demsat]:
        lines.append(
            f"  {r['label']:<30} {r['icc']*100:>7.1f}% {r['n_ind']:>10,} {r['n_countries']:>12} "
            f"{r['tau']:>10.4f} {r['sigma2']:>10.4f}"
        )

    if trust_interaction:
        lines.append("")
        lines.append(f"  Trust ICC ({trust['icc']*100:.1f}%) > Redistribution ICC ({redist['icc']*100:.1f}%):")
        lines.append(f"    Income x Gini interaction for trust: "
                     f"coef = {trust_interaction['coef']:.6f}, "
                     f"SE = {trust_interaction['se']:.6f}, "
                     f"p = {trust_interaction['pval']:.4f}")
        sig = "Significant" if trust_interaction["pval"] < 0.05 else "Not significant"
        lines.append(f"    {sig} at alpha = 0.05")
    else:
        lines.append("")
        lines.append(f"  Trust ICC ({trust['icc']*100:.1f}%) <= Redistribution ICC ({redist['icc']*100:.1f}%):")
        lines.append("    Skipping interaction model for trust.")

    output = "\n".join(lines)
    print(output)

    # Save
    out_path = PROJECT_ROOT / "outputs" / "alternative_dv_icc_results.txt"
    with open(out_path, "w") as f:
        f.write(output)
    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()
