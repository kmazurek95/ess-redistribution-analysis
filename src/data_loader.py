"""
Data Loading Functions for ESS Redistribution Analysis

This module provides functions to load ESS individual-level data and country-level
data from various sources (OECD, ICTWSS, AI exposure indices).
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import pyreadstat

import config


def load_ess_data(
    filepath: Optional[Path] = None,
    countries: Optional[List[str]] = None,
    variables: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Load ESS Round 9 data from Stata file.

    Args:
        filepath: Path to ESS .dta file. If None, uses config.ESS_FILE
        countries: List of country codes to include. If None, uses config.COUNTRIES
        variables: List of variables to select. If None, loads all ESS variables

    Returns:
        DataFrame with ESS individual-level data
    """
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.ESS_FILE

    if countries is None:
        countries = config.COUNTRIES

    # Check if file exists
    if not filepath.exists():
        raise FileNotFoundError(
            f"ESS data file not found: {filepath}\n"
            "Please download ESS9e03_3.dta from https://ess.sitehost.iu.edu/ "
            "and place it in data/raw/"
        )

    logger.info(f"Loading ESS data from: {filepath}")

    # Load Stata file
    try:
        df, meta = pyreadstat.read_dta(str(filepath))
        logger.info(f"Loaded {len(df):,} observations, {len(df.columns)} variables")
    except Exception as e:
        logger.error(f"Error loading ESS file: {e}")
        raise

    # Filter countries
    if config.COUNTRY_VAR not in df.columns:
        raise ValueError(f"Country variable '{config.COUNTRY_VAR}' not found in data")

    df = df[df[config.COUNTRY_VAR].isin(countries)]
    logger.info(f"Filtered to {len(countries)} countries, {len(df):,} observations")

    # Select variables if specified
    if variables is not None:
        # Ensure country variable is included
        if config.COUNTRY_VAR not in variables:
            variables = [config.COUNTRY_VAR] + variables

        missing_vars = set(variables) - set(df.columns)
        if missing_vars:
            logger.warning(f"Variables not found in data: {missing_vars}")
            variables = [v for v in variables if v in df.columns]

        df = df[variables]
        logger.info(f"Selected {len(variables)} variables")

    # Handle missing value codes
    for col in df.select_dtypes(include=["number"]).columns:
        for code_name, code_value in config.MISSING_CODES.items():
            # Replace missing codes with NaN
            df.loc[df[col] == code_value, col] = pd.NA

    logger.info("Replaced ESS missing value codes with NaN")

    return df


def load_country_data(
    gini_path: Optional[Path] = None,
    gdp_path: Optional[Path] = None,
    unemployment_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load and merge basic country-level economic data.

    Args:
        gini_path: Path to Gini coefficient data (CSV). If None, uses config.GINI_FILE
        gdp_path: Path to GDP data (CSV). If None, uses config.GDP_FILE
        unemployment_path: Path to unemployment data (CSV). If None, uses config.UNEMPLOYMENT_FILE

    Returns:
        DataFrame with country-level economic indicators

    Expected CSV format:
        country,year,value
        AT,2018,29.4
        BE,2018,27.2
        ...
    """
    logger = logging.getLogger("ess_analysis")

    if gini_path is None:
        gini_path = config.GINI_FILE
    if gdp_path is None:
        gdp_path = config.GDP_FILE
    if unemployment_path is None:
        unemployment_path = config.UNEMPLOYMENT_FILE

    country_df = None

    # Load Gini data
    if gini_path.exists():
        gini_df = pd.read_csv(gini_path)
        gini_df = gini_df.rename(columns={"value": "gini"})
        # Filter to 2018 if year column exists
        if "year" in gini_df.columns:
            gini_df = gini_df[gini_df["year"] == 2018]
        country_df = gini_df[["country", "gini"]]
        logger.info(f"Loaded Gini data for {len(country_df)} countries")
    else:
        logger.warning(f"Gini data file not found: {gini_path}")

    # Load GDP data
    if gdp_path.exists():
        gdp_df = pd.read_csv(gdp_path)
        gdp_df = gdp_df.rename(columns={"value": "gdp"})
        if "year" in gdp_df.columns:
            gdp_df = gdp_df[gdp_df["year"] == 2018]
        gdp_df = gdp_df[["country", "gdp"]]

        if country_df is not None:
            country_df = country_df.merge(gdp_df, on="country", how="outer")
        else:
            country_df = gdp_df
        logger.info(f"Loaded GDP data for {len(gdp_df)} countries")
    else:
        logger.warning(f"GDP data file not found: {gdp_path}")

    # Load unemployment data
    if unemployment_path.exists():
        unemp_df = pd.read_csv(unemployment_path)
        unemp_df = unemp_df.rename(columns={"value": "unemployment"})
        if "year" in unemp_df.columns:
            unemp_df = unemp_df[unemp_df["year"] == 2018]
        unemp_df = unemp_df[["country", "unemployment"]]

        if country_df is not None:
            country_df = country_df.merge(unemp_df, on="country", how="outer")
        else:
            country_df = unemp_df
        logger.info(f"Loaded unemployment data for {len(unemp_df)} countries")
    else:
        logger.warning(f"Unemployment data file not found: {unemployment_path}")

    if country_df is None:
        logger.error("No country-level data files found!")
        raise FileNotFoundError(
            "Could not find any country-level data files. "
            "Please see data/external/DATA_SOURCES.md for instructions."
        )

    # Ensure country codes match ESS format (uppercase 2-letter codes)
    country_df["country"] = country_df["country"].str.upper()

    logger.info(f"Merged country data: {len(country_df)} countries, {len(country_df.columns)} variables")

    return country_df


def load_institutional_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """
    Load institutional indicators (EPL, ALMP, union density, social spending).

    Args:
        filepath: Path to institutional data CSV. If None, uses config.INSTITUTIONAL_FILE

    Returns:
        DataFrame with institutional indicators by country

    Expected CSV format:
        country,epl,almp_spending,union_density,social_spending,collective_bargaining
        AT,2.4,0.51,26.8,26.9,98.0
        BE,2.5,1.12,50.3,29.0,96.0
        ...
    """
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.INSTITUTIONAL_FILE

    if not filepath.exists():
        logger.warning(
            f"Institutional data file not found: {filepath}\n"
            "Extension analyses (welfare regime, institutional mediation) will be limited. "
            "See data/external/DATA_SOURCES.md for data acquisition instructions."
        )
        # Return empty DataFrame with expected structure
        return pd.DataFrame(columns=[
            "country", "epl", "almp_spending", "union_density",
            "social_spending", "collective_bargaining"
        ])

    inst_df = pd.read_csv(filepath)

    # Ensure country codes are uppercase
    inst_df["country"] = inst_df["country"].str.upper()

    logger.info(f"Loaded institutional data for {len(inst_df)} countries")

    # Report which countries are missing which indicators
    for col in inst_df.columns:
        if col != "country":
            n_missing = inst_df[col].isna().sum()
            if n_missing > 0:
                logger.warning(f"Indicator '{col}' missing for {n_missing} countries")

    return inst_df


def load_ai_exposure_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """
    Load AI/automation exposure indicators.

    Args:
        filepath: Path to AI exposure data CSV. If None, uses config.AI_EXPOSURE_FILE

    Returns:
        DataFrame with AI exposure indicators by country

    Expected CSV format:
        country,ai_exposure_oecd,automation_risk,ai_exposure_felten,social_exposure
        AT,0.45,0.52,0.38,0.22
        BE,0.41,0.49,0.35,0.19
        ...
    """
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.AI_EXPOSURE_FILE

    if not filepath.exists():
        logger.warning(
            f"AI exposure data file not found: {filepath}\n"
            "AI exposure extension analysis will not be possible. "
            "See data/external/DATA_SOURCES.md for data acquisition instructions."
        )
        # Return empty DataFrame with expected structure
        return pd.DataFrame(columns=[
            "country", "ai_exposure_oecd", "automation_risk",
            "ai_exposure_felten", "social_exposure"
        ])

    ai_df = pd.read_csv(filepath)

    # Ensure country codes are uppercase
    ai_df["country"] = ai_df["country"].str.upper()

    logger.info(f"Loaded AI exposure data for {len(ai_df)} countries")

    # Report which countries have which indicators
    for col in ai_df.columns:
        if col != "country":
            n_available = ai_df[col].notna().sum()
            logger.info(f"Indicator '{col}' available for {n_available} countries")

    return ai_df


def merge_country_data(
    ess_df: pd.DataFrame,
    country_df: pd.DataFrame,
    country_var: str = None
) -> pd.DataFrame:
    """
    Merge individual-level ESS data with country-level data.

    Args:
        ess_df: ESS individual-level DataFrame
        country_df: Country-level DataFrame
        country_var: Name of country variable in ess_df. If None, uses config.COUNTRY_VAR

    Returns:
        Merged DataFrame
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    # Check country variable exists
    if country_var not in ess_df.columns:
        raise ValueError(f"Country variable '{country_var}' not found in ESS data")

    if "country" not in country_df.columns:
        raise ValueError("Country variable 'country' not found in country-level data")

    # Merge
    merged_df = ess_df.merge(
        country_df,
        left_on=country_var,
        right_on="country",
        how="left"
    )

    # Check for countries without country-level data
    missing_country_data = merged_df[merged_df["country"].isna()][country_var].unique()
    if len(missing_country_data) > 0:
        logger.warning(
            f"Countries in ESS data without country-level data: {missing_country_data.tolist()}"
        )

    # Report merge statistics
    n_before = len(ess_df)
    n_after = len(merged_df)
    if n_before != n_after:
        logger.warning(f"Merge changed sample size: {n_before} → {n_after}")

    logger.info(f"Merged country-level data: {len(merged_df):,} observations")

    return merged_df


def merge_institutional_data(
    df: pd.DataFrame,
    institutional_df: pd.DataFrame,
    country_var: str = None
) -> pd.DataFrame:
    """
    Merge institutional indicators into main dataset.

    Args:
        df: Main DataFrame (already has ESS + basic country data)
        institutional_df: Institutional indicators DataFrame
        country_var: Name of country variable. If None, uses config.COUNTRY_VAR

    Returns:
        Merged DataFrame
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if len(institutional_df) == 0:
        logger.warning("Institutional data is empty, skipping merge")
        return df

    # Merge
    merged_df = df.merge(
        institutional_df,
        left_on=country_var,
        right_on="country",
        how="left",
        suffixes=("", "_inst")
    )

    # Report which countries have institutional data
    n_with_inst = merged_df["epl"].notna().sum()
    pct_with_inst = n_with_inst / len(merged_df) * 100

    logger.info(
        f"Merged institutional data: {pct_with_inst:.1f}% of observations have EPL data"
    )

    return merged_df


def merge_ai_exposure_data(
    df: pd.DataFrame,
    ai_df: pd.DataFrame,
    country_var: str = None
) -> pd.DataFrame:
    """
    Merge AI/automation exposure indicators into main dataset.

    Args:
        df: Main DataFrame
        ai_df: AI exposure indicators DataFrame
        country_var: Name of country variable. If None, uses config.COUNTRY_VAR

    Returns:
        Merged DataFrame
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if len(ai_df) == 0:
        logger.warning("AI exposure data is empty, skipping merge")
        return df

    # Merge
    merged_df = df.merge(
        ai_df,
        left_on=country_var,
        right_on="country",
        how="left",
        suffixes=("", "_ai")
    )

    # Report which countries have AI exposure data
    if "ai_exposure_oecd" in merged_df.columns:
        n_with_ai = merged_df["ai_exposure_oecd"].notna().sum()
        pct_with_ai = n_with_ai / len(merged_df) * 100

        logger.info(
            f"Merged AI exposure data: {pct_with_ai:.1f}% of observations have OECD AI exposure"
        )

    return merged_df
