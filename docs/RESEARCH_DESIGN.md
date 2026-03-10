# Research Design

Multilevel analysis of redistribution preferences and institutional trust across 28 European countries, with agent-based simulation of tipping dynamics under institutional stress.

---

## Research Questions

**RQ1:** To what extent do individual characteristics and country-level economic conditions explain between-country variation in redistribution preferences?

**RQ2:** Does country-level AI/automation exposure independently shape redistribution preferences, or does it operate indirectly through inequality?

**RQ3:** Which attitudinal domain -- redistribution preferences or institutional trust -- is more structurally vulnerable to tipping under exogenous shocks, and why?

## Analytical Strategy

The project proceeds in five stages, each building on the results of the previous:

### Stage 1: Redistribution Models (M1-M7)

Seven-model sequence estimating multilevel linear models of redistribution preferences (gincdif, 1-5 scale) with individuals nested in countries. Begins with a null model to establish the ICC (8.0%), adds individual predictors (income, ideology, trust, demographics), country-level economic variables (Gini, GDP, unemployment), random slopes for income and ideology, and cross-level interactions. The key finding is the income x Gini interaction (coef = 0.012, p = 0.002): higher inequality weakens the negative income effect on redistribution support.

### Stage 2: Welfare Regime Extension (Notebook 04)

Descriptive analysis of redistribution preferences by Esping-Andersen regime type. Post-communist countries show highest support despite least generous welfare states; social democratic countries show lower support, consistent with the thermostat model. Full mixed-effects regime interaction models (M8-M13) require pymer4/R and are not yet estimated.

### Stage 3: AI Exposure Extension (M14-M16)

Tests whether Felten, Raj & Seamans (2021) AIOE scores predict redistribution preferences. Result: null across all specifications (p = 0.857). The direct pathway from AI exposure to redistribution attitudes is not supported. This null finding redirects attention to the indirect channel: AI reshapes income distributions, which activates the income x Gini interaction.

### Stage 4: Redistribution Simulation

Agent-based model parameterized by Stage 1 regression coefficients. Tests whether inequality shocks (motivated by AI-driven labor displacement) produce discontinuous tipping in redistribution attitude equilibria. Result: gradual drift only (~0.022 points per Gini percentage point). The income x Gini interaction is too small for tipping. This lower-bound result motivates the dual-domain comparison.

### Stage 5: Trust Models and Simulation (T1-T7)

ICC comparison reveals trust in parliament (18.1%) has 2.3x more between-country variation than redistribution (8.0%). A parallel model sequence tests education x corruption as the cross-level interaction, following Van der Meer & Hakhverdian (2017). The interaction is significant (coef = 0.050, p < 0.001) and 4x larger than the redistribution interaction. A second simulation applies corruption shocks with a self-reinforcing feedback loop (trust erosion degrades governance, which further erodes trust). Tipping observed at -15 CPI in all 5 representative countries.

## Data

- **Individual-level:** ESS Round 9 (2018), ~36,000 respondents across 28 European countries
- **Country-level economic:** Gini, GDP per capita, unemployment (World Bank/OECD, 2018)
- **Institutional:** EPL, ALMP spending, union density, social spending (OECD/ICTWSS, 2018)
- **AI exposure:** Felten AIOE scores aggregated via Eurostat LFS employment weights
- **Corruption:** Transparency International CPI 2018

## Estimation

All models estimated via REML using statsmodels MixedLM. Level-1 predictors are grand-mean centered; Level-2 predictors are z-score standardized. The 28-country sample constrains the number of simultaneous Level-2 predictors. Non-OECD countries are missing institutional data and are handled through subsample analyses.

## Key Findings

1. **Redistribution preferences** are weakly clustered across countries (ICC = 8.0%). The income x Gini interaction is significant but small (beta = 0.012). AI exposure has no direct effect (p = 0.857). Simulation shows gradual drift, no tipping.

2. **Institutional trust** is strongly clustered (ICC = 18.1%). The education x corruption interaction is 4x larger. Corruption is the dominant country-level predictor (coef = 0.93, p < 0.001). Simulation shows tipping at -15 CPI, amplified 40% by the feedback loop.

3. **The structural difference** is the feedback loop. Trust erosion degrades governance quality, which further erodes trust. Redistribution preferences lack this self-reinforcing mechanism. The domain most critical for democratic stability is also the most tipping-prone.

## Limitations

- Cross-sectional data (ESS 2018) limits causal inference. Future rounds could exploit temporal variation.
- Country-level AI exposure measures capture susceptibility, not actual displacement.
- 28 Level-2 units constrains simultaneous country-level predictors.
- Trust simulation feedback loop strength (0.02 per timestep) is a calibration parameter, not empirically estimated.

## References

Core references: Meltzer & Richard (1981), Esping-Andersen (1990), Hall & Soskice (2001), Thewissen & Rueda (2019), Felten, Raj & Seamans (2021), Van der Meer & Hakhverdian (2017), Minniti, Prettner & Venturini (2025). Full reference list in the research proposal archive.

---

**Last Updated:** March 2026
