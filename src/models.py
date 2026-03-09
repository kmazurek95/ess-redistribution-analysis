"""
Multilevel Modeling Functions for ESS Redistribution Analysis

This module provides functions for running multilevel/hierarchical linear models
using pymer4, calculating model diagnostics, and creating regression tables.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pymer4.models import Lmer

import config


def run_null_model(
    df: pd.DataFrame,
    outcome: str,
    group_var: str = None
) -> Lmer:
    """
    Run null model (random intercept only, no predictors) to calculate ICC.

    Args:
        df: DataFrame containing data
        outcome: Name of outcome variable
        group_var: Grouping variable (e.g., country). If None, uses config.COUNTRY_VAR

    Returns:
        Fitted pymer4 Lmer model
    """
    logger = logging.getLogger("ess_analysis")

    if group_var is None:
        group_var = config.COUNTRY_VAR

    # Formula: outcome ~ 1 + (1|group)
    formula = f"{outcome} ~ 1 + (1|{group_var})"

    logger.info(f"Running null model: {formula}")

    # Fit model
    model = Lmer(formula, data=df)
    model.fit(REML=True, summarize=False)

    # Calculate and log ICC
    icc = calculate_icc(model)
    logger.info(f"ICC = {icc:.4f} ({icc*100:.2f}% variance at country level)")

    return model


def run_random_intercept(
    df: pd.DataFrame,
    formula: str,
    group_var: str = None,
    REML: bool = True
) -> Lmer:
    """
    Run random intercept model.

    Args:
        df: DataFrame containing data
        formula: Model formula (pymer4/lme4 syntax)
        group_var: Grouping variable. If None, uses config.COUNTRY_VAR
        REML: Whether to use REML estimation (default: True)

    Returns:
        Fitted pymer4 Lmer model

    Example:
        formula = "redist_support_c ~ hinctnta_c + (1|cntry)"
    """
    logger = logging.getLogger("ess_analysis")

    if group_var is None:
        group_var = config.COUNTRY_VAR

    logger.info(f"Running random intercept model: {formula}")

    # Fit model
    model = Lmer(formula, data=df)
    model.fit(REML=REML, summarize=False)

    logger.info("Model fitted successfully")

    return model


def run_random_slope(
    df: pd.DataFrame,
    formula: str,
    group_var: str = None,
    random_effects: Optional[List[str]] = None,
    REML: bool = True
) -> Lmer:
    """
    Run random slope model.

    Args:
        df: DataFrame containing data
        formula: Model formula with random slopes
        group_var: Grouping variable. If None, uses config.COUNTRY_VAR
        random_effects: List of variables with random slopes
        REML: Whether to use REML estimation (default: True)

    Returns:
        Fitted pymer4 Lmer model

    Example:
        formula = "redist_support ~ hinctnta_c + trstprl_c + (hinctnta_c + trstprl_c|cntry)"
        random_effects = ["hinctnta_c", "trstprl_c"]
    """
    logger = logging.getLogger("ess_analysis")

    if group_var is None:
        group_var = config.COUNTRY_VAR

    logger.info(f"Running random slope model: {formula}")
    if random_effects:
        logger.info(f"Random slopes for: {random_effects}")

    # Fit model
    model = Lmer(formula, data=df)
    model.fit(REML=REML, summarize=False)

    logger.info("Model fitted successfully")

    return model


def calculate_icc(model: Lmer) -> float:
    """
    Calculate Intraclass Correlation Coefficient (ICC) from fitted model.

    The ICC represents the proportion of variance at the group level.

    Args:
        model: Fitted pymer4 Lmer model

    Returns:
        ICC value (between 0 and 1)
    """
    # Extract variance components
    var_components = model.ranef_var

    # ICC = var_between / (var_between + var_within)
    # var_between = random intercept variance
    # var_within = residual variance

    try:
        var_between = var_components.loc["Intercept", "Var"]
        var_within = var_components.loc["Residual", "Var"]

        icc = var_between / (var_between + var_within)
        return icc

    except (KeyError, AttributeError):
        logging.getLogger("ess_analysis").warning("Could not extract variance components for ICC")
        return np.nan


def calculate_variance_explained(
    model_baseline: Lmer,
    model_full: Lmer,
    level: str = "total"
) -> float:
    """
    Calculate percentage of variance explained by comparing two models.

    Args:
        model_baseline: Baseline model (fewer predictors)
        model_full: Full model (more predictors)
        level: Level of variance ('total', 'between', or 'within')

    Returns:
        Percentage of variance explained (R²)
    """
    logger = logging.getLogger("ess_analysis")

    try:
        var_baseline = model_baseline.ranef_var
        var_full = model_full.ranef_var

        if level == "total":
            # Total variance = between + within
            baseline_total = var_baseline["Var"].sum()
            full_total = var_full["Var"].sum()
            r2 = 1 - (full_total / baseline_total)

        elif level == "between":
            # Between-group variance (intercept)
            baseline_between = var_baseline.loc["Intercept", "Var"]
            full_between = var_full.loc["Intercept", "Var"]
            r2 = 1 - (full_between / baseline_between)

        elif level == "within":
            # Within-group variance (residual)
            baseline_within = var_baseline.loc["Residual", "Var"]
            full_within = var_full.loc["Residual", "Var"]
            r2 = 1 - (full_within / baseline_within)

        else:
            raise ValueError(f"Unknown level: {level}")

        logger.info(f"Variance explained ({level}): {r2*100:.2f}%")
        return r2

    except (KeyError, AttributeError) as e:
        logger.warning(f"Could not calculate variance explained: {e}")
        return np.nan


def create_regression_table(
    models_list: List[Tuple[str, Lmer]],
    output_format: str = "dataframe"
) -> pd.DataFrame:
    """
    Create publication-ready regression table from multiple models.

    Args:
        models_list: List of tuples (model_name, fitted_model)
        output_format: Output format ('dataframe', 'latex', or 'html')

    Returns:
        DataFrame (or string if latex/html) with formatted regression table
    """
    logger = logging.getLogger("ess_analysis")

    results_dict = {}

    for model_name, model in models_list:
        # Extract coefficients
        coefs = model.coefs

        # Create formatted output: coef (SE)
        for idx, row in coefs.iterrows():
            var_name = row["Predictor"]
            coef = row["Estimate"]
            se = row["SE"]
            p = row["P-val"]

            # Format: "0.123 (0.045)***"
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

    # Convert to DataFrame
    results_df = pd.DataFrame(results_dict).T

    # Add model statistics
    model_stats = {}
    for model_name, model in models_list:
        model_stats[model_name] = {
            "N": int(model.data.shape[0]),
            "Log Likelihood": f"{model.logLike:.2f}",
            "AIC": f"{model.AIC:.2f}",
            "BIC": f"{model.BIC:.2f}",
        }

    stats_df = pd.DataFrame(model_stats).T

    logger.info(f"Created regression table with {len(models_list)} models")

    if output_format == "dataframe":
        return results_df
    elif output_format == "latex":
        return results_df.to_latex()
    elif output_format == "html":
        return results_df.to_html()
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def run_replication_sequence(
    df: pd.DataFrame,
    outcome: str = None,
    group_var: str = None
) -> Dict[str, Lmer]:
    """
    Run the full 7-model sequence from the original thesis.

    Args:
        df: Analysis-ready DataFrame
        outcome: Name of outcome variable. If None, uses config.OUTCOME_VAR_REVERSED
        group_var: Grouping variable. If None, uses config.COUNTRY_VAR

    Returns:
        Dictionary of {model_number: fitted_model}
    """
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED

    if group_var is None:
        group_var = config.COUNTRY_VAR

    logger.info("Running 7-model replication sequence...")

    models = {}

    # Model 1: Null model
    logger.info("Model 1: Null model (random intercept only)")
    models["Model 1"] = run_null_model(df, outcome, group_var)

    # Model 2: Add income
    logger.info("Model 2: Add income")
    formula_m2 = f"{outcome} ~ hinctnta_c + (1|{group_var})"
    models["Model 2"] = run_random_intercept(df, formula_m2, group_var)

    # Model 3: Add political trust
    logger.info("Model 3: Add political trust")
    formula_m3 = f"{outcome} ~ hinctnta_c + trstprl_c + (1|{group_var})"
    models["Model 3"] = run_random_intercept(df, formula_m3, group_var)

    # Model 4: Add all Level-1 controls
    logger.info("Model 4: Add all Level-1 controls")
    formula_m4 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + (1|{group_var})"
    models["Model 4"] = run_random_intercept(df, formula_m4, group_var)

    # Model 5: Add Level-2 variables
    logger.info("Model 5: Add Level-2 variables")
    formula_m5 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + gini_z + gdp_z + unemployment_z + political_trust_l2 + (1|{group_var})"
    models["Model 5"] = run_random_intercept(df, formula_m5, group_var)

    # Model 6: Random slopes
    logger.info("Model 6: Random slopes for income and political trust")
    formula_m6 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + gini_z + gdp_z + unemployment_z + political_trust_l2 + (hinctnta_c + trstprl_c|{group_var})"
    models["Model 6"] = run_random_slope(df, formula_m6, group_var, ["hinctnta_c", "trstprl_c"])

    # Model 7: Cross-level interactions
    logger.info("Model 7: Cross-level interactions")
    formula_m7 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + gini_z + gdp_z + unemployment_z + political_trust_l2 + hinctnta_c:gini_z + trstprl_c:gdp_z + (hinctnta_c + trstprl_c|{group_var})"
    models["Model 7"] = run_random_slope(df, formula_m7, group_var, ["hinctnta_c", "trstprl_c"])

    logger.info("Replication sequence complete!")

    return models


def run_regime_models(
    df: pd.DataFrame,
    outcome: str = None,
    group_var: str = None,
    regime_var: str = "welfare_regime"
) -> Dict[str, Lmer]:
    """
    Run welfare regime extension models (Models 8-10).

    Args:
        df: Analysis-ready DataFrame
        outcome: Name of outcome variable
        group_var: Grouping variable
        regime_var: Name of regime classification variable

    Returns:
        Dictionary of {model_name: fitted_model}
    """
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED

    if group_var is None:
        group_var = config.COUNTRY_VAR

    logger.info("Running welfare regime extension models...")

    models = {}

    # Model 8: Regime as Level-2 predictor
    logger.info("Model 8: Welfare regime as Level-2 predictor")
    # Note: pymer4 handles categorical variables automatically
    formula_m8 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + C({regime_var}) + (1|{group_var})"
    models["Model 8"] = run_random_intercept(df, formula_m8, group_var)

    # Model 9: Income × Regime interaction
    logger.info("Model 9: Income × Welfare regime interaction")
    formula_m9 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + C({regime_var}) + hinctnta_c:C({regime_var}) + (hinctnta_c|{group_var})"
    models["Model 9"] = run_random_slope(df, formula_m9, group_var, ["hinctnta_c"])

    # Model 10: Political trust × Regime interaction
    logger.info("Model 10: Political trust × Welfare regime interaction")
    formula_m10 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + C({regime_var}) + trstprl_c:C({regime_var}) + (trstprl_c|{group_var})"
    models["Model 10"] = run_random_slope(df, formula_m10, group_var, ["trstprl_c"])

    logger.info("Regime models complete!")

    return models


def run_institutional_models(
    df: pd.DataFrame,
    outcome: str = None,
    group_var: str = None
) -> Dict[str, Lmer]:
    """
    Run institutional mediation models (Models 11-13).

    Args:
        df: Analysis-ready DataFrame
        outcome: Name of outcome variable
        group_var: Grouping variable

    Returns:
        Dictionary of {model_name: fitted_model}
    """
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED

    if group_var is None:
        group_var = config.COUNTRY_VAR

    logger.info("Running institutional mediation models...")

    models = {}

    # Model 11: Institutional indicators as Level-2 predictors
    logger.info("Model 11: EPL and ALMP as Level-2 predictors")
    formula_m11 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + epl_z + almp_spending_z + union_density_z + social_spending_z + (1|{group_var})"
    models["Model 11"] = run_random_intercept(df, formula_m11, group_var)

    # Model 12: Income × EPL interaction
    logger.info("Model 12: Income × EPL interaction")
    formula_m12 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + epl_z + almp_spending_z + hinctnta_c:epl_z + (hinctnta_c|{group_var})"
    models["Model 12"] = run_random_slope(df, formula_m12, group_var, ["hinctnta_c"])

    # Model 13: Income × ALMP interaction
    logger.info("Model 13: Income × ALMP interaction")
    formula_m13 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + epl_z + almp_spending_z + hinctnta_c:almp_spending_z + (hinctnta_c|{group_var})"
    models["Model 13"] = run_random_slope(df, formula_m13, group_var, ["hinctnta_c"])

    logger.info("Institutional models complete!")

    return models


def run_ai_exposure_models(
    df: pd.DataFrame,
    outcome: str = None,
    group_var: str = None,
    regime_var: str = "welfare_regime"
) -> Dict[str, Lmer]:
    """
    Run AI/automation exposure extension models (Models 14-16).

    Args:
        df: Analysis-ready DataFrame
        outcome: Name of outcome variable
        group_var: Grouping variable
        regime_var: Name of regime classification variable

    Returns:
        Dictionary of {model_name: fitted_model}
    """
    logger = logging.getLogger("ess_analysis")

    if outcome is None:
        outcome = config.OUTCOME_VAR_REVERSED

    if group_var is None:
        group_var = config.COUNTRY_VAR

    logger.info("Running AI exposure extension models...")

    models = {}

    # Model 14: AI exposure as Level-2 predictor
    logger.info("Model 14: AI/automation exposure as Level-2 predictor")
    formula_m14 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + ai_exposure_oecd_z + (1|{group_var})"
    models["Model 14"] = run_random_intercept(df, formula_m14, group_var)

    # Model 15: Income × AI exposure interaction
    logger.info("Model 15: Income × AI exposure interaction")
    formula_m15 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + ai_exposure_oecd_z + hinctnta_c:ai_exposure_oecd_z + (hinctnta_c|{group_var})"
    models["Model 15"] = run_random_slope(df, formula_m15, group_var, ["hinctnta_c"])

    # Model 16: AI exposure × Welfare regime interaction
    logger.info("Model 16: AI exposure × Welfare regime interaction")
    formula_m16 = f"{outcome} ~ hinctnta_c + trstprl_c + agea_c + female + eduyrs_c + meritocracy_c + ai_exposure_oecd_z + C({regime_var}) + ai_exposure_oecd_z:C({regime_var}) + (1|{group_var})"
    models["Model 16"] = run_random_intercept(df, formula_m16, group_var)

    logger.info("AI exposure models complete!")

    return models
