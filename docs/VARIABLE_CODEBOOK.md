# Variable Codebook  - ESS Redistribution Analysis

Complete reference for all variables used in the analysis.

---

## Table of Contents

1. [Individual-Level Variables (ESS Round 9)](#individual-level-variables)
2. [Country-Level Economic Indicators](#country-level-economic-indicators)
3. [Institutional Variables](#institutional-variables)
4. [AI/Automation Exposure Variables](#ai-automation-exposure-variables)
5. [Derived Variables](#derived-variables)
6. [Welfare Regime Classifications](#welfare-regime-classifications)
7. [Missing Data Codes](#missing-data-codes)

---

## Individual-Level Variables (ESS Round 9)

### Outcome Variable

**`gincdif`  - Support for Government Redistribution**
- **ESS Question:** "To what extent do you agree or disagree: The government should take measures to reduce differences in income levels?"
- **Scale:** 1 (Agree strongly) to 5 (Disagree strongly)
- **Recoded as:** `redist_support` (reversed: 1 = Disagree strongly, 5 = Agree strongly)
- **Interpretation:** Higher values = stronger support for redistribution
- **Missing codes:** 7 (Refusal), 8 (Don't know), 9 (No answer)
- **N (Round 9):** ~36,000 valid responses across 28 countries

---

### Level-1 Predictors (Individual Characteristics)

**`hinctnta`  - Household Income (Deciles)**
- **ESS Question:** Household's total net income from all sources (country-specific deciles)
- **Scale:** 1 (Lowest decile) to 10 (Highest decile)
- **Variable name:** `income`
- **Centering:** Grand-mean centered → `income_c`
- **Missing codes:** 77, 88, 99
- **Expected effect:** Higher income → less support for redistribution (self-interest hypothesis)

**`eduyrs`  - Years of Full-Time Education**
- **ESS Question:** "How many years of full-time education have you completed?"
- **Scale:** Continuous (0-25+)
- **Variable name:** `education`
- **Centering:** Grand-mean centered → `education_c`
- **Missing codes:** 77, 88, 99
- **Expected effect:** Ambiguous (education can increase both efficiency concerns and egalitarian values)

**`agea`  - Age**
- **ESS Question:** "What year were you born?"
- **Scale:** Continuous (15-100+)
- **Variable name:** `age`
- **Centering:** Grand-mean centered → `age_c`
- **Missing codes:** 999
- **Expected effect:** Mixed (older → more redistribution support due to welfare dependence, but age-cohort effects vary)

**`gndr`  - Gender**
- **ESS Question:** Coded by interviewer
- **Scale:** 1 (Male), 2 (Female)
- **Recoded as:** `female` (0 = Male, 1 = Female)
- **Missing codes:** 9
- **Expected effect:** Women → more redistribution support (welfare state reliance)

**`emplrel`  - Employment Status**
- **ESS Question:** "Are you currently in paid work?"
- **Scale:** 1 (Employee), 2 (Self-employed), 3+ (Other)
- **Recoded as:** `employed` (0 = Not employed/other, 1 = Employed)
- **Missing codes:** 6, 7, 8, 9
- **Expected effect:** Employed → less redistribution support (labor market insider status)

**`lrscale`  - Left-Right Self-Placement**
- **ESS Question:** "In politics people sometimes talk of 'left' and 'right'. Where would you place yourself?"
- **Scale:** 0 (Left) to 10 (Right)
- **Variable name:** `ideology`
- **Centering:** Grand-mean centered → `ideology_c`
- **Missing codes:** 77, 88, 99
- **Expected effect:** Higher (right-wing) → less redistribution support

**`trstprl`  - Trust in National Parliament**
- **ESS Question:** "On a scale of 0-10, how much do you trust your country's parliament?"
- **Scale:** 0 (No trust at all) to 10 (Complete trust)
- **Variable name:** `political_trust`
- **Centering:** Grand-mean centered → `political_trust_c`
- **Missing codes:** 77, 88, 99
- **Expected effect:** Higher trust → more redistribution support (confidence in government effectiveness)

**`dfincac`  - Perceived Meritocracy (Hard Work)**
- **ESS Question:** "Some people say that getting ahead depends on hard work and effort. Others say it depends on luck and connections. Where would you place yourself?"
- **Scale:** 1 (Hard work determines) to 5 (Luck/connections determine)
- **Variable name:** `merit_effort`
- **Missing codes:** 7, 8, 9
- **Expected effect:** Meritocratic beliefs → less redistribution support

**`smdfslv`  - Perceived Deservingness**
- **ESS Question:** "A person is deserving if they work hard, even if their efforts don't always succeed"
- **Scale:** 1 (Agree strongly) to 5 (Disagree strongly)
- **Variable name:** `merit_deserve`
- **Missing codes:** 7, 8, 9
- **Expected effect:** Desert-based beliefs → less redistribution support

---

## Country-Level Economic Indicators

**`gini`  - Gini Coefficient (Income Inequality)**
- **Source:** World Bank / OECD Income Distribution Database
- **Definition:** Gini coefficient of disposable income (post-tax, post-transfer)
- **Scale:** 0 (perfect equality) to 100 (perfect inequality)
- **Year:** 2018 (matching ESS Round 9)
- **Standardization:** Z-score → `gini_z`
- **Coverage:** All 28 ESS countries
- **Expected effect:** Higher inequality → more redistribution support (inequality breeds demand)
- **Alternative hypothesis:** Higher inequality → less redistribution support (power resources theory)

**`gdp_per_capita`  - GDP per Capita (PPP)**
- **Source:** World Bank / OECD National Accounts
- **Definition:** Gross Domestic Product per capita, purchasing power parity (constant 2017 international $)
- **Scale:** Continuous (USD, thousands)
- **Year:** 2018
- **Standardization:** Z-score → `gdp_per_capita_z`
- **Coverage:** All 28 ESS countries
- **Expected effect:** Higher GDP → less redistribution support (affluence reduces welfare demand)

**`unemployment_rate`  - Unemployment Rate**
- **Source:** World Bank / OECD Labour Force Statistics
- **Definition:** Unemployment as % of total labor force (ILO definition)
- **Scale:** Continuous (0-30%)
- **Year:** 2018
- **Standardization:** Z-score → `unemployment_rate_z`
- **Coverage:** All 28 ESS countries
- **Expected effect:** Higher unemployment → more redistribution support (economic insecurity)

---

## Institutional Variables

### Labor Market Institutions

**`epl_regular`  - Employment Protection Legislation (Regular Contracts)**
- **Source:** OECD Employment Protection Database
- **Definition:** Index of strictness of employment protection for regular (permanent) workers
- **Scale:** 0 (least restrictive) to 6 (most restrictive)
- **Year:** 2018
- **Standardization:** Z-score → `epl_regular_z`
- **Coverage:** OECD members only (21 of 28 countries)
- **Expected effect:** Higher EPL → less redistribution support (labor market protection substitutes for welfare)

**`epl_temporary`  - Employment Protection Legislation (Temporary Contracts)**
- **Source:** OECD Employment Protection Database
- **Definition:** Index of regulation of temporary work (fixed-term contracts, TWA)
- **Scale:** 0 (least restrictive) to 6 (most restrictive)
- **Year:** 2018
- **Standardization:** Z-score → `epl_temporary_z`
- **Coverage:** OECD members only
- **Expected effect:** Higher EPL temp → dualization effects (insiders vs outsiders)

**`almp_spending`  - Active Labor Market Policy Spending**
- **Source:** OECD Social Expenditure Database (SOCX)
- **Definition:** Public spending on active labor market programs (training, job creation, etc.) as % of GDP
- **Scale:** Continuous (0-2%)
- **Year:** 2018
- **Standardization:** Z-score → `almp_spending_z`
- **Coverage:** OECD members only
- **Expected effect:** Higher ALMP → more redistribution support (complementarity with welfare state)

**`union_density`  - Trade Union Density**
- **Source:** ICTWSS Database (Amsterdam Institute for Advanced Labour Studies)
- **Definition:** Net union membership as % of wage/salary earners in employment
- **Scale:** Continuous (0-100%)
- **Year:** 2018
- **Standardization:** Z-score → `union_density_z`
- **Coverage:** 27 of 28 countries (Iceland may have gaps)
- **Expected effect:** Higher density → more redistribution support (collective action capacity)

**`bargaining_coverage`  - Collective Bargaining Coverage**
- **Source:** ICTWSS Database
- **Definition:** Adjusted collective bargaining coverage (% of employees covered)
- **Scale:** Continuous (0-100%)
- **Year:** 2018
- **Standardization:** Z-score → `bargaining_coverage_z`
- **Coverage:** 27 of 28 countries
- **Expected effect:** Higher coverage → more redistribution support (coordinated wage-setting)

### Welfare State Spending

**`social_spending`  - Social Expenditure (% GDP)**
- **Source:** OECD Social Expenditure Database (SOCX)
- **Definition:** Total public social expenditure as % of GDP (old age, incapacity, health, family, unemployment, housing, other)
- **Scale:** Continuous (10-30%)
- **Year:** 2018
- **Standardization:** Z-score → `social_spending_z`
- **Coverage:** OECD members only
- **Expected effect:** Higher spending → path dependency (support for existing welfare state)

---

## AI/Automation Exposure Variables

**`ai_exposure_oecd`  - AI Occupational Exposure (Felten AIOE)**
- **Source:** Felten, Raj & Seamans (2021), aggregated via `scripts/aggregate_aioe.py`
- **Definition:** Country-level AIOE score based on occupational task overlap with AI capabilities, weighted by Eurostat LFS 2018 employment shares
- **Scale:** Continuous (standardized)
- **Year:** 2018 employment structure
- **Standardization:** Z-score → `ai_exposure_oecd_z`
- **Coverage:** All 28 ESS Round 9 countries
- **Empirical result:** No significant effect on redistribution preferences (p = 0.857)
- **Note:** Column name retained for pipeline compatibility. Positive values = higher cognitive/professional AI exposure. Service economies (GB, CH, NO) score highest.

**`automation_risk`  - Frey & Osborne Automation Risk**
- **Source:** Frey & Osborne (2017) probabilities aggregated via Eurostat LFS
- **Definition:** Weighted average of occupation-level automation probabilities, weighted by country employment shares
- **Scale:** Continuous (0-1, often expressed as %)
- **Year:** 2018 employment structure
- **Standardization:** Z-score → `automation_risk_z`
- **Coverage:** Not yet computed  - column contains NaN placeholder values
- **Status:** Placeholder for future extension
- **Calculation:**
  ```
  automation_risk_c = Σ(P(automation)_occ × employment_share_occ)
  ```

**`ai_exposure_felten`  - Felten et al. AI Exposure Index (Optional)**
- **Source:** Felten, Raj & Seamans (2021) aggregated to country level
- **Definition:** AI exposure based on detailed task-technology mapping
- **Scale:** Continuous (standardized)
- **Year:** 2018
- **Standardization:** Z-score → `ai_exposure_felten_z`
- **Coverage:** Varies
- **Tested effect:** No significant direct effect on redistribution preferences (coef = -0.014, p = 0.857). AI exposure enters the theoretical model as an indirect channel through inequality, not as a direct predictor.

### Composite Measures

**`social_exposure`  - Social Exposure to AI/Automation**
- **Definition:** Interaction of technical AI exposure × institutional weakness
- **Formula:**
  ```
  social_exposure = ai_exposure_oecd_z × (1 / union_density_z) × (1 / social_spending_z)
  ```
- **Interpretation:** High AI exposure + weak labor market institutions + low welfare spending = high social exposure
- **Expected effect:** Higher social exposure → more redistribution support (vulnerability hypothesis)

---

## Derived Variables

### Meritocracy Index

**`meritocracy_index`  - Composite Meritocratic Beliefs**
- **Formula:** `(merit_effort + merit_deserve) / 2`
- **Components:**
  - `merit_effort` (dfincac): Hard work determines success
  - `merit_deserve` (smdfslv): Deservingness based on effort
- **Scale:** 1 (low meritocratic beliefs) to 5 (high meritocratic beliefs)
- **Centering:** Grand-mean centered → `meritocracy_index_c`
- **Missing:** If either component is missing, index is missing
- **Expected effect:** Higher meritocracy → less redistribution support

### Centered Variables (Level-1)

All Level-1 continuous variables are **grand-mean centered**:

- `income_c` = `income` - mean(`income`)
- `education_c` = `education` - mean(`education`)
- `age_c` = `age` - mean(`age`)
- `ideology_c` = `ideology` - mean(`ideology`)
- `political_trust_c` = `political_trust` - mean(`political_trust`)
- `meritocracy_index_c` = `meritocracy_index` - mean(`meritocracy_index`)

**Rationale:** Grand-mean centering allows random intercepts to represent the average country's redistribution support at the mean of all predictors, facilitating interpretation.

### Standardized Variables (Level-2)

All Level-2 continuous variables are **z-score standardized**:

- `gini_z` = (`gini` - mean) / SD
- `gdp_per_capita_z` = (`gdp_per_capita` - mean) / SD
- `unemployment_rate_z` = (`unemployment_rate` - mean) / SD
- `epl_regular_z` = (`epl_regular` - mean) / SD
- `union_density_z` = (`union_density` - mean) / SD
- `social_spending_z` = (`social_spending` - mean) / SD
- `ai_exposure_oecd_z` = (`ai_exposure_oecd` - mean) / SD

**Rationale:** Standardization puts all country-level predictors on the same scale (mean = 0, SD = 1), allowing direct comparison of effect sizes.

---

## Welfare Regime Classifications

### Esping-Andersen Typology (5 Regimes)

**Variable:** `regime_esping`

**Classification:**

1. **Social Democratic** (Nordic)
   - Countries: Denmark (DK), Finland (FI), Norway (NO), Sweden (SE)
   - Characteristics: Universal benefits, high decommodification, high social spending
   - Expected redistribution support: High

2. **Conservative/Corporatist** (Continental)
   - Countries: Austria (AT), Belgium (BE), France (FR), Germany (DE), Netherlands (NL), Switzerland (CH)
   - Characteristics: Social insurance, contribution-based, status preservation
   - Expected redistribution support: Medium-High

3. **Liberal** (Anglo-Saxon)
   - Countries: Ireland (IE), United Kingdom (GB)
   - Characteristics: Means-tested benefits, market-oriented, residual welfare
   - Expected redistribution support: Medium

4. **Southern European** (Mediterranean)
   - Countries: Cyprus (CY), Italy (IT), Portugal (PT), Spain (ES)
   - Characteristics: Family-based welfare, fragmented coverage, labor market dualism
   - Expected redistribution support: Medium-High (due to inequality)

5. **Post-Communist** (Eastern)
   - Countries: Bulgaria (BG), Croatia (HR), Czech Republic (CZ), Estonia (EE), Hungary (HU), Latvia (LV), Lithuania (LT), Montenegro (ME), Poland (PL), Serbia (RS), Slovenia (SI)
   - Characteristics: Transition economies, hybrid systems, varying decommodification
   - Expected redistribution support: Variable (economic insecurity vs. transition fatigue)

**Source:** Esping-Andersen (1990, 1999); Arts & Gelissen (2002)

### Varieties of Capitalism (4 Types)

**Variable:** `regime_voc`

**Classification:**

1. **Coordinated Market Economies (CME)**
   - Countries: Austria, Belgium, Germany, Netherlands, Norway, Sweden, Switzerland
   - Characteristics: Strategic coordination, patient capital, strong labor institutions
   - Expected redistribution support: Medium-High (institutional complementarity)

2. **Liberal Market Economies (LME)**
   - Countries: Ireland, United Kingdom
   - Characteristics: Market coordination, short-term capital, flexible labor markets
   - Expected redistribution support: Medium-Low

3. **Mixed Market Economies (MME)**
   - Countries: France, Italy, Portugal, Spain, Cyprus
   - Characteristics: Mix of state intervention and market coordination
   - Expected redistribution support: Medium-High

4. **Dependent Market Economies (DME)**
   - Countries: Bulgaria, Croatia, Czech Republic, Estonia, Hungary, Latvia, Lithuania, Montenegro, Poland, Serbia, Slovenia
   - Characteristics: Foreign capital dependence, hierarchical coordination
   - Expected redistribution support: Variable

**Note:** Denmark, Finland not classified in original Hall & Soskice (2001); added to CME following Nölke & Vliegenthart (2009)

**Source:** Hall & Soskice (2001); Nölke & Vliegenthart (2009)

---

## Missing Data Codes

### ESS Missing Value Conventions

- **Refusal:** 7 (single-digit variables), 77 (two-digit), 777 (three-digit)
- **Don't know:** 8, 88, 888
- **No answer:** 9, 99, 999
- **Not applicable:** 6, 66, 666 (varies by question)

### Handling Strategy

1. **Individual-level variables:**
   - Convert ESS missing codes (7-9, 77-99, etc.) to `NaN`
   - Listwise deletion at model estimation (multilevel models require complete data)
   - Report missing % in descriptive statistics

2. **Country-level variables:**
   - Non-OECD countries systematically missing on OECD indicators
   - Use multiple imputation OR restrict analyses to OECD subsample
   - Document missingness patterns in tables

3. **Institutional variables:**
   - Missing for: Bulgaria (BG), Cyprus (CY), Croatia (HR), Montenegro (ME), Serbia (RS)
   - Strategy: Create "Data available" flag, conduct sensitivity analyses

4. **AI exposure variables:**
   - Most labor-intensive to construct
   - If missing, either: (a) Impute using occupation structure, (b) Restrict to available countries, (c) Use proxy measures

### Expected Missingness Rates

- **ESS individual variables:** ~5% (typical survey non-response)
- **Income (hinctnta):** ~10-15% (sensitive question)
- **Ideology (lrscale):** ~5-8% (political alienation)
- **Country-level economic:** 0% (all available from World Bank)
- **Institutional (OECD):** 25% (7/28 countries non-OECD)
- **AI exposure:** Varies (10-40% depending on source)

---

## Variable Summary Table

| Variable Type | N Variables | Centering/Scaling | Missingness | Source |
|--------------|-------------|-------------------|-------------|--------|
| **Outcome** | 1 | Reversed (1-5) | ~5% | ESS R9 |
| **Level-1 Predictors** | 9 | Grand-mean centered | 5-15% | ESS R9 |
| **Level-2 Economic** | 3 | Z-score standardized | 0% | World Bank/OECD |
| **Level-2 Institutional** | 6 | Z-score standardized | 0-25% | OECD/ICTWSS |
| **Level-2 AI Exposure** | 2-3 | Z-score standardized | 10-40% | OECD/Frey & Osborne |
| **Regime Classifications** | 2 | Categorical | 0% | Typology assignment |
| **Derived Composites** | 2 | Varies | Inherited | Calculated |

---

## References

**ESS Documentation:**
- ESS Round 9 Integrated File, Edition 3.1 (2023)
- ESS Round 9 Data Documentation Report, Edition 3.1 (2023)
- European Social Survey website: https://ess.sitehost.iu.edu/

**OECD Data:**
- OECD Employment Protection Database: https://www.oecd.org/employment/emp/oecdindicatorsofemploymentprotection.htm
- OECD Social Expenditure Database (SOCX): https://www.oecd.org/social/expenditure.htm
- OECD Employment Outlook 2023: https://www.oecd.org/employment/outlook/

**ICTWSS:**
- Visser, J. (2021). ICTWSS Database version 6.1. Amsterdam Institute for Advanced Labour Studies (AIAS), University of Amsterdam.

**AI/Automation:**
- Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? *Technological Forecasting and Social Change*, 114, 254-280.
- Felten, E., Raj, M., & Seamans, R. (2021). Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses. *Strategic Management Journal*, 42(12), 2195-2217.

**Welfare Regimes:**
- Esping-Andersen, G. (1990). *The Three Worlds of Welfare Capitalism*. Princeton University Press.
- Arts, W., & Gelissen, J. (2002). Three worlds of welfare capitalism or more? *Journal of European Social Policy*, 12(2), 137-158.
- Hall, P. A., & Soskice, D. (2001). *Varieties of Capitalism*. Oxford University Press.
- Nölke, A., & Vliegenthart, A. (2009). Enlarging the varieties of capitalism. *World Politics*, 61(4), 670-702.

---

**Last Updated:** March 2026
**Version:** 1.1
**Project:** ESS Redistribution and Trust Analysis
**Contact:** Kaleb Mazurek
