"""Data transformation, variable creation, and dataset preparation pipeline."""

import logging

import numpy as np
import pandas as pd

import config
from src.data_loader import (
    load_ess_data,
    load_country_data,
    load_institutional_data,
    load_ai_exposure_data,
    merge_country_data,
    merge_institutional_data,
    merge_ai_exposure_data,
)


def reverse_code(series, max_val, min_val=1):
    return (max_val + min_val) - series


def create_meritocracy_index(df, merit_effort_var=None, merit_deserve_var=None, index_name="meritocracy"):
    """Average two meritocracy items into a single index."""
    logger = logging.getLogger("ess_analysis")

    if merit_effort_var is None:
        merit_effort_var = config.LEVEL1_VARS["merit_effort"]
    if merit_deserve_var is None:
        merit_deserve_var = config.LEVEL1_VARS["merit_deserve"]

    if merit_effort_var not in df.columns or merit_deserve_var not in df.columns:
        logger.error(f"Meritocracy variables not found: {merit_effort_var}, {merit_deserve_var}")
        return df

    df[index_name] = df[[merit_effort_var, merit_deserve_var]].mean(axis=1)

    return df


def center_variables(df, vars_to_center, group_var=None, suffix="_c"):
    """Grand-mean or group-mean center variables."""
    logger = logging.getLogger("ess_analysis")

    for var in vars_to_center:
        if var not in df.columns:
            logger.warning(f"Variable '{var}' not found, skipping")
            continue

        centered_name = f"{var}{suffix}"

        if group_var is None:
            grand_mean = df[var].mean()
            df[centered_name] = df[var] - grand_mean
        else:
            if group_var not in df.columns:
                logger.error(f"Group variable '{group_var}' not found")
                continue
            group_means = df.groupby(group_var)[var].transform("mean")
            df[centered_name] = df[var] - group_means

    return df


def standardize_variables(df, vars_to_standardize, suffix="_z"):
    """Z-score standardize variables (mean=0, sd=1)."""
    logger = logging.getLogger("ess_analysis")

    for var in vars_to_standardize:
        if var not in df.columns:
            logger.warning(f"Variable '{var}' not found, skipping")
            continue

        mean = df[var].mean()
        std = df[var].std()

        if std == 0:
            logger.warning(f"Variable '{var}' has zero variance, cannot standardize")
            continue

        df[f"{var}{suffix}"] = (df[var] - mean) / std

    return df


def assign_welfare_regime(df, country_var=None, classification="esping_andersen", regime_var_name="welfare_regime"):
    """Assign welfare regime classification to each country."""
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if country_var not in df.columns:
        logger.error(f"Country variable '{country_var}' not found")
        return df

    if classification == "esping_andersen":
        country_to_regime = config.COUNTRY_TO_REGIME_ESPING
    elif classification == "voc":
        country_to_regime = config.COUNTRY_TO_REGIME_VOC
    else:
        raise ValueError(f"Unknown classification: {classification}. Use 'esping_andersen' or 'voc'")

    df[regime_var_name] = df[country_var].map(country_to_regime)

    return df


def create_institutional_indices(df, index_name="institutional_strength", components=None):
    """Create composite institutional strength index from z-scored components."""
    logger = logging.getLogger("ess_analysis")

    if components is None:
        components = ["epl", "almp_spending", "union_density", "social_spending"]

    available_components = [c for c in components if c in df.columns]

    if len(available_components) == 0:
        logger.warning("No institutional indicators available to create composite index")
        return df

    if len(available_components) < len(components):
        missing = set(components) - set(available_components)
        logger.warning(f"Some components missing: {missing}")

    component_zscores = []
    for comp in available_components:
        z = (df[comp] - df[comp].mean()) / df[comp].std()
        component_zscores.append(z)

    df[index_name] = pd.concat(component_zscores, axis=1).mean(axis=1)

    return df


def create_analysis_dataset(
    ess_df=None, country_df=None, institutional_df=None, ai_df=None,
    reverse_outcome=True, create_meritocracy=True, center_level1=True,
    standardize_level2=True, assign_regimes=True
):
    """Complete pipeline from raw data to analysis-ready dataset."""
    if ess_df is None:
        ess_df = load_ess_data()
    if country_df is None:
        country_df = load_country_data()
    if institutional_df is None:
        institutional_df = load_institutional_data()
    if ai_df is None:
        ai_df = load_ai_exposure_data()

    df = merge_country_data(ess_df, country_df)

    if len(institutional_df) > 0:
        df = merge_institutional_data(df, institutional_df)
    if len(ai_df) > 0:
        df = merge_ai_exposure_data(df, ai_df)

    if reverse_outcome:
        outcome_var = config.OUTCOME_VAR
        if outcome_var in df.columns:
            df[config.OUTCOME_VAR_REVERSED] = reverse_code(df[outcome_var], max_val=5)

    if create_meritocracy:
        df = create_meritocracy_index(df)

    if center_level1:
        level1_to_center = [
            v for v in ["hinctnta", "trstprl", "agea", "eduyrs", "meritocracy"]
            if v in df.columns
        ]
        df = center_variables(df, level1_to_center)

    if standardize_level2:
        level2_to_standardize = ["gini", "gdp", "unemployment"]
        if "epl" in df.columns:
            level2_to_standardize.extend(["epl", "almp_spending", "union_density", "social_spending"])
        if "ai_exposure_oecd" in df.columns:
            level2_to_standardize.append("ai_exposure_oecd")
        if "automation_risk" in df.columns:
            level2_to_standardize.append("automation_risk")

        level2_to_standardize = [v for v in level2_to_standardize if v in df.columns]
        df = standardize_variables(df, level2_to_standardize)

    if assign_regimes:
        df = assign_welfare_regime(df, classification="esping_andersen")
        df = assign_welfare_regime(df, classification="voc", regime_var_name="voc_regime")

    if "gndr" in df.columns:
        df["female"] = (df["gndr"] == 2).astype(int)

    if "pdwrk" in df.columns:
        df["employed"] = pd.to_numeric(df["pdwrk"], errors="coerce").eq(1).astype(int)

    # Aggregate political trust to country level for use as Level-2 predictor
    if "trstprl" in df.columns:
        country_var = config.COUNTRY_VAR
        df["political_trust_l2"] = df.groupby(country_var)["trstprl"].transform("mean")

    return df


def save_processed_data(df, filepath=None, format="parquet"):
    """Save processed data to file."""
    if filepath is None:
        filepath = config.PROCESSED_FILE

    filepath.parent.mkdir(parents=True, exist_ok=True)

    if format == "parquet":
        df.to_parquet(filepath, index=False)
    elif format == "csv":
        if filepath.suffix != ".csv":
            filepath = filepath.with_suffix(".csv")
        df.to_csv(filepath, index=False)
    elif format == "stata":
        if filepath.suffix not in [".dta"]:
            filepath = filepath.with_suffix(".dta")
        df.to_stata(filepath, write_index=False)
    else:
        raise ValueError(f"Unknown format: {format}")

    return filepath


def load_processed_data(filepath=None):
    """Load processed data from file."""
    if filepath is None:
        filepath = config.PROCESSED_FILE

    if not filepath.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {filepath}\n"
            "Run 02_data_preparation.ipynb to create processed dataset."
        )

    if filepath.suffix == ".parquet":
        df = pd.read_parquet(filepath)
    elif filepath.suffix == ".csv":
        df = pd.read_csv(filepath)
    elif filepath.suffix == ".dta":
        import pyreadstat
        df, _ = pyreadstat.read_dta(str(filepath))
    else:
        raise ValueError(f"Unknown file format: {filepath.suffix}")

    return df
