"""
Trust simulation configuration. Loads parameters from
outputs/trust_simulation_parameters.json.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import numpy as np

SIMULATION_DIR = Path(__file__).parent
PROJECT_ROOT = SIMULATION_DIR.parent
PARAMS_FILE = PROJECT_ROOT / "outputs" / "trust_simulation_parameters.json"

REPRESENTATIVE_COUNTRIES = {
    "Social Democratic": "DK",
    "Conservative/Corporatist": "DE",
    "Liberal": "GB",
    "Mediterranean": "ES",
    "Post-Communist": "PL",
}

REGIME_COLORS = {
    "Social Democratic": "#1f77b4",
    "Conservative/Corporatist": "#ff7f0e",
    "Liberal": "#2ca02c",
    "Mediterranean": "#d62728",
    "Post-Communist": "#9467bd",
}


@dataclass
class TrustSimulationConfig:
    """Parameters for the trust simulation."""
    fixed_effects: Dict[str, float] = field(default_factory=dict)
    education_corruption_interaction: float = 0.0
    education_corruption_interaction_se: float = 0.0
    residual_variance: float = 0.0
    intercept_variance: float = 0.0
    country_params: Dict[str, dict] = field(default_factory=dict)
    regime_countries: Dict[str, List[str]] = field(default_factory=dict)
    n_individuals: int = 0
    n_countries: int = 0
    corruption_mean: float = 0.0
    corruption_sd: float = 0.0


def build_trust_config() -> TrustSimulationConfig:
    """Build config from the trust parameter file."""
    with open(PARAMS_FILE) as f:
        raw = json.load(f)

    cfg = TrustSimulationConfig()
    cfg.n_individuals = raw["n_individuals"]
    cfg.n_countries = raw["n_countries"]

    cfg.fixed_effects = {
        name: vals["coef"] for name, vals in raw["fixed_effects"].items()
    }

    interact = raw["education_corruption_interaction"]
    cfg.education_corruption_interaction = interact["coef"]
    cfg.education_corruption_interaction_se = interact["se"]

    re = raw["random_effects"]
    cfg.residual_variance = re["sigma2"]
    cfg.intercept_variance = re["tau"]

    cfg.country_params = {}
    for code, params in raw["country_parameters"].items():
        if params.get("random_intercept") is None:
            continue
        cfg.country_params[code] = params

    cfg.regime_countries = {}
    for code, params in cfg.country_params.items():
        regime = params.get("regime", "Unknown")
        cfg.regime_countries.setdefault(regime, []).append(code)

    cpi_values = [
        p["cpi_score"] for p in cfg.country_params.values()
        if p.get("cpi_score") is not None
    ]
    if cpi_values:
        cfg.corruption_mean = float(np.mean(cpi_values))
        cfg.corruption_sd = float(np.std(cpi_values, ddof=0))

    return cfg
