"""
Simulation Configuration

Loads empirical parameters from the multilevel regression models.
All parameters come from outputs/simulation_parameters.json.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

SIMULATION_DIR = Path(__file__).parent
PROJECT_ROOT = SIMULATION_DIR.parent
PARAMS_FILE = PROJECT_ROOT / "outputs" / "simulation_parameters.json"

# Representative countries (one per welfare regime)
REPRESENTATIVE_COUNTRIES = {
    "Social Democratic": "DK",
    "Conservative/Corporatist": "DE",
    "Liberal": "GB",
    "Mediterranean": "ES",
    "Post-Communist": "PL",
}

# Regime colors for consistent visualization
REGIME_COLORS = {
    "Social Democratic": "#1f77b4",
    "Conservative/Corporatist": "#ff7f0e",
    "Liberal": "#2ca02c",
    "Mediterranean": "#d62728",
    "Post-Communist": "#9467bd",
}


@dataclass
class SimulationConfig:
    """All parameters the simulation model needs."""

    # Fixed effects from Model 7 (final model)
    fixed_effects: Dict[str, float] = field(default_factory=dict)

    # Income x Gini interaction from Model 5 (the key nonlinearity)
    income_gini_interaction: float = 0.0
    income_gini_interaction_se: float = 0.0

    # Random effects
    residual_variance: float = 0.0
    intercept_variance: float = 0.0

    # Country parameters (only countries with valid random intercepts)
    country_params: Dict[str, dict] = field(default_factory=dict)

    # Regime-to-countries mapping
    regime_countries: Dict[str, List[str]] = field(default_factory=dict)

    # Metadata
    n_individuals: int = 0
    n_countries: int = 0

    # Gini z-score parameters (needed to convert raw Gini shocks to z-scores)
    gini_mean: float = 0.0
    gini_sd: float = 0.0


def load_parameters() -> dict:
    """Load raw simulation parameters from the empirical model results."""
    with open(PARAMS_FILE) as f:
        return json.load(f)


def build_config() -> SimulationConfig:
    """Build a SimulationConfig from the parameter file."""
    raw = load_parameters()
    cfg = SimulationConfig()

    # Metadata
    cfg.n_individuals = raw["metadata"]["n_individuals"]
    cfg.n_countries = raw["metadata"]["n_countries"]

    # Fixed effects: extract just the coefficient values
    cfg.fixed_effects = {
        name: vals["coef"] for name, vals in raw["fixed_effects"].items()
    }

    # Income x Gini interaction (from Model 5, extracted separately)
    interaction = raw["income_gini_interaction_model5"]
    cfg.income_gini_interaction = interaction["coef"]
    cfg.income_gini_interaction_se = interaction["se"]

    # Random effects
    re = raw["random_effects"]
    cfg.residual_variance = re["residual_variance"]
    cfg.intercept_variance = re["country_intercept_variance"]

    # Country parameters — exclude countries with null random intercepts.
    # HU and IT excluded: missing Gini/GDP led to listwise deletion in
    # empirical models, so they have no estimated random effects.
    cfg.country_params = {}
    for code, params in raw["country_parameters"].items():
        if params.get("random_intercept") is None:
            continue
        cfg.country_params[code] = params

    # Build regime-to-countries mapping from the included countries
    cfg.regime_countries = {}
    for code, params in cfg.country_params.items():
        regime = params.get("welfare_regime", "Unknown")
        cfg.regime_countries.setdefault(regime, []).append(code)

    # Compute Gini z-score parameters from the included countries
    # (needed to convert raw Gini shocks back to z-scores)
    gini_values = [
        p["gini"] for p in cfg.country_params.values() if p["gini"] is not None
    ]
    if gini_values:
        import numpy as np

        cfg.gini_mean = float(np.mean(gini_values))
        cfg.gini_sd = float(np.std(gini_values, ddof=0))

    return cfg
