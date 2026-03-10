# Simulation: Dual-Domain Attitude Dynamics Under Institutional Stress

This directory contains two agent-based simulations exploring tipping dynamics in political attitudes. The comparison between domains is the central research contribution.

## Simulation 1: Redistribution (inequality shocks)

Models the indirect channel from AI-driven labor displacement to redistribution preferences. The direct effect of AI exposure is null (p = 0.857), so the simulation treats AI as a source of inequality increases that activate the income x Gini interaction (coef = 0.012, p = 0.002).

**Result:** Gradual drift only (~0.022 points per Gini percentage point). No discontinuous tipping at any shock level. The interaction is too small.

Files: `config.py`, `model.py`, `run_experiments.py`, `analysis.py`

## Simulation 2: Trust (corruption/governance shocks)

Models trust erosion under governance quality degradation. The education x corruption interaction (coef = 0.050, p < 0.001) is 4x larger than the redistribution interaction. Includes a feedback loop: aggregate trust erosion degrades governance quality, which further erodes trust.

**Result:** Tipping observed at -15 CPI in all 5 countries (shift > 1.0 point on 0-10 scale). The feedback loop amplifies shocks by ~40%.

Files: `trust_config.py`, `trust_model.py`, `trust_experiments.py`, `trust_analysis.py`

## Why two simulations

The key structural difference is the feedback loop. Redistribution preferences have no self-reinforcing mechanism: wanting more redistribution does not cause less redistribution. Trust does: trust erodes, citizens disengage from institutions, governance quality declines, which erodes trust further. This is why the trust domain tips and redistribution does not, even though both have significant cross-level interactions.

## Parameters

- Redistribution: `../outputs/simulation_parameters.json` (from Models M1-M7)
- Trust: `../outputs/trust_simulation_parameters.json` (from Models T1-T7)

Both use 5 representative countries (DK, DE, GB, ES, PL), 1,000 agents, 50 replications per condition.

## How it works

1. Agents have income, education, ideology drawn from empirical distributions
2. Countries defined by random intercepts, macro-level variables, welfare regime
3. Shocks applied exogenously (Gini increase or CPI decrease)
4. Attitudes update via empirical regression equation + social influence
5. For trust only: feedback loop adjusts corruption z-score based on aggregate trust deficit
