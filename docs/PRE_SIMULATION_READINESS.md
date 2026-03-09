# PRE-SIMULATION READINESS REPORT

Generated: 2026-03-06

---

## DATA STATUS

| Dataset | Status | Details |
|---------|--------|---------|
| Individual data (ESS9) | OK | 48,436 obs, 28 countries, 609 variables |
| Gini coefficients | OK | World Bank SI.POV.GINI, 23/28 countries (missing CH, IS, ME, RS, GB) |
| GDP per capita | OK | World Bank NY.GDP.PCAP.PP.CD, 28/28 countries |
| Unemployment rate | OK | World Bank SL.UEM.TOTL.ZS, 28/28 countries |
| Institutional data | OK | OECD/ICTWSS, 20-23 countries depending on indicator |
| AI exposure data | OK (NEW) | Real Felten AIOE scores for all 28 countries, aggregated via Eurostat LFS employment weights |

- **Complete cases for core model (M1-M7):** 31,393 individuals in 26 countries
- **Complete cases for AI model (M14):** 30,656 individuals in 25 countries
- **Countries excluded from core model:** HU (missing Gini), IT (missing Gini)

---

## MODEL RESULTS

### Core Replication (Notebook 03) — UNCHANGED

All 7 models have outputs. Results match exactly across re-estimation.

| Statistic | Value |
|-----------|-------|
| ICC (null model) | 0.0770 |
| ICC (final model, M7) | 0.0628 |
| N individuals | 31,393 |
| N countries | 26 |

**Key Fixed Effects (Model 7 — final model):**

| Predictor | Coef | SE | p-value | Sig |
|-----------|------|-----|---------|-----|
| Intercept | 3.853 | 0.048 | <0.001 | *** |
| income_c | -0.039 | 0.002 | <0.001 | *** |
| education_c | -0.009 | 0.001 | <0.001 | *** |
| age_c | 0.003 | 0.000 | <0.001 | *** |
| female | 0.078 | 0.011 | <0.001 | *** |
| employed | 0.026 | 0.012 | 0.038 | * |
| ideology_c | -0.079 | 0.012 | <0.001 | *** |
| political_trust_c | -0.027 | 0.002 | <0.001 | *** |
| meritocracy_index_c | 0.095 | 0.008 | <0.001 | *** |
| gini_z | 0.082 | 0.055 | 0.137 | ns |
| gdp_per_capita_z | 0.043 | 0.059 | 0.462 | ns |
| unemployment_rate_z | 0.054 | 0.048 | 0.263 | ns |
| ideology_c:gini_z | 0.028 | 0.012 | 0.024 | * |

**Cross-Level Interactions:**

| Interaction | Model | Coef | SE | p-value | 95% CI |
|-------------|-------|------|-----|---------|--------|
| Income x Gini | M5 | 0.012 | 0.004 | 0.002 | [0.005, 0.019] |
| Ideology x Gini | M7 | 0.028 | 0.012 | 0.024 | [0.004, 0.052] |

**Random Effects (Model 7):**

| Component | Value |
|-----------|-------|
| Country intercept variance (tau) | 0.0558 |
| Ideology slope variance | 0.0036 |
| Intercept-slope covariance | 0.0080 |
| Residual variance (sigma^2) | 0.8328 |

**Model Fit (Log-Likelihood progression):**

| Model | Log-Likelihood | Resid. Var | Intercept Var |
|-------|---------------|------------|---------------|
| M1: Null | -43,437 | 0.928 | 0.077 |
| M2: L1 | -42,121 | 0.852 | 0.058 |
| M3: L1+L2 | -42,124 | 0.852 | 0.052 |
| M4: RS Income | -42,096 | 0.849 | 0.055 |
| M5: Income x Gini | -42,096 | 0.849 | 0.052 |
| M6: RS Ideology | -41,809 | 0.833 | 0.059 |
| M7: Ideology x Gini | -41,810 | 0.833 | 0.056 |

Note: AIC/BIC not available (statsmodels does not compute these for REML-estimated models).

### AI Exposure Extension (Notebook 05) — RE-RUN WITH NEW DATA

All three models converged. No convergence warnings (Model 15 converged cleanly this time, unlike the old run).

| Model | Key Variable | Coef | SE | p-value | Sig |
|-------|-------------|------|-----|---------|-----|
| M14: AI main effect | ai_exposure_oecd_z | -0.014 | 0.076 | 0.857 | ns |
| M15: AI x Regime | ai_exposure_oecd_z | -0.134 | 0.193 | 0.489 | ns |
| M15: AI x Post-Communist | interaction | 0.285 | 0.219 | 0.194 | ns |
| M15: AI x Mediterranean | interaction | 0.254 | 0.726 | 0.726 | ns |
| M16: Social exposure | social_exposure_z | -0.013 | 0.071 | 0.857 | ns |

**Interpretation:** AI exposure (Felten AIOE) does not significantly predict redistribution preferences at the country level. Direction is slightly negative (higher AI exposure = marginally less redistribution support), opposite to the technological threat hypothesis. No regime interactions are significant.

**What changed from old data:** The country rankings reversed entirely. Old data: Post-Communist highest exposure, Social Democratic lowest. New data: Liberal (1.21) > Social Democratic (0.99) > Conservative (0.72) > Mediterranean (-0.53) > Post-Communist (-0.78). This is substantively correct — Felten AIOE measures cognitive/professional AI exposure, not manufacturing automation risk.

**Country-level correlation:** AI exposure x redistribution support: r = 0.285 (weak positive, not significant).

---

## SIMULATION-READY

| Item | Status |
|------|--------|
| Parameter file generated | Yes: `outputs/simulation_parameters.json` |
| Countries with complete parameters | 26 of 28 |
| Countries missing parameters | HU (no random intercept, no Gini), IT (no random intercept) |
| Welfare regime assignments | 27 assigned, 1 unassigned (IS) |

**Welfare Regime Assignments (Esping-Andersen):**

| Regime | Countries |
|--------|-----------|
| Social Democratic | DK, FI, NO, SE |
| Conservative/Corporatist | AT, BE, CH, DE, FR, NL |
| Liberal | GB, IE |
| Mediterranean | CY, ES, IT, PT |
| Post-Communist | BG, CZ, EE, HR, HU, LT, LV, ME, PL, RS, SI |
| Unassigned | IS |

**Parameter file contents:**
- `fixed_effects`: 13 parameters with coef, SE, p-value, 95% CI
- `income_gini_interaction_model5`: separate entry for simulation tipping dynamics
- `random_effects`: tau, sigma^2, ICC (null and final)
- `country_parameters`: 28 entries with random intercept, random slope (ideology), Gini, GDP, unemployment, AI exposure, z-scored values, regime assignments

---

## REPOSITORY STATUS

| Check | Status |
|-------|--------|
| Placeholder text (`[Your Name]`, etc.) | 0 found |
| TODO items | 3 (all in OECD API stub in `scripts/fetch_oecd_data.py`) |
| Junk files | 1 (`analysis.log` — harmless log file) |
| README | 87 lines, leads with findings |
| `docs/DATA_SOURCES.md` | Verified provenance version (106 lines) |
| `PHASE_1_COMPLETE.md` | Deleted |
| `PROJECT_STATUS.md` | Deleted |
| `DATA_COLLECTION_STATUS.md` | Deleted |

---

## FIGURES

18 figures in `outputs/figures/`. All from real data.

| Figure | Source | Status |
|--------|--------|--------|
| `01_country_means.png` | NB 01 | Real data |
| `01_economic_correlations.png` | NB 01 | Real data |
| `01_bivariate_relationships.png` | NB 01 | Real data |
| `01_correlations.png` | NB 01 | Real data |
| `01_meritocracy_items.png` | NB 01 | Real data |
| `01_employment_status.png` | NB 01 | Real data |
| `02_regime_comparison.png` | NB 02 | Real data |
| `02_correlation_centered.png` | NB 02 | Real data |
| `03_caterpillar_plot.png` | NB 03 | Real model results |
| `03_random_slopes_income.png` | NB 03 | Real model results |
| `03_interaction_income_gini.png` | NB 03 | Real model results |
| `03_random_slopes_ideology.png` | NB 03 | Real model results |
| `03_interaction_ideology_gini.png` | NB 03 | Real model results |
| `03_model_fit_aic.png` | NB 03 | Real model results |
| `05_ai_exposure_by_regime.png` | NB 05 | REGENERATED with real Felten AIOE |
| `05_ai_redistribution_scatter.png` | NB 05 | REGENERATED with real Felten AIOE |
| `05_ai_regime_interaction.png` | NB 05 | REGENERATED with real Felten AIOE |
| `05_ai_education_interaction.png` | NB 05 | REGENERATED with real Felten AIOE |

---

## BLOCKERS FOR SIMULATION BUILD

1. **IS (Iceland) has no welfare regime assignment.** Typically Social Democratic but not assigned in `config.py`. The simulation will need to handle this (assign it manually or exclude it).

2. **HU and IT excluded from model** — no random intercepts for these countries. If the simulation needs all 28 countries, you'll need to decide how to handle these (use regime-average intercepts, or restrict to 26 countries).

3. **AIC/BIC unavailable.** statsmodels MixedLM does not compute AIC/BIC for REML-estimated models. Log-likelihood is available. If AIC/BIC are needed, re-estimate with ML instead of REML (produces slightly different variance estimates).

4. **AI exposure is NOT significant.** The simulation will not be able to use AI exposure as a driver of tipping dynamics. The Income x Gini interaction (p=0.002) is the primary nonlinearity source.

None of these are hard blockers for starting the simulation build.

---

## RECOMMENDED ACTIONS BEFORE SIMULATION WEEK

1. **Decide on IS regime assignment** — add `"IS": "Social Democratic"` to config.py WELFARE_REGIMES_ESPING, or document the exclusion.

2. **Decide on HU/IT handling** — assign regime-average random intercepts, or restrict the simulation to 26 countries.

3. **Consider deleting `analysis.log`** — harmless but unnecessary.

4. **Update README line 30** — currently says "OECD AI exposure index, Frey & Osborne automation risk" which should say "Felten, Raj & Seamans (2021) AIOE scores" to reflect actual data.

5. **Optionally update `docs/SUMMARY_FINDINGS.md`** — notebook 05 results are now finalized (AI exposure NOT significant with real data). The summary already flagged results as stale; can now be updated with the actual null finding.
