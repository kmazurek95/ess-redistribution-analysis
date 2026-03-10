"""Multilevel modeling functions using pymer4."""

import logging

import numpy as np
import pandas as pd
from pymer4.models import Lmer

import config


def run_null_model(df, outcome, group_var=None):
    """Run null model (random intercept only) to calculate ICC."""
    logger = logging.getLogger("ess_analysis")

    if group_var is None:
        group_var = config.COUNTRY_VAR

    formula = f"{outcome} ~ 1 + (1|{group_var})"
    model = Lmer(formula, data=df)
    model.fit(REML=True, summarize=False)

    icc = calculate_icc(model)
    logger.info(f"Null model ICC = {icc:.4f} ({icc*100:.2f}% variance at country level)")

    return model


def run_random_intercept(df, formula, group_var=None, REML=True):
    """Run random intercept model."""
    if group_var is None:
        group_var = config.COUNTRY_VAR

    model = Lmer(formula, data=df)
    model.fit(REML=REML, summarize=False)
    return model


def run_random_slope(df, formula, group_var=None, random_effects=None, REML=True):
    """Run random slope model."""
    if group_var is None:
        group_var = config.COUNTRY_VAR

    model = Lmer(formula, data=df)
    model.fit(REML=REML, summarize=False)
    return model


def calculate_icc(model):
    """Calculate Intraclass Correlation Coefficient from fitted model."""
    try:
        var_components = model.ranef_var
        var_between = var_components.loc["Intercept", "Var"]
        var_within = var_components.loc["Residual", "Var"]
        return var_between / (var_between + var_within)
    except (KeyError, AttributeError):
        logging.getLogger("ess_analysis").warning("Could not extract variance components for ICC")
        return np.nan


def calculate_variance_explained(model_baseline, model_full, level="total"):
    """Calculate R-squared by comparing variance components of two models."""
    logger = logging.getLogger("ess_analysis")

    try:
        var_baseline = model_baseline.ranef_var
        var_full = model_full.ranef_var

        if level == "total":
            r2 = 1 - (var_full["Var"].sum() / var_baseline["Var"].sum())
        elif level == "between":
            r2 = 1 - (var_full.loc["Intercept", "Var"] / var_baseline.loc["Intercept", "Var"])
        elif level == "within":
            r2 = 1 - (var_full.loc["Residual", "Var"] / var_baseline.loc["Residual", "Var"])
        else:
            raise ValueError(f"Unknown level: {level}")

        logger.info(f"Variance explained ({level}): {r2*100:.2f}%")
        return r2

    except (KeyError, AttributeError) as e:
        logger.warning(f"Could not calculate variance explained: {e}")
        return np.nan


def create_regression_table(models_list, output_format="dataframe"):
    """Create publication-ready regression table from multiple models."""
    results_dict = {}

    for model_name, model in models_list:
        coefs = model.coefs
        for idx, row in coefs.iterrows():
            var_name = row["Predictor"]
            coef = row["Estimate"]
            se = row["SE"]
            p = row["P-val"]

            sig_stars = ""
            if p < 0.001:
                sig_stars = "***"
            elif p < 0.01:
                sig_stars = "**"
            elif p < 0.05:
                sig_stars = "*"

            formatted = f"{coef:.3f} ({se:.3f}){sig_stars}"

            if var_name not in results_dict:
                results_dict[var_name] = {}
            results_dict[var_name][model_name] = formatted

    results_df = pd.DataFrame(results_dict).T

    if output_format == "dataframe":
        return results_df
    elif output_format == "latex":
        return results_df.to_latex()
    elif output_format == "html":
        return results_df.to_html()
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def run_replication_sequence(df, outcome=None, group_var=None):
    """Run the full 7-model replication sequence."""
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED
    if group_var is None:
        group_var = config.COUNTRY_VAR

    models = {}

    models["Model 1"] = run_null_model(df, outcome, group_var)

    formula_m2 = f"{outcome} ~ hinctnta_c + (1|{group_var})"
    models["Model 2"] = run_random_intercept(df, formula_m2, group_var)

    formula_m3 = f"{outcome} ~ hinctnta_c + trstprl_c + (1|{group_var})"
    models["Model 3"] = run_random_intercept(df, formula_m3, group_var)

    formula_m4 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + (1|{group_var})"
    models["Model 4"] = run_random_intercept(df, formula_m4, group_var)

    formula_m5 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + gini_z + gdp_z + unemployment_z + political_trust_l2 + (1|{group_var})"
    models["Model 5"] = run_random_intercept(df, formula_m5, group_var)

    formula_m6 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + gini_z + gdp_z + unemployment_z + political_trust_l2 + (hinctnta_c + trstprl_c|{group_var})"
    models["Model 6"] = run_random_slope(df, formula_m6, group_var, ["hinctnta_c", "trstprl_c"])

    formula_m7 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + gini_z + gdp_z + unemployment_z + political_trust_l2 + hinctnta_c:gini_z + trstprl_c:gdp_z + (hinctnta_c + trstprl_c|{group_var})"
    models["Model 7"] = run_random_slope(df, formula_m7, group_var, ["hinctnta_c", "trstprl_c"])

    logger.info(f"Replication sequence complete: {len(models)} models fitted")
    return models


def run_regime_models(df, outcome=None, group_var=None, regime_var="welfare_regime"):
    """Run welfare regime extension models (Models 8-10)."""
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED
    if group_var is None:
        group_var = config.COUNTRY_VAR

    models = {}

    formula_m8 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + C({regime_var}) + (1|{group_var})"
    models["Model 8"] = run_random_intercept(df, formula_m8, group_var)

    formula_m9 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + C({regime_var}) + hinctnta_c:C({regime_var}) + (hinctnta_c|{group_var})"
    models["Model 9"] = run_random_slope(df, formula_m9, group_var, ["hinctnta_c"])

    formula_m10 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + C({regime_var}) + trstprl_c:C({regime_var}) + (trstprl_c|{group_var})"
    models["Model 10"] = run_random_slope(df, formula_m10, group_var, ["trstprl_c"])

    logger.info(f"Regime models complete: {len(models)} models fitted")
    return models


def run_institutional_models(df, outcome=None, group_var=None):
    """Run institutional mediation models (Models 11-13)."""
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED
    if group_var is None:
        group_var = config.COUNTRY_VAR

    models = {}

    formula_m11 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + epl_z + almp_spending_z + union_density_z + social_spending_z + (1|{group_var})"
    models["Model 11"] = run_random_intercept(df, formula_m11, group_var)

    formula_m12 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + epl_z + almp_spending_z + hinctnta_c:epl_z + (hinctnta_c|{group_var})"
    models["Model 12"] = run_random_slope(df, formula_m12, group_var, ["hinctnta_c"])

    formula_m13 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + epl_z + almp_spending_z + hinctnta_c:almp_spending_z + (hinctnta_c|{group_var})"
    models["Model 13"] = run_random_slope(df, formula_m13, group_var, ["hinctnta_c"])

    logger.info(f"Institutional models complete: {len(models)} models fitted")
    return models


def run_ai_exposure_models(df, outcome=None, group_var=None, regime_var="welfare_regime"):
    """Run AI/automation exposure extension models (Models 14-16)."""
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED
    if group_var is None:
        group_var = config.COUNTRY_VAR

    models = {}

    formula_m14 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + ai_exposure_oecd_z + (1|{group_var})"
    models["Model 14"] = run_random_intercept(df, formula_m14, group_var)

    formula_m15 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + ai_exposure_oecd_z + hinctnta_c:ai_exposure_oecd_z + (hinctnta_c|{group_var})"
    models["Model 15"] = run_random_slope(df, formula_m15, group_var, ["hinctnta_c"])

    formula_m16 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + ai_exposure_oecd_z + C({regime_var}) + ai_exposure_oecd_z:C({regime_var}) + (1|{group_var})"
    models["Model 16"] = run_random_intercept(df, formula_m16, group_var)

    logger.info(f"AI exposure models complete: {len(models)} models fitted")
    return models
