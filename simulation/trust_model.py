"""
Agent-based model for trust dynamics under corruption/governance shocks.

Uses empirical regression coefficients from ESS Round 9 trust models
to simulate how corruption shocks affect institutional trust equilibria.
Includes a feedback loop: aggregate trust erosion degrades governance
quality, which further erodes trust.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

from simulation.trust_config import TrustSimulationConfig, REPRESENTATIVE_COUNTRIES


@dataclass
class TrustSimParams:
    """Runtime parameters for the trust simulation."""
    n_agents: int = 1000
    max_timesteps: int = 500
    convergence_threshold: float = 0.001
    social_influence_strength: float = 0.05
    n_neighbors: int = 15
    majority_threshold: float = 5.0  # midpoint of 0-10 trust scale
    noise_scale: float = 0.1
    feedback_strength: float = 0.02  # trust -> corruption feedback per timestep
    random_seed: Optional[int] = 42


class TrustCountry:
    """
    A country with N agents whose institutional trust evolves
    under the empirical regression model + social influence + feedback.
    """

    def __init__(self, code, country_params, config, sim_params, rng):
        self.code = code
        self.regime = country_params["regime"]
        self.cpi_raw = country_params["cpi_score"]
        self.corruption_z = country_params["corruption_z"]
        self.random_intercept = country_params["random_intercept"]
        self.random_slope_education = country_params.get("random_slope_education", 0.0)

        self.config = config
        self.sim_params = sim_params
        self.rng = rng

        fe = config.fixed_effects
        self.beta_intercept = fe["Intercept"]
        self.beta_income = fe["income_c"]
        self.beta_education = fe["education_c"]
        self.beta_age = fe["age_c"]
        self.beta_female = fe["female"]
        self.beta_employed = fe["employed"]
        self.beta_ideology = fe["ideology_c"]
        self.beta_meritocracy = fe["meritocracy_index_c"]
        self.beta_gini = fe.get("gini_z", 0.0)
        self.beta_gdp = fe.get("gdp_per_capita_z", 0.0)
        self.beta_unemployment = fe.get("unemployment_rate_z", 0.0)
        self.beta_corruption = fe["corruption_z"]
        self.beta_ed_corruption = config.education_corruption_interaction
        self.beta_ed_gini = fe.get("education_c:gini_z", 0.0)

        self.residual_sd = np.sqrt(config.residual_variance)

        # Store initial corruption for feedback tracking
        self.initial_corruption_z = self.corruption_z

        n = sim_params.n_agents
        self._init_agents(n)

    def _init_agents(self, n):
        """Initialize agent attributes from plausible distributions."""
        self.income = self.rng.normal(0.0, 2.5, size=n)
        self.education = self.rng.normal(0.0, 3.5, size=n)
        self.ideology = self.rng.normal(0.0, 2.0, size=n)
        self.age = self.rng.normal(0.0, 17.0, size=n)
        self.female = self.rng.binomial(1, 0.52, size=n).astype(float)
        self.employed = self.rng.binomial(1, 0.55, size=n).astype(float)
        self.meritocracy = self.rng.normal(0.0, 0.8, size=n)

        # Country-level variables (constant for all agents, but stored for clarity)
        self.gini_z = 0.0  # use country's actual value if available
        cp = self.config.country_params.get(self.code, {})
        if cp.get("gini") is not None:
            # Approximate z-score using the redistribution model's Gini distribution
            self.gini_z = (cp["gini"] - 31.0) / 5.0  # rough centering

        self.attitude = self._compute_predicted_attitude()
        self.attitude = np.clip(self.attitude, 0.0, 10.0)

    def _compute_predicted_attitude(self):
        """Predicted trust from the regression equation."""
        pred = (
            self.beta_intercept
            + self.random_intercept
            + self.beta_income * self.income
            + (self.beta_education + self.random_slope_education) * self.education
            + self.beta_age * self.age
            + self.beta_female * self.female
            + self.beta_employed * self.employed
            + self.beta_ideology * self.ideology
            + self.beta_meritocracy * self.meritocracy
            + self.beta_corruption * self.corruption_z
            + self.beta_ed_corruption * (self.education * self.corruption_z)
            + self.beta_gini * self.gini_z
            + self.beta_ed_gini * (self.education * self.gini_z)
        )
        return pred

    def step(self):
        """One timestep: recompute trust from regression + social influence + feedback."""
        n = self.sim_params.n_agents
        sp = self.sim_params

        predicted = self._compute_predicted_attitude()
        noise = self.rng.normal(0.0, self.residual_sd * sp.noise_scale, size=n)
        predicted = predicted + noise

        # Social influence: agents observe neighbors
        neighbor_means = np.empty(n)
        for i in range(n):
            neighbor_idx = self.rng.choice(n, size=sp.n_neighbors, replace=False)
            neighbor_means[i] = self.attitude[neighbor_idx].mean()

        # Shift toward neighbor mean when neighbors are below threshold
        # (distrust is contagious - when neighbors distrust, you distrust more)
        below_threshold = neighbor_means < sp.majority_threshold
        social_shift = np.where(
            below_threshold,
            sp.social_influence_strength * (neighbor_means - predicted),
            0.0,
        )

        self.attitude = predicted + social_shift
        self.attitude = np.clip(self.attitude, 0.0, 10.0)

        # Feedback: aggregate trust erosion degrades governance quality
        # Mean trust below initial level -> corruption gets worse
        mean_trust = float(self.attitude.mean())
        initial_pred = float(self._compute_predicted_attitude().mean())
        trust_deficit = mean_trust - initial_pred
        if trust_deficit < 0:
            # Negative trust deficit -> corruption z decreases (governance worsens)
            self.corruption_z += sp.feedback_strength * trust_deficit

        return mean_trust

    def apply_corruption_shock(self, cpi_decrease, config):
        """Apply a governance degradation shock (cpi_decrease in CPI points)."""
        self.cpi_raw = self.cpi_raw - cpi_decrease
        if config.corruption_sd > 0:
            self.corruption_z = (self.cpi_raw - config.corruption_mean) / config.corruption_sd
        else:
            self.corruption_z = 0.0

        # Simultaneously shift education distribution upward slightly
        # (more educated cohorts entering, modeling AI-era education expansion)
        education_boost = cpi_decrease * 0.05  # 5% of shock magnitude
        n_to_boost = int(0.15 * self.sim_params.n_agents)
        if n_to_boost > 0:
            boost_idx = self.rng.choice(self.sim_params.n_agents, size=n_to_boost, replace=False)
            self.education[boost_idx] += education_boost

    def run_to_convergence(self):
        """Run until convergence or max timesteps."""
        sp = self.sim_params
        trajectory = [float(self.attitude.mean())]

        for t in range(sp.max_timesteps):
            mean_trust = self.step()
            trajectory.append(mean_trust)

            if len(trajectory) >= 2:
                delta = abs(trajectory[-1] - trajectory[-2])
                if delta < sp.convergence_threshold:
                    break

        return trajectory[-1], len(trajectory) - 1, trajectory

    def get_summary(self):
        """Summary statistics of current state."""
        return {
            "mean_trust": float(self.attitude.mean()),
            "sd_trust": float(self.attitude.std()),
            "pct_above_threshold": float(
                (self.attitude >= self.sim_params.majority_threshold).mean() * 100
            ),
            "cpi_raw": self.cpi_raw,
            "corruption_z": self.corruption_z,
            "corruption_z_drift": self.corruption_z - self.initial_corruption_z,
        }


def run_single_trust_experiment(country_code, shock_magnitude, config, sim_params, seed):
    """Run one country + corruption shock experiment."""
    rng = np.random.default_rng(seed)

    sp = TrustSimParams(
        n_agents=sim_params.n_agents,
        max_timesteps=sim_params.max_timesteps,
        convergence_threshold=sim_params.convergence_threshold,
        social_influence_strength=sim_params.social_influence_strength,
        n_neighbors=sim_params.n_neighbors,
        majority_threshold=sim_params.majority_threshold,
        noise_scale=sim_params.noise_scale,
        feedback_strength=sim_params.feedback_strength,
        random_seed=seed,
    )

    country_params = config.country_params[country_code]
    country = TrustCountry(country_code, country_params, config, sp, rng)

    if shock_magnitude > 0:
        country.apply_corruption_shock(shock_magnitude, config)

    final_mean, n_steps, trajectory = country.run_to_convergence()
    summary = country.get_summary()

    return {
        "country": country_code,
        "regime": country.regime,
        "shock": shock_magnitude,
        "seed": seed,
        "final_mean": final_mean,
        "final_sd": summary["sd_trust"],
        "pct_above_threshold": summary["pct_above_threshold"],
        "n_steps": n_steps,
        "cpi_raw": summary["cpi_raw"],
        "corruption_z": summary["corruption_z"],
        "corruption_z_drift": summary["corruption_z_drift"],
    }
