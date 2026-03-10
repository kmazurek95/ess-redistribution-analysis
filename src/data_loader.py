"""Load ESS individual-level and country-level data from various sources."""

import logging
from pathlib import Path

import pandas as pd
import pyreadstat

import config


def load_ess_data(filepath=None, countries=None, variables=None):
    """Load ESS Round 9 data from Stata file."""
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.ESS_FILE
    if countries is None:
        countries = config.COUNTRIES

    if not filepath.exists():
        raise FileNotFoundError(
            f"ESS data file not found: {filepath}\n"
            "Please download ESS9e03_3.dta from https://ess.sitehost.iu.edu/ "
            "and place it in data/raw/"
        )

    df, meta = pyreadstat.read_dta(str(filepath))
    logger.info(f"Loaded {len(df):,} observations, {len(df.columns)} variables")

    if config.COUNTRY_VAR not in df.columns:
        raise ValueError(f"Country variable '{config.COUNTRY_VAR}' not found in data")

    df = df[df[config.COUNTRY_VAR].isin(countries)]
    logger.info(f"Filtered to {len(countries)} countries, {len(df):,} observations")

    if variables is not None:
        if config.COUNTRY_VAR not in variables:
            variables = [config.COUNTRY_VAR] + variables

        missing_vars = set(variables) - set(df.columns)
        if missing_vars:
            logger.warning(f"Variables not found in data: {missing_vars}")
            variables = [v for v in variables if v in df.columns]

        df = df[variables]

    for col in df.select_dtypes(include=["number"]).columns:
        for code_name, code_value in config.MISSING_CODES.items():
            df.loc[df[col] == code_value, col] = pd.NA

    return df


def load_country_data(gini_path=None, gdp_path=None, unemployment_path=None):
    """Load and merge country-level economic data (Gini, GDP, unemployment)."""
    logger = logging.getLogger("ess_analysis")

    if gini_path is None:
        gini_path = config.GINI_FILE
    if gdp_path is None:
        gdp_path = config.GDP_FILE
    if unemployment_path is None:
        unemployment_path = config.UNEMPLOYMENT_FILE

    country_df = None

    if gini_path.exists():
        gini_df = pd.read_csv(gini_path)
        gini_df = gini_df.rename(columns={"value": "gini"})
        if "year" in gini_df.columns:
            gini_df = gini_df[gini_df["year"] == 2018]
        country_df = gini_df[["country", "gini"]]
    else:
        logger.warning(f"Gini data file not found: {gini_path}")

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
    else:
        logger.warning(f"GDP data file not found: {gdp_path}")

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
    else:
        logger.warning(f"Unemployment data file not found: {unemployment_path}")

    if country_df is None:
        raise FileNotFoundError(
            "Could not find any country-level data files. "
            "Please see data/external/DATA_SOURCES.md for instructions."
        )

    country_df["country"] = country_df["country"].str.upper()

    return country_df


def load_institutional_data(filepath=None):
    """Load institutional indicators (EPL, ALMP, union density, social spending)."""
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.INSTITUTIONAL_FILE

    if not filepath.exists():
        logger.warning(
            f"Institutional data file not found: {filepath}\n"
            "Extension analyses will be limited. "
            "See data/external/DATA_SOURCES.md for data acquisition instructions."
        )
        return pd.DataFrame(columns=[
            "country", "epl", "almp_spending", "union_density",
            "social_spending", "collective_bargaining"
        ])

    inst_df = pd.read_csv(filepath)
    inst_df["country"] = inst_df["country"].str.upper()

    for col in inst_df.columns:
        if col != "country":
            n_missing = inst_df[col].isna().sum()
            if n_missing > 0:
                logger.warning(f"Indicator '{col}' missing for {n_missing} countries")

    return inst_df


def load_ai_exposure_data(filepath=None):
    """Load AI/automation exposure indicators."""
    logger = logging.getLogger("ess_analysis")

    if filepath is None:
        filepath = config.AI_EXPOSURE_FILE

    if not filepath.exists():
        logger.warning(
            f"AI exposure data file not found: {filepath}\n"
            "AI exposure extension analysis will not be possible. "
            "See data/external/DATA_SOURCES.md for data acquisition instructions."
        )
        return pd.DataFrame(columns=[
            "country", "ai_exposure_oecd", "automation_risk",
            "ai_exposure_felten", "social_exposure"
        ])

    ai_df = pd.read_csv(filepath)
    ai_df["country"] = ai_df["country"].str.upper()

    return ai_df


def merge_country_data(ess_df, country_df, country_var=None):
    """Merge individual-level ESS data with country-level data."""
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if country_var not in ess_df.columns:
        raise ValueError(f"Country variable '{country_var}' not found in ESS data")
    if "country" not in country_df.columns:
        raise ValueError("Country variable 'country' not found in country-level data")

    merged_df = ess_df.merge(
        country_df,
        left_on=country_var,
        right_on="country",
        how="left"
    )

    missing_country_data = merged_df[merged_df["country"].isna()][country_var].unique()
    if len(missing_country_data) > 0:
        logger.warning(
            f"Countries in ESS data without country-level data: {missing_country_data.tolist()}"
        )

    n_before = len(ess_df)
    n_after = len(merged_df)
    if n_before != n_after:
        logger.warning(f"Merge changed sample size: {n_before} -> {n_after}")

    return merged_df


def merge_institutional_data(df, institutional_df, country_var=None):
    """Merge institutional indicators into main dataset."""
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if len(institutional_df) == 0:
        logger.warning("Institutional data is empty, skipping merge")
        return df

    merged_df = df.merge(
        institutional_df,
        left_on=country_var,
        right_on="country",
        how="left",
        suffixes=("", "_inst")
    )

    n_with_inst = merged_df["epl"].notna().sum()
    pct_with_inst = n_with_inst / len(merged_df) * 100
    logger.info(f"Merged institutional data: {pct_with_inst:.1f}% of observations have EPL data")

    return merged_df


def merge_ai_exposure_data(df, ai_df, country_var=None):
    """Merge AI/automation exposure indicators into main dataset."""
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    if len(ai_df) == 0:
        logger.warning("AI exposure data is empty, skipping merge")
        return df

    merged_df = df.merge(
        ai_df,
        left_on=country_var,
        right_on="country",
        how="left",
        suffixes=("", "_ai")
    )

    if "ai_exposure_oecd" in merged_df.columns:
        n_with_ai = merged_df["ai_exposure_oecd"].notna().sum()
        pct_with_ai = n_with_ai / len(merged_df) * 100
        logger.info(f"Merged AI exposure data: {pct_with_ai:.1f}% of observations have OECD AI exposure")

    return merged_df
