# Methodology

Technical details of the multilevel modeling approach, variable transformations, and simulation design.

---

## Multilevel Model Specification

Individuals (Level 1) are nested within countries (Level 2). The combined model:

```
Y_ij = gamma_00 + gamma_10(X_ij) + gamma_01(Z_j) + gamma_11(X_ij * Z_j) + u_0j + u_1j(X_ij) + e_ij
```

Where gamma = fixed effects, u = random effects (country deviations), e = individual residuals. All models estimated via REML using statsmodels MixedLM with robust standard errors.

## Variable Transformations

**Level-1 (grand-mean centering):** Subtract the sample mean from each individual score. Applied to income, education, age, ideology, political trust, meritocracy index. Intercepts then represent the outcome at the mean of all predictors.

**Level-2 (z-score standardization):** Transform to mean=0, SD=1. Applied to Gini, GDP, unemployment, corruption CPI, EPL, ALMP, union density, social spending, AI exposure. Coefficients represent the effect of a 1 SD change, enabling direct comparison of country-level predictor importance.

## Redistribution Model Sequence (M1-M7)

**DV:** gincdif (reversed, 1-5 scale). N = 31,393 in 26 countries.

| Model | Specification | Key result |
|-------|-------------|------------|
| M1 | Null: `redist ~ 1 + (1\|country)` | ICC = 8.0% |
| M2 | + income_c | coef = -0.039, p < 0.001 |
| M3 | + all L1 predictors | ideology strongest (coef = -0.079) |
| M4 | + L2 economic variables | Gini, GDP, unemployment all ns |
| M5 | + random slope for income | slope variance = 0.0003 |
| M6 | Income x Gini interaction | **coef = 0.012, p = 0.002** |
| M7 | + ideology random slope, ideology x Gini | coef = 0.028, p = 0.024 |

L1 predictors: income_c, ideology_c, political_trust_c, education_c, age_c, female, employed, meritocracy_index_c. L2 predictors: gini_z, gdp_per_capita_z, unemployment_rate_z.

## AI Exposure Models (M14-M16)

| Model | Variable | Coef | p |
|-------|----------|------|---|
| M14 | AI exposure (main effect) | -0.014 | 0.857 |
| M15 | AI x regime interactions | all | > 0.19 |
| M16 | Social exposure composite | -0.013 | 0.857 |

AI exposure measure: Felten, Raj & Seamans (2021) AIOE scores aggregated to country level using Eurostat LFS 2018 employment weights. No direct effect on redistribution preferences in any specification. N = 30,656 in 25 countries.

## Trust Model Sequence (T1-T7)

**DV:** trstprl (0-10 scale). N = 31,033 in 25 countries.

| Model | Specification | Key result |
|-------|-------------|------------|
| T1 | Null | ICC = 18.1% |
| T2 | + L1 predictors | education: 0.057, p < 0.001 |
| T3 | + L2 predictors (incl. corruption) | **corruption: 0.928, p < 0.001** |
| T4 | + random slope for education | slope variance = 0.0043 |
| T5 | Education x corruption interaction | **coef = 0.050, p < 0.001** |
| T6 | Education x Gini interaction | coef = -0.026, p = 0.045 |
| T7 | Full model (both interactions) | ed x Gini drops to p = 0.87 |

L1 predictors: income_c, education_c, ideology_c, age_c, female, employed, meritocracy_index_c. L2 predictors: gini_z, gdp_per_capita_z, unemployment_rate_z, corruption_z.

**Corruption measurement:** Transparency International Corruption Perceptions Index 2018, z-score standardized. Higher CPI = less corrupt. The corruption_z coefficient (0.928) means a 1 SD increase in governance quality raises trust by nearly a full point on the 0-10 scale.

## Welfare Regime Classification

Esping-Andersen extended typology with 5 regime types:

- **Social Democratic:** DK, FI, NO, SE
- **Conservative/Corporatist:** DE, FR, BE, AT, NL, CH
- **Liberal:** GB, IE
- **Mediterranean:** ES, IT, PT, CY
- **Post-Communist:** CZ, EE, HR, HU, LT, LV, PL, SI, BG, RS, ME

Used descriptively in the redistribution analysis (Notebook 04) and as country groupings in the simulation.

## AI/Automation Exposure Measurement

Felten, Raj & Seamans (2021) AIOE: occupation-level AI task overlap scores (774 SOC 6-digit occupations), averaged to SOC 2-digit groups, mapped to ISCO-08 1-digit via BLS/ILO crosswalk, weighted by Eurostat LFS 2018 employment shares. Measures cognitive/professional AI exposure, not manufacturing automation. Service economies (GB, CH, NO) score highest; post-communist manufacturing economies (RS, HU, BG) score lowest.

**Social exposure composite:** Technical AI exposure x institutional weakness (inverse of EPL + ALMP + social spending). Also null (p = 0.857).

**Indirect channel:** The null direct effect combined with the significant income x Gini interaction identifies an indirect pathway: AI labor displacement shifts income distributions, increasing Gini, which activates the cross-level interaction. Supported by Minniti, Prettner & Venturini (2025), who find AI innovation reduces labor share by 0.5-1.6% per doubling of regional AI patent intensity in European regions.

## Simulation Design

### Redistribution Simulation

- 5 representative countries (DK, DE, GB, ES, PL) spanning all welfare regime types
- 1,000 agents per country with income, ideology, attitudes from ESS-calibrated distributions
- Update rule: empirical fixed effects + country random intercepts + income x Gini interaction + Granovetter-style social influence
- Shocks: Gini increases of 3, 5, 10, 15 percentage points
- 50 replications per condition
- Result: gradual linear drift (~0.022 pts/Gini pp), no discontinuous tipping

### Trust Simulation

- Same 5 countries, 1,000 agents, 50 replications
- Update rule: empirical fixed effects + education x corruption interaction + social influence
- Shocks: CPI decreases of 5, 10, 15, 20 points
- **Feedback loop:** When aggregate trust falls below predicted level, corruption_z decreases by 0.02 * trust deficit per timestep, modeling governance degradation from citizen disengagement
- Result: tipping at -15 CPI in all countries, feedback amplifies direct effect by ~40%

### Why Trust Tips and Redistribution Does Not

Two structural differences explain the divergence:

1. **Effect size:** The education x corruption interaction (0.050) is 4x larger than income x Gini (0.012). Corruption shocks propagate more strongly through the attitude equation.

2. **Feedback loop:** Trust erosion degrades governance quality, which further erodes trust. Redistribution preferences have no analogous self-reinforcing mechanism -- wanting more redistribution does not cause less redistribution.

## Key References

- Raudenbush & Bryk (2002), Snijders & Bosker (2012) -- multilevel methods
- Esping-Andersen (1990), Hall & Soskice (2001) -- welfare regimes
- Meltzer & Richard (1981), Rehm (2016) -- redistribution preferences
- Felten, Raj & Seamans (2021), Frey & Osborne (2017) -- AI exposure measurement
- Van der Meer & Hakhverdian (2017), Noordzij et al. (2021) -- education x corruption interaction
- Minniti, Prettner & Venturini (2025) -- AI and labor share

---

**Last Updated:** March 2026
