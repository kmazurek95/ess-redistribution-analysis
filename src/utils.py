"""Utility functions for logging, data validation, and statistical helpers."""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def get_project_root():
    return Path(__file__).parent.parent.absolute()


def load_config():
    import config
    return config


def setup_logging(log_file=None, level="INFO", format_str=None):
    """Configure logging for the analysis."""
    config = load_config()

    if log_file is None:
        log_file = config.LOG_FILE
    if format_str is None:
        format_str = config.LOG_FORMAT

    logger = logging.getLogger("ess_analysis")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(format_str))
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)

    return logger


def check_missing_data(df, vars=None, threshold=0.5):
    """Report missing data patterns. Warns if any variable exceeds threshold."""
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
            logger.warning(f"Variable '{var}' has {pct_missing:.1%} missing data (threshold: {threshold:.1%})")

    return pd.DataFrame(missing_report)


def calculate_vif(df, vars, threshold=10.0):
    """Calculate Variance Inflation Factors to check for multicollinearity."""
    logger = logging.getLogger("ess_analysis")
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    df_clean = df[vars].dropna()
    if len(df_clean) == 0:
        logger.error("No complete cases available for VIF calculation")
        return pd.DataFrame()

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
            logger.warning(f"Variable '{var}' has high VIF ({vif_value:.2f} > {threshold})")

    return pd.DataFrame(vif_data)


def format_pvalue(p, threshold=0.001):
    if p < threshold:
        return f"<{threshold}"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.2f}"


def create_country_summary(df, country_var, vars):
    """Create summary statistics by country."""
    logger = logging.getLogger("ess_analysis")

    if country_var not in df.columns:
        logger.error(f"Country variable '{country_var}' not found")
        return pd.DataFrame()

    available_vars = [v for v in vars if v in df.columns]
    missing_vars = set(vars) - set(available_vars)
    if missing_vars:
        logger.warning(f"Variables not found: {missing_vars}")

    return df.groupby(country_var)[available_vars].agg(["count", "mean", "std", "min", "max"]).reset_index()


def detect_outliers(series, method="iqr", threshold=3.0):
    """Return boolean Series flagging outliers via IQR or z-score method."""
    if method == "iqr":
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        return (series < Q1 - threshold * IQR) | (series > Q3 + threshold * IQR)
    elif method == "zscore":
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'")


def create_descriptive_table(df, vars, group_var=None, decimals=2):
    if group_var:
        return df.groupby(group_var)[vars].describe().round(decimals)
    return df[vars].describe().round(decimals)


def check_data_quality(df, country_var, min_country_n=100, max_missing_pct=0.5, min_variance=0.01):
    """Run data quality checks: sample sizes, missingness, variance."""
    logger = logging.getLogger("ess_analysis")
    quality_report = {
        "total_n": len(df),
        "n_countries": df[country_var].nunique(),
        "warnings": [],
        "passed": True
    }

    country_counts = df[country_var].value_counts()
    small_countries = country_counts[country_counts < min_country_n]
    if len(small_countries) > 0:
        warning = f"Countries with n < {min_country_n}: {small_countries.to_dict()}"
        quality_report["warnings"].append(warning)
        quality_report["passed"] = False
        logger.warning(warning)

    missing_check = check_missing_data(df, threshold=max_missing_pct)
    high_missing = missing_check[missing_check["above_threshold"]]
    if len(high_missing) > 0:
        warning = f"Variables with >{max_missing_pct:.0%} missing: {high_missing['variable'].tolist()}"
        quality_report["warnings"].append(warning)
        quality_report["passed"] = False
        logger.warning(warning)

    numeric_vars = df.select_dtypes(include=[np.number]).columns
    low_variance_vars = [var for var in numeric_vars if df[var].var() < min_variance]
    if low_variance_vars:
        warning = f"Variables with variance < {min_variance}: {low_variance_vars}"
        quality_report["warnings"].append(warning)
        logger.warning(warning)

    quality_report["low_variance_vars"] = low_variance_vars
    quality_report["small_countries"] = small_countries.to_dict()
    quality_report["high_missing_vars"] = high_missing["variable"].tolist() if len(high_missing) > 0 else []

    return quality_report


def save_results(obj, filename, output_type="table", **kwargs):
    """Save analysis results (DataFrame, figure, or model) to appropriate output directory."""
    config = load_config()

    if output_type == "table":
        output_dir = config.TABLES_DIR
    elif output_type == "figure":
        output_dir = config.FIGURES_DIR
    elif output_type == "model":
        output_dir = config.MODELS_DIR
    else:
        raise ValueError(f"Unknown output_type: {output_type}")

    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename

    if isinstance(obj, pd.DataFrame):
        if filepath.suffix == ".csv":
            obj.to_csv(filepath, **kwargs)
        elif filepath.suffix in [".xlsx", ".xls"]:
            obj.to_excel(filepath, **kwargs)
        elif filepath.suffix == ".parquet":
            obj.to_parquet(filepath, **kwargs)
        else:
            raise ValueError(f"Unsupported file extension for DataFrame: {filepath.suffix}")
    elif hasattr(obj, "savefig"):
        obj.savefig(filepath, **kwargs)
    else:
        import pickle
        with open(filepath, "wb") as f:
            pickle.dump(obj, f)

    return filepath
