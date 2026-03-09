"""
Data Preparation Functions for ESS Redistribution Analysis

This module provides functions for data transformation, variable creation,
centering/standardization, and complete dataset preparation pipeline.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def reverse_code(
    series: pd.Series,
    max_val: int,
    min_val: int = 1
) -> pd.Series:
    """
    Reverse code a Likert scale variable.

    Args:
        series: Pandas Series to reverse code
        max_val: Maximum value of original scale
        min_val: Minimum value of original scale (default: 1)

    Returns:
        Reverse-coded Series
    """
    return (max_val + min_val) - series


def create_meritocracy_index(
    df: pd.DataFrame,
    merit_effort_var: Optional[str] = None,
    merit_deserve_var: Optional[str] = None,
    index_name: str = "meritocracy"
) -> pd.DataFrame:
    """
    Create meritocracy index by averaging two meritocracy items.

    Args:
        df: DataFrame containing meritocracy items
        merit_effort_var: Name of 'fair to earn more if work hard' variable
        merit_deserve_var: Name of 'people get what deserve' variable
        index_name: Name for the created index variable

    Returns:
        DataFrame with meritocracy index added
    """
    logger = logging.getLogger("ess_analysis")

    # Use config defaults if not specified
    if merit_effort_var is None:
        merit_effort_var = config.LEVEL1_VARS["merit_effort"]
    if merit_deserve_var is None:
        merit_deserve_var = config.LEVEL1_VARS["merit_deserve"]

    # Check variables exist
    if merit_effort_var not in df.columns or merit_deserve_var not in df.columns:
        logger.error(
            f"Meritocracy variables not found: {merit_effort_var}, {merit_deserve_var}"
        )
        return df

    # Create index (mean of two items)
    df[index_name] = df[[merit_effort_var, merit_deserve_var]].mean(axis=1)

    # Report statistics
    n_complete = df[index_name].notna().sum()
    logger.info(
        f"Created meritocracy index '{index_name}': "
        f"mean={df[index_name].mean():.2f}, n={n_complete:,}"
    )

    return df


def center_variables(
    df: pd.DataFrame,
    vars_to_center: List[str],
    group_var: Optional[str] = None,
    suffix: str = "_c"
) -> pd.DataFrame:
    """
    Grand-mean center Level-1 variables (or group-mean center if group_var specified).

    Args:
        df: DataFrame containing variables
        vars_to_center: List of variable names to center
        group_var: If provided, performs group-mean centering within groups
        suffix: Suffix for centered variable names (default: '_c')

    Returns:
        DataFrame with centered variables added
    """
    logger = logging.getLogger("ess_analysis")

    for var in vars_to_center:
        if var not in df.columns:
            logger.warning(f"Variable '{var}' not found, skipping")
            continue

        centered_name = f"{var}{suffix}"

        if group_var is None:
            # Grand-mean centering
            grand_mean = df[var].mean()
            df[centered_name] = df[var] - grand_mean
            logger.info(
                f"Grand-mean centered '{var}' (mean={grand_mean:.2f}) → '{centered_name}'"
            )
        else:
            # Group-mean centering
            if group_var not in df.columns:
                logger.error(f"Group variable '{group_var}' not found")
                continue

            group_means = df.groupby(group_var)[var].transform("mean")
            df[centered_name] = df[var] - group_means
            logger.info(f"Group-mean centered '{var}' within '{group_var}' → '{centered_name}'")

    return df


def standardize_variables(
    df: pd.DataFrame,
    vars_to_standardize: List[str],
    suffix: str = "_z"
) -> pd.DataFrame:
    """
    Z-score standardize Level-2 variables (mean=0, sd=1).

    Args:
        df: DataFrame containing variables
        vars_to_standardize: List of variable names to standardize
        suffix: Suffix for standardized variable names (default: '_z')

    Returns:
        DataFrame with standardized variables added
    """
    logger = logging.getLogger("ess_analysis")

    for var in vars_to_standardize:
        if var not in df.columns:
            logger.warning(f"Variable '{var}' not found, skipping")
            continue

        standardized_name = f"{var}{suffix}"

        # Calculate z-score
        mean = df[var].mean()
        std = df[var].std()

        if std == 0:
            logger.warning(f"Variable '{var}' has zero variance, cannot standardize")
            continue

        df[standardized_name] = (df[var] - mean) / std

        logger.info(
            f"Standardized '{var}' (mean={mean:.2f}, sd={std:.2f}) → '{standardized_name}'"
        )

    return df


def assign_welfare_regime(
    df: pd.DataFrame,
    country_var: Optional[str] = None,
    classification: str = "esping_andersen",
    regime_var_name: str = "welfare_regime"
) -> pd.DataFrame:
    """
    Assign welfare regime classification to each country.

    Args:
        df: DataFrame containing country variable
        country_var: Name of country variable. If None, uses config.COUNTRY_VAR
        classification: Type of classification ('esping_andersen' or 'voc')
        regime_var_name: Name for created regime variable

    Returns:
        DataFrame with regime classification added
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if country_var not in df.columns:
        logger.error(f"Country variable '{country_var}' not found")
        return df

    # Select classification mapping
    if classification == "esping_andersen":
        country_to_regime = config.COUNTRY_TO_REGIME_ESPING
        logger.info("Using Esping-Andersen welfare regime classification")
    elif classification == "voc":
        country_to_regime = config.COUNTRY_TO_REGIME_VOC
        logger.info("Using Varieties of Capitalism classification")
    else:
        raise ValueError(
            f"Unknown classification: {classification}. "
            "Use 'esping_andersen' or 'voc'"
        )

    # Assign regime
    df[regime_var_name] = df[country_var].map(country_to_regime)

    # Report
    n_assigned = df[regime_var_name].notna().sum()
    n_total = len(df)
    logger.info(
        f"Assigned regime classification to {n_assigned:,}/{n_total:,} observations"
    )

    # Show distribution
    regime_counts = df[regime_var_name].value_counts()
    logger.info(f"Regime distribution:\n{regime_counts}")

    return df


def create_institutional_indices(
    df: pd.DataFrame,
    index_name: str = "institutional_strength",
    components: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Create composite institutional strength index.

    Args:
        df: DataFrame containing institutional indicators
        index_name: Name for the composite index
        components: List of component variables. If None, uses EPL, ALMP, union_density, social_spending

    Returns:
        DataFrame with composite index added
    """
    logger = logging.getLogger("ess_analysis")

    if components is None:
        components = ["epl", "almp_spending", "union_density", "social_spending"]

    # Check which components are available
    available_components = [c for c in components if c in df.columns]

    if len(available_components) == 0:
        logger.warning("No institutional indicators available to create composite index")
        return df

    if len(available_components) < len(components):
        missing = set(components) - set(available_components)
        logger.warning(f"Some components missing: {missing}")

    # Standardize each component (z-score)
    component_zscores = []
    for comp in available_components:
        z = (df[comp] - df[comp].mean()) / df[comp].std()
        component_zscores.append(z)

    # Average standardized components
    df[index_name] = pd.concat(component_zscores, axis=1).mean(axis=1)

    logger.info(
        f"Created institutional index '{index_name}' from {len(available_components)} components"
    )

    return df


def create_analysis_dataset(
    ess_df: Optional[pd.DataFrame] = None,
    country_df: Optional[pd.DataFrame] = None,
    institutional_df: Optional[pd.DataFrame] = None,
    ai_df: Optional[pd.DataFrame] = None,
    reverse_outcome: bool = True,
    create_meritocracy: bool = True,
    center_level1: bool = True,
    standardize_level2: bool = True,
    assign_regimes: bool = True
) -> pd.DataFrame:
    """
    Complete pipeline from raw data to analysis-ready dataset.

    Args:
        ess_df: ESS DataFrame. If None, loads from config.ESS_FILE
        country_df: Country-level DataFrame. If None, loads from config files
        institutional_df: Institutional DataFrame. If None, loads from config.INSTITUTIONAL_FILE
        ai_df: AI exposure DataFrame. If None, loads from config.AI_EXPOSURE_FILE
        reverse_outcome: Whether to reverse-code outcome variable
        create_meritocracy: Whether to create meritocracy index
        center_level1: Whether to grand-mean center Level-1 variables
        standardize_level2: Whether to z-score standardize Level-2 variables
        assign_regimes: Whether to assign welfare regime classifications

    Returns:
        Analysis-ready DataFrame
    """
    logger = logging.getLogger("ess_analysis")
    logger.info("Starting data preparation pipeline...")

    # Load data if not provided
    if ess_df is None:
        logger.info("Loading ESS data...")
        ess_df = load_ess_data()

    if country_df is None:
        logger.info("Loading country-level data...")
        country_df = load_country_data()

    if institutional_df is None:
        logger.info("Loading institutional data...")
        institutional_df = load_institutional_data()

    if ai_df is None:
        logger.info("Loading AI exposure data...")
        ai_df = load_ai_exposure_data()

    # Merge datasets
    logger.info("Merging datasets...")
    df = merge_country_data(ess_df, country_df)

    if len(institutional_df) > 0:
        df = merge_institutional_data(df, institutional_df)

    if len(ai_df) > 0:
        df = merge_ai_exposure_data(df, ai_df)

    # Reverse code outcome variable
    if reverse_outcome:
        logger.info("Reverse coding outcome variable...")
        outcome_var = config.OUTCOME_VAR
        if outcome_var in df.columns:
            df[config.OUTCOME_VAR_REVERSED] = reverse_code(df[outcome_var], max_val=5)
            logger.info(
                f"Created '{config.OUTCOME_VAR_REVERSED}' from reversed '{outcome_var}'"
            )

    # Create meritocracy index
    if create_meritocracy:
        logger.info("Creating meritocracy index...")
        df = create_meritocracy_index(df)

    # Center Level-1 variables
    if center_level1:
        logger.info("Centering Level-1 variables...")
        level1_to_center = [
            "hinctnta",  # income
            "trstprl",   # political trust
            "agea",      # age
            "eduyrs",    # education
            "meritocracy"  # created index
        ]
        # Only center variables that exist
        level1_to_center = [v for v in level1_to_center if v in df.columns]
        df = center_variables(df, level1_to_center)

    # Standardize Level-2 variables
    if standardize_level2:
        logger.info("Standardizing Level-2 variables...")
        level2_to_standardize = [
            "gini",
            "gdp",
            "unemployment",
        ]
        # Add institutional variables if available
        if "epl" in df.columns:
            level2_to_standardize.extend([
                "epl",
                "almp_spending",
                "union_density",
                "social_spending"
            ])
        # Add AI variables if available
        if "ai_exposure_oecd" in df.columns:
            level2_to_standardize.append("ai_exposure_oecd")
        if "automation_risk" in df.columns:
            level2_to_standardize.append("automation_risk")

        # Only standardize variables that exist
        level2_to_standardize = [v for v in level2_to_standardize if v in df.columns]
        df = standardize_variables(df, level2_to_standardize)

    # Assign welfare regime classifications
    if assign_regimes:
        logger.info("Assigning welfare regime classifications...")
        df = assign_welfare_regime(df, classification="esping_andersen")
        df = assign_welfare_regime(
            df,
            classification="voc",
            regime_var_name="voc_regime"
        )

    # Create dummy variables for gender
    if "gndr" in df.columns:
        df["female"] = (df["gndr"] == 2).astype(int)
        logger.info("Created 'female' dummy variable from 'gndr'")

    # Create employment dummy from pdwrk (paid work in last 7 days)
    if "pdwrk" in df.columns:
        df["employed"] = pd.to_numeric(df["pdwrk"], errors="coerce").eq(1).astype(int)
        logger.info("Created 'employed' dummy variable from 'pdwrk'")

    # Aggregate political trust to country level (Level-2)
    if "trstprl" in df.columns:
        country_var = config.COUNTRY_VAR
        df["political_trust_l2"] = df.groupby(country_var)["trstprl"].transform("mean")
        logger.info("Aggregated political trust to country level (political_trust_l2)")

    logger.info("Data preparation pipeline complete!")
    logger.info(f"Final dataset: {len(df):,} observations, {len(df.columns)} variables")

    return df


def save_processed_data(
    df: pd.DataFrame,
    filepath: Optional[Path] = None,
    format: str = "parquet"
) -> Path:
    """
    Save processed data to file.

    Args:
        df: DataFrame to save
        filepath: Path to save file. If None, uses config.PROCESSED_FILE
        format: File format ('parquet', 'csv', or 'stata')

    Returns:
        Path to saved file
    """
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.PROCESSED_FILE

    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Save based on format
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

    logger.info(f"Saved processed data to: {filepath}")
    return filepath


def load_processed_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """
    Load processed data from file.

    Args:
        filepath: Path to processed data file. If None, uses config.PROCESSED_FILE

    Returns:
        DataFrame with processed data
    """
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.PROCESSED_FILE

    if not filepath.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {filepath}\n"
            "Run 02_data_preparation.ipynb to create processed dataset."
        )

    # Load based on file extension
    if filepath.suffix == ".parquet":
        df = pd.read_parquet(filepath)
    elif filepath.suffix == ".csv":
        df = pd.read_csv(filepath)
    elif filepath.suffix == ".dta":
        df, _ = pyreadstat.read_dta(str(filepath))
    else:
        raise ValueError(f"Unknown file format: {filepath.suffix}")

    logger.info(f"Loaded processed data: {len(df):,} observations, {len(df.columns)} variables")

    return df
