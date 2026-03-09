"""
Agent-Based Model: Redistribution Attitude Dynamics Under Inequality Shocks

Uses empirical regression coefficients from ESS Round 9 multilevel models
to simulate how exogenous Gini shocks affect redistribution attitude equilibria
across welfare regime types.

Pure numpy implementation (no Mesa dependency).
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple

from simulation.config import SimulationConfig, REPRESENTATIVE_COUNTRIES


@dataclass
class SimulationParams:
    """Runtime parameters for the simulation."""

    n_agents: int = 1000
    max_timesteps: int = 500
    convergence_threshold: float = 0.001
    social_influence_strength: float = 0.05
    n_neighbors: int = 15
    majority_threshold: float = 3.5
    noise_scale: float = 0.1  # fraction of residual SD used as perturbation
    random_seed: Optional[int] = 42


class Country:
    """
    A country with N agents whose redistribution attitudes evolve
    under the empirical regression model + social influence.
    """

    def __init__(
        self,
        code: str,
        country_params: dict,
        config: SimulationConfig,
        sim_params: SimulationParams,
        rng: np.random.Generator,
    ):
        self.code = code
        self.regime = country_params["welfare_regime"]
        self.gini_raw = country_params["gini"]
        self.gini_z = country_params["gini_z_value"]
        self.random_intercept = country_params["random_intercept"]
        self.random_slope_ideology = country_params.get("random_slope_ideology", 0.0)

        self.config = config
        self.sim_params = sim_params
        self.rng = rng

        # Fixed effects shorthand
        fe = config.fixed_effects
        self.beta_intercept = fe["Intercept"]
        self.beta_income = fe["income_c"]
        self.beta_ideology = fe["ideology_c"]
        self.beta_gini = fe["gini_z"]
        self.beta_income_gini = config.income_gini_interaction
        self.beta_ideology_gini = fe.get("ideology_c:gini_z", 0.0)
        self.beta_education = fe["education_c"]
        self.beta_age = fe["age_c"]
        self.beta_female = fe["female"]
        self.beta_employed = fe["employed"]
        self.beta_trust = fe["political_trust_c"]
        self.beta_meritocracy = fe["meritocracy_index_c"]

        self.residual_sd = np.sqrt(config.residual_variance)

        # Initialize agents
        n = sim_params.n_agents
        self._init_agents(n)

    def _init_agents(self, n: int):
        """Initialize agent attribute arrays from plausible distributions."""
        # Income: centered (mean 0), spread scaled by Gini.
        # Higher Gini -> wider income spread. SD ~ 2.5 for average Gini,
        # scaled by (1 + 0.3 * gini_z) to reflect inequality.
        income_sd = 2.5 * (1.0 + 0.3 * self.gini_z)
        self.income = self.rng.normal(0.0, max(income_sd, 0.5), size=n)

        # Ideology: centered, SD ~ 2.0 (ESS lrscale 0-10, centered ~ SD 2)
        self.ideology = self.rng.normal(0.0, 2.0, size=n)

        # Demographics (centered): education, age, trust, meritocracy
        self.education = self.rng.normal(0.0, 3.5, size=n)
        self.age = self.rng.normal(0.0, 17.0, size=n)
        self.female = self.rng.binomial(1, 0.52, size=n).astype(float)
        self.employed = self.rng.binomial(1, 0.55, size=n).astype(float)
        self.trust = self.rng.normal(0.0, 2.5, size=n)
        self.meritocracy = self.rng.normal(0.0, 0.8, size=n)

        # Initialize attitudes from the empirical model prediction
        self.attitude = self._compute_predicted_attitude()
        self.attitude = np.clip(self.attitude, 1.0, 5.0)

    def _compute_predicted_attitude(self) -> np.ndarray:
        """Compute predicted attitude from the regression equation."""
        pred = (
            self.beta_intercept
            + self.random_intercept
            + self.beta_income * self.income
            + self.beta_ideology * self.ideology
            + self.beta_gini * self.gini_z
            + self.beta_income_gini * (self.income * self.gini_z)
            + self.beta_ideology_gini * (self.ideology * self.gini_z)
            + self.beta_education * self.education
            + self.beta_age * self.age
            + self.beta_female * self.female
            + self.beta_employed * self.employed
            + self.beta_trust * self.trust
            + self.beta_meritocracy * self.meritocracy
        )
        return pred

    def step(self) -> float:
        """
        One simulation timestep: recompute attitudes from regression model
        with current Gini, then apply social influence.

        Returns the mean attitude after this step.
        """
        n = self.sim_params.n_agents
        sp = self.sim_params

        # 1. Predicted attitude from regression model (with current Gini)
        predicted = self._compute_predicted_attitude()

        # Add small stochastic perturbation
        noise = self.rng.normal(0.0, self.residual_sd * sp.noise_scale, size=n)
        predicted = predicted + noise

        # 2. Social influence (Granovetter threshold logic)
        # Each agent observes K random neighbors
        neighbor_means = np.empty(n)
        for i in range(n):
            neighbor_idx = self.rng.choice(n, size=sp.n_neighbors, replace=False)
            neighbor_means[i] = self.attitude[neighbor_idx].mean()

        # Agents whose neighbors exceed the majority threshold shift toward
        # the neighbor mean; otherwise no social influence shift
        above_threshold = neighbor_means >= sp.majority_threshold
        social_shift = np.where(
            above_threshold,
            sp.social_influence_strength * (neighbor_means - predicted),
            0.0,
        )

        # 3. Update attitudes
        self.attitude = predicted + social_shift
        self.attitude = np.clip(self.attitude, 1.0, 5.0)

        return float(self.attitude.mean())

    def apply_gini_shock(self, raw_shock: float, config: SimulationConfig):
        """
        Apply an exogenous Gini increase.

        Args:
            raw_shock: increase in raw Gini points (e.g., 0.05 = 5pp)
            config: SimulationConfig with gini_mean/gini_sd for z-scoring
        """
        # Update raw Gini
        self.gini_raw = self.gini_raw + raw_shock

        # Recompute z-score using original distribution parameters
        if config.gini_sd > 0:
            self.gini_z = (self.gini_raw - config.gini_mean) / config.gini_sd
        else:
            self.gini_z = 0.0

        # Wage polarization: shift 20% of middle-income agents downward.
        # Middle = 25th to 75th percentile of income distribution.
        p25 = np.percentile(self.income, 25)
        p75 = np.percentile(self.income, 75)
        middle_mask = (self.income >= p25) & (self.income <= p75)

        # Randomly select 20% of middle-income agents
        middle_indices = np.where(middle_mask)[0]
        n_to_shift = int(0.2 * len(middle_indices))
        if n_to_shift > 0:
            shift_indices = self.rng.choice(
                middle_indices, size=n_to_shift, replace=False
            )
            income_sd = max(np.std(self.income), 0.5)
            self.income[shift_indices] -= 0.5 * income_sd

    def run_to_convergence(self) -> Tuple[float, int, list]:
        """
        Run simulation until convergence or max timesteps.

        Returns:
            (final_mean_attitude, n_steps, trajectory)
        """
        sp = self.sim_params
        trajectory = [float(self.attitude.mean())]

        for t in range(sp.max_timesteps):
            mean_att = self.step()
            trajectory.append(mean_att)

            # Check convergence
            if len(trajectory) >= 2:
                delta = abs(trajectory[-1] - trajectory[-2])
                if delta < sp.convergence_threshold:
                    break

        return trajectory[-1], len(trajectory) - 1, trajectory

    def get_summary(self) -> dict:
        """Return summary statistics of current state."""
        return {
            "mean_attitude": float(self.attitude.mean()),
            "sd_attitude": float(self.attitude.std()),
            "pct_above_threshold": float(
                (self.attitude >= self.sim_params.majority_threshold).mean() * 100
            ),
            "gini_raw": self.gini_raw,
            "gini_z": self.gini_z,
        }


def run_single_experiment(
    country_code: str,
    shock_magnitude: float,
    config: SimulationConfig,
    sim_params: SimulationParams,
    seed: int,
) -> dict:
    """
    Run a single country + shock experiment.

    Args:
        country_code: ISO2 country code
        shock_magnitude: raw Gini increase (0 = baseline)
        config: SimulationConfig
        sim_params: SimulationParams
        seed: random seed for this run

    Returns:
        dict with results
    """
    rng = np.random.default_rng(seed)

    # Create a fresh SimulationParams with the specific seed
    sp = SimulationParams(
        n_agents=sim_params.n_agents,
        max_timesteps=sim_params.max_timesteps,
        convergence_threshold=sim_params.convergence_threshold,
        social_influence_strength=sim_params.social_influence_strength,
        n_neighbors=sim_params.n_neighbors,
        majority_threshold=sim_params.majority_threshold,
        noise_scale=sim_params.noise_scale,
        random_seed=seed,
    )

    country_params = config.country_params[country_code]
    country = Country(country_code, country_params, config, sp, rng)

    # Apply shock if nonzero
    if shock_magnitude > 0:
        country.apply_gini_shock(shock_magnitude, config)

    # Run to convergence
    final_mean, n_steps, trajectory = country.run_to_convergence()
    summary = country.get_summary()

    return {
        "country": country_code,
        "regime": country.regime,
        "shock": shock_magnitude,
        "seed": seed,
        "final_mean": final_mean,
        "final_sd": summary["sd_attitude"],
        "pct_above_threshold": summary["pct_above_threshold"],
        "n_steps": n_steps,
        "gini_raw": summary["gini_raw"],
        "gini_z": summary["gini_z"],
    }
