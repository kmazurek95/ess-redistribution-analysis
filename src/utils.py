"""
Utility Functions for ESS Redistribution Analysis

This module provides helper functions for logging, configuration, data validation,
and statistical calculations.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path: Path object pointing to project root
    """
    # Navigate up from src/ to project root
    return Path(__file__).parent.parent.absolute()


def load_config():
    """
    Load configuration settings from config.py.

    Returns:
        module: config module with all settings
    """
    import config
    return config


def setup_logging(
    log_file: Optional[Path] = None,
    level: str = "INFO",
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the analysis.

    Args:
        log_file: Path to log file. If None, uses config.LOG_FILE
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Custom format string. If None, uses config.LOG_FORMAT

    Returns:
        Logger: Configured logger instance
    """
    config = load_config()

    if log_file is None:
        log_file = config.LOG_FILE

    if format_str is None:
        format_str = config.LOG_FORMAT

    # Create logger
    logger = logging.getLogger("ess_analysis")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(format_str)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(format_str)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def check_missing_data(
    df: pd.DataFrame,
    vars: Optional[List[str]] = None,
    threshold: float = 0.5
) -> pd.DataFrame:
    """
    Report missing data patterns.

    Args:
        df: DataFrame to check
        vars: List of variables to check. If None, checks all columns
        threshold: Warn if missing percentage exceeds this threshold

    Returns:
        DataFrame with columns: variable, n_missing, pct_missing, above_threshold
    """
    logger = logging.getLogger("ess_analysis")

    if vars is None:
        vars = df.columns.tolist()

    missing_report = []

    for var in vars:
        if var not in df.columns:
            logger.warning(f"Variable '{var}' not found in DataFrame")
            continue

        n_missing = df[var].isna().sum()
        pct_missing = n_missing / len(df)
        above_threshold = pct_missing > threshold

        missing_report.append({
            "variable": var,
            "n_missing": n_missing,
            "pct_missing": pct_missing,
            "above_threshold": above_threshold
        })

        if above_threshold:
            logger.warning(
                f"Variable '{var}' has {pct_missing:.1%} missing data "
                f"(threshold: {threshold:.1%})"
            )

    return pd.DataFrame(missing_report)


def calculate_vif(
    df: pd.DataFrame,
    vars: List[str],
    threshold: float = 10.0
) -> pd.DataFrame:
    """
    Calculate Variance Inflation Factors to check for multicollinearity.

    Args:
        df: DataFrame containing variables
        vars: List of variable names to include in VIF calculation
        threshold: VIF threshold for flagging high collinearity (default: 10)

    Returns:
        DataFrame with columns: variable, VIF, high_collinearity
    """
    logger = logging.getLogger("ess_analysis")

    from statsmodels.stats.outliers_influence import variance_inflation_factor

    # Remove missing data
    df_clean = df[vars].dropna()

    if len(df_clean) == 0:
        logger.error("No complete cases available for VIF calculation")
        return pd.DataFrame()

    # Calculate VIF for each variable
    vif_data = []
    for i, var in enumerate(vars):
        vif_value = variance_inflation_factor(df_clean.values, i)
        high_collinearity = vif_value > threshold

        vif_data.append({
            "variable": var,
            "VIF": vif_value,
            "high_collinearity": high_collinearity
        })

        if high_collinearity:
            logger.warning(
                f"Variable '{var}' has high VIF ({vif_value:.2f} > {threshold})"
            )

    return pd.DataFrame(vif_data)


def format_pvalue(p: float, threshold: float = 0.001) -> str:
    """
    Format p-values for publication tables.

    Args:
        p: P-value to format
        threshold: Threshold below which to use '<' notation

    Returns:
        Formatted p-value string
    """
    if p < threshold:
        return f"<{threshold}"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.2f}"


def create_country_summary(
    df: pd.DataFrame,
    country_var: str,
    vars: List[str]
) -> pd.DataFrame:
    """
    Create summary statistics by country for typology construction.

    Args:
        df: DataFrame containing data
        country_var: Name of country identifier variable
        vars: List of variables to summarize

    Returns:
        DataFrame with country-level summary statistics
    """
    logger = logging.getLogger("ess_analysis")

    if country_var not in df.columns:
        logger.error(f"Country variable '{country_var}' not found")
        return pd.DataFrame()

    # Check which vars exist
    available_vars = [v for v in vars if v in df.columns]
    missing_vars = set(vars) - set(available_vars)

    if missing_vars:
        logger.warning(f"Variables not found: {missing_vars}")

    # Calculate summary statistics by country
    summary_stats = df.groupby(country_var)[available_vars].agg([
        "count", "mean", "std", "min", "max"
    ]).reset_index()

    return summary_stats


def detect_outliers(
    series: pd.Series,
    method: str = "iqr",
    threshold: float = 3.0
) -> pd.Series:
    """
    Detect outliers in a continuous variable.

    Args:
        series: Pandas Series to check
        method: Method for outlier detection ('iqr' or 'zscore')
        threshold: Threshold for flagging outliers
            - For IQR: multiplier of IQR (default 3.0)
            - For z-score: number of standard deviations (default 3.0)

    Returns:
        Boolean Series indicating outliers (True = outlier)
    """
    if method == "iqr":
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)

    elif method == "zscore":
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold

    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'")


def create_descriptive_table(
    df: pd.DataFrame,
    vars: List[str],
    group_var: Optional[str] = None,
    decimals: int = 2
) -> pd.DataFrame:
    """
    Create a descriptive statistics table.

    Args:
        df: DataFrame containing data
        vars: List of variables to summarize
        group_var: Optional grouping variable (e.g., country, regime)
        decimals: Number of decimal places for rounding

    Returns:
        DataFrame with descriptive statistics
    """
    if group_var:
        desc = df.groupby(group_var)[vars].describe().round(decimals)
    else:
        desc = df[vars].describe().round(decimals)

    return desc


def check_data_quality(
    df: pd.DataFrame,
    country_var: str,
    min_country_n: int = 100,
    max_missing_pct: float = 0.5,
    min_variance: float = 0.01
) -> Dict[str, any]:
    """
    Comprehensive data quality check.

    Args:
        df: DataFrame to check
        country_var: Name of country identifier variable
        min_country_n: Minimum required sample size per country
        max_missing_pct: Maximum allowable missing percentage
        min_variance: Minimum required variance for continuous variables

    Returns:
        Dictionary with quality check results and warnings
    """
    logger = logging.getLogger("ess_analysis")
    quality_report = {
        "total_n": len(df),
        "n_countries": df[country_var].nunique(),
        "warnings": [],
        "passed": True
    }

    # Check country sample sizes
    country_counts = df[country_var].value_counts()
    small_countries = country_counts[country_counts < min_country_n]

    if len(small_countries) > 0:
        warning = f"Countries with n < {min_country_n}: {small_countries.to_dict()}"
        quality_report["warnings"].append(warning)
        quality_report["passed"] = False
        logger.warning(warning)

    # Check missing data
    missing_check = check_missing_data(df, threshold=max_missing_pct)
    high_missing = missing_check[missing_check["above_threshold"]]

    if len(high_missing) > 0:
        warning = f"Variables with >{max_missing_pct:.0%} missing: {high_missing['variable'].tolist()}"
        quality_report["warnings"].append(warning)
        quality_report["passed"] = False
        logger.warning(warning)

    # Check variance for continuous variables
    numeric_vars = df.select_dtypes(include=[np.number]).columns
    low_variance_vars = []

    for var in numeric_vars:
        if df[var].var() < min_variance:
            low_variance_vars.append(var)

    if low_variance_vars:
        warning = f"Variables with variance < {min_variance}: {low_variance_vars}"
        quality_report["warnings"].append(warning)
        logger.warning(warning)

    quality_report["low_variance_vars"] = low_variance_vars
    quality_report["small_countries"] = small_countries.to_dict()
    quality_report["high_missing_vars"] = high_missing["variable"].tolist() if len(high_missing) > 0 else []

    if quality_report["passed"]:
        logger.info("All data quality checks passed ✓")
    else:
        logger.warning(f"Data quality issues detected: {len(quality_report['warnings'])} warnings")

    return quality_report


def save_results(
    obj: any,
    filename: str,
    output_type: str = "table",
    **kwargs
) -> Path:
    """
    Save analysis results to appropriate output directory.

    Args:
        obj: Object to save (DataFrame, Figure, or model object)
        filename: Filename (without directory path)
        output_type: Type of output ('table', 'figure', or 'model')
        **kwargs: Additional arguments passed to save function

    Returns:
        Path to saved file
    """
    config = load_config()
    logger = logging.getLogger("ess_analysis")

    # Determine output directory
    if output_type == "table":
        output_dir = config.TABLES_DIR
    elif output_type == "figure":
        output_dir = config.FIGURES_DIR
    elif output_type == "model":
        output_dir = config.MODELS_DIR
    else:
        raise ValueError(f"Unknown output_type: {output_type}")

    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full path
    filepath = output_dir / filename

    # Save based on object type
    if isinstance(obj, pd.DataFrame):
        if filepath.suffix == ".csv":
            obj.to_csv(filepath, **kwargs)
        elif filepath.suffix in [".xlsx", ".xls"]:
            obj.to_excel(filepath, **kwargs)
        elif filepath.suffix == ".parquet":
            obj.to_parquet(filepath, **kwargs)
        else:
            raise ValueError(f"Unsupported file extension for DataFrame: {filepath.suffix}")

    elif hasattr(obj, "savefig"):  # Matplotlib figure
        obj.savefig(filepath, **kwargs)

    else:  # Assume picklable object (e.g., model)
        import pickle
        with open(filepath, "wb") as f:
            pickle.dump(obj, f)

    logger.info(f"Saved {output_type} to: {filepath}")
    return filepath
