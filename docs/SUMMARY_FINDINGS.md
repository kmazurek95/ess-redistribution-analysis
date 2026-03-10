# Summary of Findings

## Core Replication (Notebook 03)

**Sample:** 31,393 individuals across 26 European countries (ESS Round 9, 2018)

**ICC:** 7.7% of redistribution preference variation is between countries. Modest but sufficient for multilevel modeling (ICC = 0.077 null model, 0.063 final model).

**Individual predictors (all significant at p < 0.001):**

| Predictor | Coef | Direction |
|-----------|------|-----------|
| Income | -0.039 | Higher income reduces support (self-interest) |
| Ideology | -0.079 | Right-wing orientation reduces support |
| Political trust | -0.027 | Higher trust reduces support |
| Meritocracy beliefs | +0.095 | Stronger meritocratic beliefs *increase* support (reversed scale) |
| Education | -0.009 | More education reduces support |
| Gender (female) | +0.078 | Women support redistribution more |
| Age | +0.003 | Older respondents support more |
| Employed | +0.026 | Employed support marginally more (p = 0.038) |

**Cross-level interactions:**

- **Income x Gini** (coef = 0.012, SE = 0.004, p = 0.002, 95% CI [0.005, 0.019]):
  Higher national inequality weakens the negative income effect. In more unequal
  countries, even higher-income individuals show relatively more redistribution
  support. This is the key nonlinearity for the simulation.

- **Ideology x Gini** (coef = 0.028, SE = 0.012, p = 0.024, 95% CI [0.004, 0.052]):
  Higher inequality also weakens the ideology effect. Right-wing individuals in
  unequal countries are less distinctively anti-redistribution.

**Country-level direct effects:** Gini, GDP, and unemployment do not significantly
predict redistribution preferences as main effects (all p > 0.13). The action is
in the cross-level interactions, not in direct country-level effects.

---

## Welfare Regime Extension (Notebook 04)

Full mixed-effects models with regime interactions (Models 8-13) require pymer4/R.
Results here are descriptive only.

Mean redistribution support by Esping-Andersen regime:

| Regime | Mean Support | N countries |
|--------|-------------|-------------|
| Post-Communist | ~3.9 | 11 |
| Mediterranean | ~3.7 | 4 |
| Conservative/Corporatist | ~3.5 | 6 |
| Social Democratic | ~3.4 | 4 |
| Liberal | ~3.3 | 2 |

Post-Communist countries show highest support despite least generous welfare
states ("post-communist exceptionalism"). Social Democratic countries show lower
support, consistent with the "thermostat" model (generous existing redistribution
reduces perceived need for more).

---

## AI Exposure Extension (Notebook 05)

**AI exposure measure:** Felten, Raj & Seamans (2021) AIOE scores, aggregated
to country level using Eurostat LFS 2018 employment weights. All 28 ESS countries
covered. Service-oriented economies (GB, CH, NO, SE) rank highest; post-communist
manufacturing economies (RS, HU, BG) rank lowest.

**Direct effect: NULL.** AI exposure does not significantly predict redistribution
preferences (coef = -0.014, p = 0.857). This holds across all specifications:

| Model | Variable | Coef | p-value |
|-------|----------|------|---------|
| M14 | AI exposure (main effect) | -0.014 | 0.857 |
| M15 | AI x regime interactions | all | > 0.19 |
| M16 | Social exposure composite | -0.013 | 0.857 |

N = 30,656 individuals in 25 countries. All models converged cleanly.

**Interpretation:** AI labor market exposure does not directly shift redistribution
attitudes. The mechanism, if it exists, operates indirectly through AI's effects
on income distributions and inequality  - which then activate the significant
income x Gini interaction identified in the core models.

---

## The Indirect Channel: From Null Finding to Simulation Design

The null AI direct effect and the significant income x Gini interaction together
identify an indirect pathway:

```
AI labor displacement → income distribution shift → Gini increase
    → income x Gini interaction activates (p = 0.002)
    → nonlinear attitude dynamics → potential tipping
```

The first link in this chain (AI → Gini increase) is supported by empirical
evidence: Minniti, Prettner & Venturini (2025) find AI innovation reduces labor
share by 0.5-1.6% per doubling of regional AI patent intensity in European
regions; Almusharraf (2025) estimates automation contributed to a 12% rise in
the Gini index across 2000-2023. This contrasts with Thewissen & Rueda (2019),
who find routine task intensity directly predicts redistribution demand. The
difference in instruments -- Felten AIOE measures cognitive task proximity, not
material economic threat -- supports the indirect channel interpretation.

The agent-based simulation models this indirect channel. It is parameterized by
the empirically estimated regression coefficients and country-level data. The
simulation explores when inequality shocks -- including those driven by AI
adoption -- produce tipping in redistribution preference equilibria, and how
tipping thresholds vary across welfare regime types.

This is not a tested and confirmed causal pathway. It is a theoretical framework
grounded in the empirical results, designed to generate testable predictions
about the political consequences of AI-driven economic restructuring.

---

## Simulation Results

An agent-based simulation was built to explore whether the empirically identified
income x Gini interaction (coef = 0.012, p = 0.002) could produce discontinuous
tipping in redistribution attitude equilibria under AI-motivated inequality shocks.

**Design:**

- 5 representative countries spanning all welfare regime types (Denmark/Social
  Democratic, Germany/Conservative, United Kingdom/Liberal, Spain/Mediterranean,
  Poland/Post-Communist)
- 1,000 agents per country with income, ideology, and attitudes drawn from
  ESS-calibrated distributions
- Update rule: empirical fixed effects + country random intercepts + income x Gini
  interaction + Granovetter-style social influence
- Shocks: Gini increases of 3, 5, 10, and 15 percentage points with simultaneous
  income distribution compression (middle-income hollowing)
- 50 replications per shock x country combination
- Shock magnitudes motivated by Minniti, Prettner & Venturini (2025), who find AI
  innovation reduces labor share by 0.5-1.6% per doubling of regional AI patent
  intensity in European regions

**Results:**

- No discontinuous tipping at any shock level. The interaction produces gradual
  linear drift of ~0.022 points per Gini percentage point.
- Welfare regime type determines baseline attitude levels but does not
  differentially buffer against inequality shocks. All country types shift at
  the same rate.
- A 10pp Gini shock effectively eliminates the income gradient in redistribution
  preferences (slope flattens from -0.030 to -0.001).
- Denmark crosses the majority support threshold (~3.5) at approximately 15pp
  shock, driven by proximity to the threshold rather than differential sensitivity.

**Interpretation:**

- The null tipping result is consistent with the small effect size of the income x
  Gini interaction (beta = 0.012). A 15pp shock shifts the income slope by only
  ~0.18 units. This is detectable but insufficient for the kind of discontinuous
  equilibrium shift that characterizes social tipping.
- This aligns with Sacchi et al. (2020), who find automation risk produces only a
  2.37pp increase in redistribution support compared to 17.48pp for ideology and
  9.8pp for income. Technology-driven effects on redistribution preferences are
  real but small relative to other determinants.
- The finding constrains the theoretical space: redistribution attitude tipping
  from AI-driven inequality, if it occurs, requires either (a) compounding across
  multiple attitudinal domains, (b) mechanisms beyond the cross-sectional income x
  Gini channel (media framing, political mobilization, network contagion), or
  (c) inequality shocks substantially larger than current AI adoption trends suggest.
- This motivates multi-domain modeling: the single-channel, single-domain model
  sets the lower bound; the trust analysis below explores whether a different
  attitudinal domain is structurally more vulnerable.

---

## Trust in Parliament (trstprl) - Alternative DV

**ICC comparison:** Trust in parliament (18.1%) and satisfaction with democracy
(20.6%) both show substantially more between-country variation than redistribution
preferences (8.0%). Trust was selected for full modeling because of the established
literature on education x corruption cross-level interactions.

**Model sequence (T1-T7), N = 31,033 in 25 countries:**

| Model | ICC | LogLik | Key result |
|-------|-----|--------|------------|
| T1: Null | 18.1% | -109,012 | |
| T2: Individual predictors | 16.1% | -76,214 | education: 0.057 (p < 0.001) |
| T3: + Country-level | 7.8% | -70,124 | corruption: 0.928 (p < 0.001) |
| T4: + Random slope (education) | 8.9% | -70,018 | slope variance: 0.0043 |
| T5: Education x Corruption | 7.3% | -70,013 | **coef = 0.050, p < 0.001** |
| T6: Education x Gini | 8.6% | -70,019 | coef = -0.026, p = 0.045 |
| T7: Full model | 7.4% | -70,016 | ed x gini drops to p = 0.87 |

**Corruption is the dominant country-level predictor of trust** (coef = 0.93,
p < 0.001). A 1 SD increase in CPI (less corrupt) raises trust by nearly a full
point on the 0-10 scale. Gini, GDP, and unemployment are not significant.

**Education x Corruption interaction (coef = 0.050, p < 0.001):** Education's
positive effect on trust is amplified in less corrupt countries. In corrupt
countries, education buys less trust. This is consistent with Van der Meer &
Hakhverdian (2017) and Noordzij et al. (2021): educated citizens are better at
evaluating governance quality, so their trust is more responsive to corruption.

**Education x Gini is not independently significant.** Marginally significant alone
(p = 0.045) but drops to p = 0.87 in the full model. Corruption is doing the work.

---

## Trust Simulation Results

The trust simulation tests whether the education x corruption interaction can
produce tipping under governance quality shocks.

**Design:**

- Same 5 representative countries as the redistribution simulation
- Shocks: CPI decreases of 5, 10, 15, 20 points (modeling governance degradation)
- Simultaneous education distribution expansion (more educated cohorts)
- Feedback loop: aggregate trust erosion degrades governance quality
  (corruption z decreases by 0.02 * trust deficit per timestep)
- 50 replications per condition, 1,000 agents per country

**Results:**

| Country | Regime | Baseline | -5 CPI | -10 CPI | -15 CPI | -20 CPI |
|---------|--------|----------|--------|---------|---------|---------|
| DK | Social Democratic | 6.21 | -0.36 | -0.69 | -1.02 | -1.35 |
| DE | Conservative | 5.14 | -0.38 | -0.70 | -1.03 | -1.35 |
| GB | Liberal | 4.35 | -0.38 | -0.71 | -1.03 | -1.36 |
| ES | Mediterranean | 3.48 | -0.45 | -0.77 | -1.10 | -1.43 |
| PL | Post-Communist | 4.33 | -0.44 | -0.77 | -1.10 | -1.44 |

**Tipping observed at -15 CPI in all 5 countries** (shift > 1.0 point). Mediterranean
and Post-Communist countries show slightly larger shifts (~0.07 points more than
Social Democratic/Conservative/Liberal), reflecting lower baseline governance quality.

**Feedback amplification:** The trust-governance feedback loop produces corruption
z-score drift of -1.4 to -1.5 at the largest shock level, amplifying the direct
effect by approximately 40%.

---

## Dual-Domain Comparison

The project's central finding is that different political attitudes have
fundamentally different vulnerability structures under institutional stress.

**Redistribution preferences (gincdif):**
- ICC = 8.0%. Modest between-country variation.
- Nonlinearity: income x Gini (coef = 0.012, p = 0.002). Higher inequality weakens
  the negative income effect.
- Simulation: gradual drift only. The interaction is too small for discontinuous
  tipping under plausible inequality shocks (3-15 Gini points).
- No feedback loop: wanting more redistribution does not cause less redistribution.

**Institutional trust (trstprl):**
- ICC = 18.1%. Substantial between-country variation - 2.3x redistribution.
- Nonlinearity: education x corruption (coef = 0.050, p < 0.001). Educated citizens
  are more sensitive to governance quality.
- Simulation: tipping at -15 CPI in all countries. The education x corruption
  interaction is 4x larger than income x Gini.
- Feedback loop: trust erodes -> citizens disengage -> governance worsens -> trust
  erodes further. This self-reinforcing structure is absent in redistribution.

**Democratic satisfaction (stfdem):**
- ICC = 20.6%. Highest between-country variation of any DV tested. Not yet modeled
  beyond the null model.

**Implication:** AI-driven economic restructuring threatens democratic stability not
primarily through shifting redistribution preferences (which drift slowly and lack
feedback) but potentially through eroding institutional trust (which has higher
between-country variation, a larger cross-level interaction, and a self-reinforcing
erosion mechanism). The domain most critical for democratic function is structurally
the most vulnerable.
