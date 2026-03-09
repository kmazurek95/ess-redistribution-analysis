"""
Visualization Functions for ESS Redistribution Analysis

This module provides functions for creating publication-quality plots
for multilevel analysis results.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import config

# pymer4 is imported lazily inside functions that need it (plot_random_effects,
# plot_interaction) to avoid hanging on Windows without R configured.


# Set default plotting style
sns.set_style(config.PLOT_SETTINGS["style"])
sns.set_context(config.PLOT_SETTINGS["context"])


def plot_country_means(
    df: pd.DataFrame,
    outcome: str,
    country_var: str = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (12, 8)
) -> plt.Figure:
    """
    Create caterpillar plot of country means with confidence intervals.

    Args:
        df: DataFrame containing data
        outcome: Name of outcome variable
        country_var: Name of country variable. If None, uses config.COUNTRY_VAR
        save_path: Path to save figure. If None, saves to outputs/figures/
        figsize: Figure size (width, height)

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    # Calculate country means and standard errors
    country_stats = df.groupby(country_var)[outcome].agg([
        'mean', 'sem', 'count'
    ]).reset_index()

    # Calculate 95% confidence intervals
    country_stats['ci_lower'] = country_stats['mean'] - 1.96 * country_stats['sem']
    country_stats['ci_upper'] = country_stats['mean'] + 1.96 * country_stats['sem']

    # Sort by mean
    country_stats = country_stats.sort_values('mean')

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot points and error bars
    ax.errorbar(
        x=country_stats['mean'],
        y=range(len(country_stats)),
        xerr=[
            country_stats['mean'] - country_stats['ci_lower'],
            country_stats['ci_upper'] - country_stats['mean']
        ],
        fmt='o',
        capsize=4,
        markersize=6,
        color='steelblue',
        ecolor='gray',
        alpha=0.7
    )

    # Set y-tick labels to country codes
    ax.set_yticks(range(len(country_stats)))
    ax.set_yticklabels(country_stats[country_var])

    # Add vertical line at grand mean
    grand_mean = df[outcome].mean()
    ax.axvline(grand_mean, color='red', linestyle='--', alpha=0.5, label='Grand mean')

    # Labels and title
    ax.set_xlabel(f'{outcome} (Mean ± 95% CI)', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    ax.set_title('Country Means of Redistribution Support', fontsize=14, fontweight='bold')
    ax.legend()

    plt.tight_layout()

    # Save figure
    if save_path is None:
        save_path = config.FIGURES_DIR / 'country_means.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved caterpillar plot to: {save_path}")

    return fig


def plot_distribution_by_country(
    df: pd.DataFrame,
    outcome: str,
    country_var: str = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (16, 12)
) -> plt.Figure:
    """
    Create small multiples histograms showing outcome distribution by country.

    Args:
        df: DataFrame containing data
        outcome: Name of outcome variable
        country_var: Name of country variable
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    # Get list of countries
    countries = sorted(df[country_var].unique())
    n_countries = len(countries)

    # Calculate grid dimensions
    n_cols = 7
    n_rows = int(np.ceil(n_countries / n_cols))

    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, sharex=True, sharey=True)
    axes = axes.flatten()

    # Plot histogram for each country
    for i, country in enumerate(countries):
        ax = axes[i]
        country_data = df[df[country_var] == country][outcome]

        ax.hist(country_data, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_title(f'{country} (n={len(country_data)})', fontsize=10)
        ax.axvline(country_data.mean(), color='red', linestyle='--', linewidth=1)

    # Hide unused subplots
    for i in range(n_countries, len(axes)):
        axes[i].axis('off')

    # Add common labels
    fig.text(0.5, 0.04, outcome, ha='center', fontsize=12)
    fig.text(0.04, 0.5, 'Frequency', va='center', rotation='vertical', fontsize=12)
    fig.suptitle(f'Distribution of {outcome} by Country', fontsize=14, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0.05, 0.05, 1, 0.97])

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / 'distribution_by_country.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved distribution plot to: {save_path}")

    return fig


def plot_random_effects(
    model,
    effect_type: str = "intercept",
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Visualize random intercepts or random slopes from fitted model.

    Args:
        model: Fitted pymer4 Lmer model
        effect_type: Type of random effect ('intercept' or 'slope')
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    # Extract random effects
    ranef = model.ranef

    # Determine which column to plot
    if effect_type == "intercept":
        col_name = "Intercept"
    else:
        # For slopes, use the first non-intercept column
        col_name = [c for c in ranef.columns if c != "Intercept"][0]

    # Sort by effect size
    ranef_sorted = ranef.sort_values(col_name)

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot as horizontal bars
    ax.barh(range(len(ranef_sorted)), ranef_sorted[col_name], color='steelblue', alpha=0.7)

    # Set y-tick labels to group names (countries)
    ax.set_yticks(range(len(ranef_sorted)))
    ax.set_yticklabels(ranef_sorted.index)

    # Add vertical line at zero
    ax.axvline(0, color='red', linestyle='--', alpha=0.5)

    # Labels
    ax.set_xlabel(f'Random {effect_type.capitalize()}', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    ax.set_title(f'Random {effect_type.capitalize()}s by Country', fontsize=14, fontweight='bold')

    plt.tight_layout()

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / f'random_{effect_type}s.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved random effects plot to: {save_path}")

    return fig


def plot_interaction(
    model,
    var1: str,
    var2: str,
    df: pd.DataFrame,
    moderator_values: List[float] = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Create margins plot for cross-level interaction.

    Args:
        model: Fitted model with interaction term
        var1: First variable (Level-1, e.g., income)
        var2: Second variable (Level-2, e.g., Gini)
        df: DataFrame used to fit model
        moderator_values: Values of var2 to plot. If None, uses [-1SD, Mean, +1SD]
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    if moderator_values is None:
        # Use -1SD, mean, +1SD of moderator
        mean_var2 = df[var2].mean()
        std_var2 = df[var2].std()
        moderator_values = [
            mean_var2 - std_var2,
            mean_var2,
            mean_var2 + std_var2
        ]
        moderator_labels = ['-1 SD', 'Mean', '+1 SD']
    else:
        moderator_labels = [f'{v:.2f}' for v in moderator_values]

    # Extract coefficients from model
    coefs = model.coefs
    intercept = coefs[coefs['Predictor'] == 'Intercept']['Estimate'].values[0]
    b_var1 = coefs[coefs['Predictor'] == var1]['Estimate'].values[0]
    b_var2 = coefs[coefs['Predictor'] == var2]['Estimate'].values[0]

    # Get interaction term coefficient
    interaction_term = f"{var1}:{var2}"
    if interaction_term in coefs['Predictor'].values:
        b_interaction = coefs[coefs['Predictor'] == interaction_term]['Estimate'].values[0]
    else:
        logger.warning(f"Interaction term '{interaction_term}' not found in model")
        return None

    # Create range of var1 values
    var1_range = np.linspace(df[var1].min(), df[var1].max(), 100)

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot lines for each moderator value
    colors = ['blue', 'green', 'red']
    for i, (mod_val, mod_label) in enumerate(zip(moderator_values, moderator_labels)):
        # Predicted values: y = intercept + b1*var1 + b2*var2 + b3*var1*var2
        y_pred = intercept + b_var1 * var1_range + b_var2 * mod_val + b_interaction * var1_range * mod_val

        ax.plot(var1_range, y_pred, label=f'{var2} = {mod_label}', color=colors[i], linewidth=2)

    # Labels
    ax.set_xlabel(var1, fontsize=12)
    ax.set_ylabel('Predicted Redistribution Support', fontsize=12)
    ax.set_title(f'Interaction: {var1} × {var2}', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / f'interaction_{var1}_{var2}.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved interaction plot to: {save_path}")

    return fig


def create_regression_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    group_var: str = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Create spaghetti plot with country-specific regression lines.

    Args:
        df: DataFrame containing data
        x: X-axis variable
        y: Y-axis variable
        group_var: Grouping variable (country)
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    if group_var is None:
        group_var = config.COUNTRY_VAR

    fig, ax = plt.subplots(figsize=figsize)

    # Plot regression line for each country
    for country in df[group_var].unique():
        country_data = df[df[group_var] == country]

        # Fit simple linear regression
        coeffs = np.polyfit(country_data[x].dropna(), country_data[y].dropna(), 1)
        poly_func = np.poly1d(coeffs)

        # Plot line
        x_range = np.linspace(country_data[x].min(), country_data[x].max(), 100)
        ax.plot(x_range, poly_func(x_range), alpha=0.5, linewidth=1)

    # Add overall regression line
    overall_coeffs = np.polyfit(df[x].dropna(), df[y].dropna(), 1)
    overall_func = np.poly1d(overall_coeffs)
    x_range_overall = np.linspace(df[x].min(), df[x].max(), 100)
    ax.plot(x_range_overall, overall_func(x_range_overall),
            color='red', linewidth=3, label='Overall', linestyle='--')

    # Labels
    ax.set_xlabel(x, fontsize=12)
    ax.set_ylabel(y, fontsize=12)
    ax.set_title(f'{y} vs {x} by Country', fontsize=14, fontweight='bold')
    ax.legend()

    plt.tight_layout()

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / f'regression_{x}_{y}.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved regression plot to: {save_path}")

    return fig


def plot_by_regime(
    df: pd.DataFrame,
    outcome: str,
    regime_var: str = "welfare_regime",
    plot_type: str = "violin",
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Create box/violin plots of outcome by welfare regime.

    Args:
        df: DataFrame containing data
        outcome: Name of outcome variable
        regime_var: Name of regime classification variable
        plot_type: Type of plot ('box' or 'violin')
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    fig, ax = plt.subplots(figsize=figsize)

    # Filter out missing regime values
    plot_data = df[df[regime_var].notna()]

    if plot_type == "violin":
        sns.violinplot(data=plot_data, x=regime_var, y=outcome, palette=config.REGIME_COLORS, ax=ax)
    elif plot_type == "box":
        sns.boxplot(data=plot_data, x=regime_var, y=outcome, palette=config.REGIME_COLORS, ax=ax)
    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")

    # Rotate x-axis labels for readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    # Labels
    ax.set_xlabel('Welfare Regime', fontsize=12)
    ax.set_ylabel(outcome, fontsize=12)
    ax.set_title(f'{outcome} by Welfare Regime', fontsize=14, fontweight='bold')

    plt.tight_layout()

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / f'{outcome}_by_regime.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved regime comparison plot to: {save_path}")

    return fig


def plot_institutional_scatter(
    df: pd.DataFrame,
    institutional_var: str,
    outcome_var: str,
    regime_var: str = "welfare_regime",
    country_var: str = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Create country-level scatter plot of institutional indicator vs outcome,
    colored by welfare regime.

    Args:
        df: DataFrame containing data
        institutional_var: Name of institutional variable (e.g., 'epl', 'almp_spending')
        outcome_var: Name of outcome variable (country mean)
        regime_var: Name of regime classification variable
        country_var: Name of country variable
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    # Aggregate to country level
    country_data = df.groupby(country_var).agg({
        institutional_var: 'first',
        outcome_var: 'mean',
        regime_var: 'first'
    }).reset_index()

    # Remove missing data
    country_data = country_data.dropna(subset=[institutional_var, outcome_var, regime_var])

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot points colored by regime
    for regime in country_data[regime_var].unique():
        regime_data = country_data[country_data[regime_var] == regime]
        color = config.REGIME_COLORS.get(regime, 'gray')

        ax.scatter(
            regime_data[institutional_var],
            regime_data[outcome_var],
            label=regime,
            color=color,
            s=100,
            alpha=0.7,
            edgecolors='black'
        )

        # Add country labels
        for _, row in regime_data.iterrows():
            ax.annotate(
                row[country_var],
                (row[institutional_var], row[outcome_var]),
                fontsize=8,
                alpha=0.7,
                xytext=(3, 3),
                textcoords='offset points'
            )

    # Add regression line
    coeffs = np.polyfit(country_data[institutional_var], country_data[outcome_var], 1)
    poly_func = np.poly1d(coeffs)
    x_range = np.linspace(country_data[institutional_var].min(), country_data[institutional_var].max(), 100)
    ax.plot(x_range, poly_func(x_range), color='black', linestyle='--', alpha=0.5)

    # Labels
    ax.set_xlabel(institutional_var, fontsize=12)
    ax.set_ylabel(f'{outcome_var} (Country Mean)', fontsize=12)
    ax.set_title(f'{institutional_var} vs {outcome_var} by Regime', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / f'{institutional_var}_vs_{outcome_var}_by_regime.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved institutional scatter plot to: {save_path}")

    return fig


def plot_ai_exposure_by_regime(
    df: pd.DataFrame,
    ai_var: str,
    outcome_var: str,
    regime_var: str = "welfare_regime",
    country_var: str = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Visualize AI exposure × regime patterns.

    Args:
        df: DataFrame containing data
        ai_var: Name of AI exposure variable
        outcome_var: Name of outcome variable
        regime_var: Name of regime classification variable
        country_var: Name of country variable
        save_path: Path to save figure
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    logger = logging.getLogger("ess_analysis")

    if country_var is None:
        country_var = config.COUNTRY_VAR

    # Aggregate to country level
    country_data = df.groupby(country_var).agg({
        ai_var: 'first',
        outcome_var: 'mean',
        regime_var: 'first'
    }).reset_index()

    # Remove missing data
    country_data = country_data.dropna(subset=[ai_var, outcome_var, regime_var])

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Left plot: Scatter by regime
    for regime in country_data[regime_var].unique():
        regime_data = country_data[country_data[regime_var] == regime]
        color = config.REGIME_COLORS.get(regime, 'gray')

        ax1.scatter(
            regime_data[ai_var],
            regime_data[outcome_var],
            label=regime,
            color=color,
            s=100,
            alpha=0.7,
            edgecolors='black'
        )

    ax1.set_xlabel(ai_var, fontsize=11)
    ax1.set_ylabel(f'{outcome_var} (Mean)', fontsize=11)
    ax1.set_title('AI Exposure vs Redistribution Support', fontsize=12)
    ax1.legend()

    # Right plot: Boxplot of AI exposure by regime
    sns.boxplot(data=country_data, x=regime_var, y=ai_var, palette=config.REGIME_COLORS, ax=ax2)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_xlabel('Welfare Regime', fontsize=11)
    ax2.set_ylabel(ai_var, fontsize=11)
    ax2.set_title('AI Exposure by Regime', fontsize=12)

    plt.tight_layout()

    # Save
    if save_path is None:
        save_path = config.FIGURES_DIR / f'{ai_var}_by_regime.png'

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=config.PLOT_SETTINGS["dpi"], bbox_inches='tight')
    logger.info(f"Saved AI exposure plot to: {save_path}")

    return fig
