# Agent-Based Simulation: Redistribution Attitude Dynamics Under Inequality Shocks

## Design Summary

This simulation models the **indirect channel** from AI-driven labor displacement
to redistribution preference dynamics. The direct effect of AI exposure on
redistribution preferences is null (p = 0.857). Instead, the simulation uses AI
as an exogenous source of inequality increases, which then activate the
empirically estimated income x Gini interaction.

## Empirical Basis

All parameters come from the multilevel regression models in
`outputs/simulation_parameters.json`, estimated from ESS Round 9 (2018) data
(N = 31,393 individuals, 26 countries).

**Key mechanism:** The income x Gini interaction (coef = 0.012, p = 0.002) means
that the relationship between income and redistribution preferences is
*moderated by inequality*. As inequality (Gini) increases:
- The negative income effect weakens (rich people become relatively more
  supportive of redistribution)
- This creates a nonlinearity that can produce tipping dynamics when inequality
  shocks are large enough

**Secondary mechanism:** The ideology x Gini interaction (coef = 0.028, p = 0.024)
means ideological polarization on redistribution also shifts with inequality.

## What Is Being Simulated

1. **Agents** represent individuals with income, ideology, and redistribution
   preferences, initialized from the empirical distributions
2. **Countries** are characterized by their Gini coefficient, random intercept,
   and welfare regime
3. **AI shock** is modeled as an exogenous Gini increase (inequality shock),
   representing the downstream labor market effects of AI adoption
4. **Attitude updating** follows the empirical regression equation, with the
   income x Gini interaction creating nonlinear dynamics as Gini changes

## What The Null AI Direct Effect Means

The simulation does NOT model AI exposure as directly changing attitudes.
Instead:
- AI drives occupational restructuring and wage polarization
- This increases the Gini coefficient
- The Gini increase activates the income x Gini interaction
- Attitudes shift nonlinearly as a result

This is a theory-driven extrapolation, not a confirmed causal chain. The
empirical evidence establishes the income x Gini interaction; the simulation
explores its dynamic implications under inequality shocks.

## Expected Outputs

- **Phase diagrams:** Mapping inequality shock magnitude to attitude equilibria
- **Tipping thresholds:** Gini increase required to shift country from one
  attitude equilibrium to another
- **Regime comparisons:** How tipping thresholds differ across welfare regime
  types (Social Democratic, Conservative, Liberal, Mediterranean, Post-Communist)
- **Trajectory plots:** Country-specific attitude trajectories under varying
  shock magnitudes

## Directory Structure

```
simulation/
├── README.md              # This file
├── config.py              # Loads parameters from simulation_parameters.json
├── model.py               # ABM classes (Country, Agent, Simulation)
├── run_experiments.py     # Experiment runner (parameter sweeps)
└── analysis.py            # Result analysis and visualization
```

## Parameter Source

All simulation parameters are loaded from `../outputs/simulation_parameters.json`.
This file contains:
- Fixed effects (13 coefficients with SEs and p-values)
- Random effects (country intercept variance, ideology slope variance)
- Country-specific parameters (random intercepts, Gini, GDP, AI exposure, regime)
- The income x Gini interaction from Model 5 (the key nonlinearity)
