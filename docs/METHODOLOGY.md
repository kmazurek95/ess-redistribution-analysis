# Methodology Guide

Comprehensive explanation of the multilevel modeling approach, variable transformations, and typology construction methods used in this analysis.

---

## Table of Contents

1. [Multilevel Modeling Rationale](#multilevel-modeling-rationale)
2. [Variable Centering and Standardization](#variable-centering-and-standardization)
3. [Model Building Sequence](#model-building-sequence)
4. [Random Effects Interpretation](#random-effects-interpretation)
5. [Cross-Level Interactions](#cross-level-interactions)
6. [Welfare Regime Classification](#welfare-regime-classification)
7. [Institutional Indicators](#institutional-indicators)
8. [AI/Automation Exposure Measurement](#ai-automation-exposure-measurement)
9. [Typology Construction](#typology-construction)
10. [Key References](#key-references)

---

## Multilevel Modeling Rationale

### Why Multilevel Models?

Individuals (Level 1) are **nested within countries** (Level 2), violating the independence assumption of standard OLS regression. Multilevel models (also called hierarchical linear models or mixed-effects models) account for this clustering by:

1. **Allowing intercepts to vary by country** — Countries have different baseline levels of redistribution support
2. **Allowing slopes to vary by country** — The effect of income on redistribution support may differ across countries
3. **Modeling both levels simultaneously** — Individual characteristics AND country context shape attitudes

### Key Advantages

- **Correct standard errors** — OLS underestimates SEs when ignoring clustering
- **Partition variance** — Decompose variance into within-country and between-country components
- **Test cross-level interactions** — Does country-level inequality moderate individual-level income effects?
- **Use all data efficiently** — Unlike country fixed effects, multilevel models estimate country-level effects

### Mathematical Specification

**Level 1 (individual i in country j):**
```
Y_ij = β₀j + β₁j(Income_ij) + β₂j(PoliticalTrust_ij) + ... + ε_ij
```

**Level 2 (country j):**
```
β₀j = γ₀₀ + γ₀₁(Gini_j) + γ₀₂(GDP_j) + u₀j  (random intercept)
β₁j = γ₁₀ + γ₁₁(Gini_j) + u₁j               (random slope for income)
```

**Combined form:**
```
Y_ij = γ₀₀ + γ₁₀(Income_ij) + γ₀₁(Gini_j) + γ₁₁(Income_ij × Gini_j) + u₀j + u₁j(Income_ij) + ε_ij
```

Where:
- **γ** = Fixed effects (population-average parameters)
- **u** = Random effects (country-specific deviations)
- **ε** = Individual-level residuals

---

## Variable Centering and Standardization

### Level-1 Variables: Grand-Mean Centering

**What:** Subtract the overall sample mean from each individual's score

**Formula:** `X_centered = X - mean(X)`

**Why:**
1. **Interpretability** — Intercept represents outcome for someone at the average of all predictors
2. **Reduces multicollinearity** — Especially important for interaction terms
3. **Facilitates comparison** — Centered coefficients are comparable across models

**Applied to:** Income, political trust, age, education, meritocracy index

**Example:**
```python
# Original income ranges from 1-10 (deciles)
# Mean income = 5.5
# Centered: income_c ranges from -4.5 to +4.5
# Interpretation: One decile above the mean
```

### Level-2 Variables: Z-Score Standardization

**What:** Transform to mean=0, SD=1

**Formula:** `X_z = (X - mean(X)) / SD(X)`

**Why:**
1. **Comparability** — Coefficients represent effect of 1 SD change (standardized effect size)
2. **Different scales** — Gini (0-100), GDP ($20k-$70k), ALMP (0-2% GDP) → all on same scale
3. **Interpretability** — Easy to compare relative importance of country-level predictors

**Applied to:** Gini, GDP, unemployment, EPL, ALMP, union density, social spending, AI exposure

**Example:**
```python
# Original Gini: mean=31.5, SD=4.2
# Gini_z = 0 means a country at average inequality
# Gini_z = +1 means a country 1 SD above average (higher inequality)
# Coefficient: "Effect of moving from average to high-inequality country"
```

### Why Not Standardize Level-1?

- Level-1 variables have meaningful scales (income deciles, age in years)
- Standardization would obscure substantive interpretation
- Grand-mean centering is sufficient for dealing with multicollinearity

---

## Model Building Sequence

### The 7-Model Replication Sequence

**Model 1: Null Model**
- Formula: `Y ~ 1 + (1|country)`
- Purpose: Calculate ICC (how much variance is between countries?)
- No predictors — just partition variance

**Model 2: Add Income (Level-1)**
- Formula: `Y ~ income_c + (1|country)`
- Purpose: Test self-interest hypothesis
- Expected: Negative coefficient (higher income → less support)

**Model 3: Add Political Trust (Level-1)**
- Formula: `Y ~ income_c + trust_c + (1|country)`
- Purpose: Test legitimacy hypothesis
- Expected: Positive coefficient (higher trust → more support)

**Model 4: Add All Level-1 Controls**
- Formula: `Y ~ income_c + trust_c + age_c + female + education_c + meritocracy_c + (1|country)`
- Purpose: Control for confounders
- Ensures income/trust effects aren't spurious

**Model 5: Add Level-2 Variables**
- Formula: `Y ~ ... + gini_z + gdp_z + unemployment_z + trust_l2 + (1|country)`
- Purpose: Test country-level effects
- Expected: Gini positive (higher inequality → more support)

**Model 6: Random Slopes**
- Formula: `Y ~ ... + (income_c + trust_c|country)`
- Purpose: Allow effects to vary by country
- Tests whether income/trust slopes differ across contexts

**Model 7: Cross-Level Interactions**
- Formula: `Y ~ ... + income_c:gini_z + trust_c:gdp_z + (income_c + trust_c|country)`
- Purpose: Test whether country context moderates individual effects
- **Key hypothesis:** Income × Gini interaction

### Interpreting the Income × Gini Interaction

**Main question:** Does inequality moderate the self-interest effect?

**Hypothesis:** In high-inequality countries, the rich support redistribution more (or oppose it less) because inequality is salient

**Interpretation if γ₁₁ > 0:**
- At low Gini (egalitarian countries): Income has a strong negative effect
- At high Gini (unequal countries): Income effect is weaker (less negative)
- **Mechanism:** Inequality makes redistribution a more broadly shared concern

---

## Random Effects Interpretation

### Intraclass Correlation (ICC)

**Formula:** `ICC = σ²_between / (σ²_between + σ²_within)`

**Interpretation:**
- ICC = 0.15 → 15% of variance is between countries, 85% within countries
- Justifies multilevel approach (if ICC ≈ 0, could use OLS with robust SEs)

**Typical values:**
- Attitudes: ICC = 0.05-0.20 (modest clustering)
- Behaviors: ICC = 0.01-0.10 (weaker clustering)
- Policy outcomes: ICC = 0.30-0.50 (strong clustering)

### Random Intercepts

**What:** Country-specific deviations from the overall intercept

**Interpretation:**
- u₀j = +0.5 → Country j has 0.5 points higher baseline support (after controlling for X)
- u₀j = -0.3 → Country j has 0.3 points lower baseline support

**Visualization:** Caterpillar plots showing country rankings

### Random Slopes

**What:** Country-specific deviations from the overall slope

**Interpretation:**
- u₁j = -0.2 → In country j, income effect is 0.2 stronger (more negative) than average
- u₁j = +0.1 → In country j, income effect is 0.1 weaker (less negative) than average

**Implication:** The relationship between income and redistribution support is **context-dependent**

---

## Cross-Level Interactions

### Conceptual Meaning

Cross-level interactions test whether **Level-2 variables moderate Level-1 relationships**

**Example:** Does country-level inequality (L2) moderate the effect of individual income (L1)?

### Interpretation Strategy

1. **Plot the interaction** — Show income slopes at low/medium/high Gini
2. **Simple slopes analysis** — Test income effect at specific Gini values
3. **Regions of significance** — At what Gini values is income effect significant?

### Income × Gini Example

**If γ₁₁ = +0.08 (p < 0.01):**

```
Predicted support = ... + (-0.15)(Income_c) + (0.20)(Gini_z) + (0.08)(Income_c × Gini_z)
```

**At low inequality (Gini_z = -1):**
```
Effect of income = -0.15 + (0.08)(-1) = -0.23  (strong negative effect)
```

**At high inequality (Gini_z = +1):**
```
Effect of income = -0.15 + (0.08)(+1) = -0.07  (weak negative effect)
```

**Substantive interpretation:** Self-interest matters more in egalitarian contexts; in unequal contexts, even the rich support redistribution

---

## Welfare Regime Classification

### Esping-Andersen Typology (Extended)

**Original "Three Worlds" + Extensions:**

1. **Social Democratic** (DK, SE, NO, FI)
   - Universal benefits, high decommodification
   - Generous ALMP, strong unions
   - Egalitarian values

2. **Conservative/Corporatist** (DE, FR, BE, AT, NL, CH)
   - Occupational welfare, status preservation
   - Social insurance model
   - Moderate redistribution

3. **Liberal** (GB, IE)
   - Means-tested benefits, market reliance
   - Weak unions, low ALMP
   - Residual welfare state

4. **Mediterranean** (ES, IT, PT, CY)
   - Family-based welfare, fragmented coverage
   - Labor market dualism (insiders/outsiders)
   - Recent welfare expansion

5. **Post-Communist** (CZ, EE, HR, HU, LT, LV, PL, SI, BG, RS, ME)
   - Transition from socialist to market systems
   - Weak institutions, low trust
   - High inequality, limited ALMP

**Theoretical basis:** Esping-Andersen (1990), *The Three Worlds of Welfare Capitalism*

### Varieties of Capitalism (Hall & Soskice)

**Alternative classification focusing on labor market coordination:**

1. **Liberal Market Economies (LME):** GB, IE
   - Flexible labor markets, weak employment protection
   - Firm-level wage bargaining
   - Market-based coordination

2. **Coordinated Market Economies (CME):** DE, AT, BE, NL, CH, DK, SE, NO, FI
   - Strong employment protection, coordinated wage-setting
   - Industry/sector-level bargaining
   - Non-market coordination (institutions, networks)

3. **Mediterranean Market Economies (MME):** ES, IT, PT, FR, CY
   - State-led coordination, rigid labor markets
   - High EPL, low ALMP
   - Mixed coordination modes

4. **Dependent Market Economies (DME):** CZ, EE, HR, HU, LT, LV, PL, SI, BG, RS, ME
   - Foreign direct investment-dependent
   - Low coordination capacity
   - Hierarchical coordination

**Theoretical basis:** Hall & Soskice (2001), *Varieties of Capitalism*

### Regime vs. Continuous Indicators

**Tradeoff:**
- **Regime dummies:** Capture holistic institutional packages, easier interpretation
- **Continuous indicators:** More precise, show within-regime variation, avoid arbitrary cutoffs

**Our approach:** Use both
1. Test regime effects (Models 8-10)
2. Test continuous institutional indicators (Models 11-13)
3. Compare model fit and variance explained

---

## Institutional Indicators

### Employment Protection Legislation (EPL)

**What it measures:** Legal restrictions on firing workers

**Source:** OECD Employment Protection Database

**Variable:** EPRC_V4 (EPL for regular contracts, version 4)

**Scale:** 0-6 (higher = stricter protection)

**Theoretical relevance:**
- **Insider/outsider theory:** EPL protects insiders, creates labor market dualism
- **Redistribution preferences:** Strong EPL may reduce demand for redistribution (job security substitutes for benefits)

**Our hypothesis:** EPL moderates income effect (strong EPL buffers self-interest)

### Active Labor Market Policy (ALMP) Spending

**What it measures:** Public spending on job training, placement services, employment subsidies

**Source:** OECD SOCX (Social Expenditure Database)

**Variable:** Active labor market programmes as % GDP

**Scale:** 0-2% (typically 0.1-1.5%)

**Theoretical relevance:**
- **Investment vs. compensation:** ALMP prepares workers for new jobs (investment) vs. unemployment benefits (compensation)
- **Skill development:** Strong ALMP increases perceived opportunity for upward mobility
- **Redistribution preferences:** ALMP may reduce demand for passive transfers

**Our hypothesis:** ALMP moderates income effect (strong ALMP maintains solidarity even among winners)

### Union Density

**What it measures:** Percentage of employees who are union members

**Source:** ICTWSS Database (Institutional Characteristics of Trade Unions, Wage Setting, State Intervention and Social Pacts)

**Variable:** UD (Union Density)

**Scale:** 0-100% (typically 5-80%)

**Theoretical relevance:**
- **Power resources theory:** Union strength shapes welfare state generosity
- **Solidarity:** High union density promotes collective interests over individual self-interest
- **Redistribution preferences:** Strong unions mobilize support for redistribution

### Social Spending

**What it measures:** Total public social expenditure as % GDP

**Source:** OECD SOCX

**Variable:** Total social expenditure (% GDP)

**Scale:** 0-35% (typically 15-30%)

**Theoretical relevance:**
- **Welfare state size:** Reflects generosity and scope of social protection
- **Self-reinforcing support:** Large welfare states create constituencies that defend them ("welfare state feedback")
- **Redistribution preferences:** High spending may indicate already-satisfied demand

---

## AI/Automation Exposure Measurement

### Felten, Raj & Seamans (2021) AIOE

**Construction:** Country-level aggregation of AI Occupational Exposure scores:
1. Occupation-level AIOE at SOC 6-digit level (774 occupations)
2. Averaged to SOC 2-digit major groups
3. Mapped to ISCO-08 1-digit groups via BLS/ILO crosswalk
4. Employment-weighted country averages using Eurostat LFS 2018

**Interpretation:** Higher values = more occupational task overlap with AI capabilities. Measures cognitive/professional exposure, not manufacturing automation.

**Country rankings:** Service economies (GB, CH, NO, SE) score highest; post-communist manufacturing economies (RS, HU, BG) score lowest.

**Empirical result:** No significant direct effect on redistribution preferences (coef = -0.014, p = 0.857). All model specifications (main effect, regime interactions, social exposure composite) yield null results.

**Reproduction:** See `scripts/aggregate_aioe.py`

### Frey & Osborne Automation Probability

**Construction:**
1. Occupation-level automation probabilities (702 US occupations)
2. Weighted by country employment shares

**Formula:**
```
Country automation risk = Σ(p_occupation × employment_share_occupation)
```

**Status:** Not yet computed for this project. The `automation_risk` column contains placeholder NaN values.

**Limitations:**
- Based on US occupations (may not transfer perfectly)
- Automation probability ≠ actual job loss (complementary technologies, task reorganization)

### Social Exposure Composite (Our Contribution)

**Concept:** Technical AI exposure × Institutional weakness

**Rationale:** Countries with high technical exposure BUT weak institutions are most **socially vulnerable**

**Construction:**
```python
# Standardize components
tech_exposure_z = standardize(ai_exposure_oecd)
institutional_weakness_z = -standardize(epl + almp + social_spending)

# Composite
social_exposure = tech_exposure_z × institutional_weakness_z
```

**Interpretation:**
- **High social exposure:** High AI risk + weak institutions (e.g., Poland)
- **Low social exposure:** Low AI risk + strong institutions (e.g., Norway)
- **Moderate (buffered):** High AI risk + strong institutions (e.g., Denmark)

**Policy relevance:** Identifies countries needing institutional strengthening to manage AI transition

### Theoretical Pivot: The Indirect Channel

The null direct effect of AI exposure on redistribution preferences (p = 0.857) led to a redesign of the simulation component. Rather than modeling AI exposure as a direct attitudinal driver, the simulation treats AI-driven labor displacement as an exogenous source of inequality shocks. The causal chain is: AI labor displacement shifts income distributions and compresses middle-income ranges, increasing the Gini coefficient, which then activates the significant income x Gini cross-level interaction (coef = 0.012, p = 0.002). This indirect channel is supported by recent empirical work showing AI innovation reduces labor share by 0.5-1.6% per doubling of regional AI patent intensity in European regions (Minniti, Prettner & Venturini, 2025, European Economic Review), and by evidence that automation risk effects on redistribution preferences are moderated by welfare state generosity (Busemeyer & Sahm, 2021; Sacchi et al., 2020).

This framing is more empirically grounded than the direct channel: the simulation only uses parameters with statistical support, and the AI narrative provides the substantive motivation for the inequality shocks rather than entering the model equations directly.

---

## Typology Construction

### From Continuous Indicators to Country Types

**Goal:** Reduce complexity, identify ideal-type cases for qualitative study

**Approach:** Combine quantitative clustering with theoretical interpretation

### Step 1: Select Dimensions

**For institutional mediation typology:**
1. EPL strictness (labor market protection)
2. ALMP spending (investment in skills)
3. Union density (collective organization)

**For social exposure typology:**
1. Technical AI exposure (OECD index or Frey & Osborne)
2. Institutional strength (composite of EPL, ALMP, social spending)

### Step 2: Cluster Analysis

**Method:** K-means clustering or hierarchical clustering

**Considerations:**
- **Number of clusters:** Determined by dendrogram or elbow plot (typically 3-5)
- **Standardization:** Essential (variables on different scales)
- **Validation:** Silhouette scores, theoretical coherence

### Step 3: Theoretical Interpretation

**Map clusters to theoretical frameworks:**
- Do clusters align with Esping-Andersen regimes?
- Do they reveal new patterns (e.g., high-AI/low-institution cluster)?

**Label clusters descriptively:**
- "Institutional buffers" (high ALMP, high EPL)
- "Market-oriented" (low ALMP, low EPL)
- "Transition" (moderate indicators, high variation)

### Step 4: Case Selection

**For qualitative follow-up:**
1. **Prototypical cases:** Countries at cluster centers
2. **Deviant cases:** Countries that don't fit expected patterns
3. **Comparison pairs:** Similar on some dimensions, different on others

**Example:**
- **Denmark** (high AI exposure, strong institutions) vs. **Poland** (high AI exposure, weak institutions)
- **Research question:** How do institutions mediate political responses to automation risk?

---

## Key References

### Multilevel Modeling

- Raudenbush, S. W., & Bryk, A. S. (2002). *Hierarchical Linear Models*. Sage.
- Snijders, T. A. B., & Bosker, R. J. (2012). *Multilevel Analysis*. Sage.
- Gelman, A., & Hill, J. (2006). *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge University Press.

### Welfare State Theory

- Esping-Andersen, G. (1990). *The Three Worlds of Welfare Capitalism*. Princeton University Press.
- Hall, P. A., & Soskice, D. (2001). *Varieties of Capitalism*. Oxford University Press.
- Korpi, W., & Palme, J. (1998). The paradox of redistribution and strategies of equality. *American Sociological Review*, 63(5), 661-687.

### Redistribution Preferences

- Meltzer, A. H., & Richard, S. F. (1981). A rational theory of the size of government. *Journal of Political Economy*, 89(5), 914-927.
- Iversen, T., & Soskice, D. (2001). An asset theory of social policy preferences. *American Political Science Review*, 95(4), 875-893.
- Rehm, P. (2016). *Risk Inequality and Welfare States*. Cambridge University Press.

### Institutional Political Economy

- Pierson, P. (2001). *The New Politics of the Welfare State*. Oxford University Press.
- Thelen, K. (2014). *Varieties of Liberalization and the New Politics of Social Solidarity*. Cambridge University Press.
- Hemerijck, A. (2013). *Changing Welfare States*. Oxford University Press.

### AI and Labor Markets

- Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? *Technological Forecasting and Social Change*, 114, 254-280.
- Acemoglu, D., & Restrepo, P. (2020). Robots and jobs: Evidence from US labor markets. *Journal of Political Economy*, 128(6), 2188-2244.
- Felten, E., Raj, M., & Seamans, R. (2021). Occupational, industry, and geographic exposure to artificial intelligence. *Strategic Management Journal*, 42(12), 2195-2217.

### Welfare State Adaptation

- Esping-Andersen, G., et al. (2002). *Why We Need a New Welfare State*. Oxford University Press.
- Hacker, J. S. (2006). *The Great Risk Shift*. Oxford University Press.
- Beramendi, P., et al. (2015). *The Politics of Advanced Capitalism*. Cambridge University Press.

---

**Last Updated:** February 2026
**For:** ESS Redistribution Analysis — REPAIR PhD Application
