# Data Sources and Provenance

All data files used in this project, their sources, and verification status.

---

## Individual-Level Data

### ESS Round 9 (2018)
- **File**: `data/raw/ESS9e03_3.dta`
- **Source**: European Social Survey, edition 3.3
- **URL**: https://ess.sitehost.iu.edu/
- **Format**: Stata (.dta), loaded via pyreadstat
- **Coverage**: 28 countries (Slovakia excluded), ~47,000 respondents before filtering
- **Key variables**: gincdif (redistribution), hinctnta (income decile), trstprl
  (political trust), sofrwrk/ppldsrv (meritocracy), agea, gndr, eduyrs
- **License**: ESS data are freely available for non-commercial use after registration
- **Not included in repository** due to license restrictions. Users must download directly.

---

## Country-Level Economic Data

All three files below were fetched from the **World Bank Open Data API** using
`scripts/fetch_oecd_data.py` (the OECD API section is a stub; the functional
portion uses `wbdata` for World Bank indicators). Year = 2018.

Format for all three: `country,year,value` (ISO-2 country codes).

### Gini Coefficient
- **File**: `data/external/gini_data.csv`
- **Indicator**: SI.POV.GINI (World Bank)
- **Description**: Gini index of disposable income inequality (0-100 scale)
- **Verified**: Spot-checked against World Bank data portal. Values match
  published figures (e.g., CZ = 25.0, BG = 40.4).
- **Coverage**: 23 of 28 countries. Missing: CH, IS, ME, RS, and GB (World Bank
  does not publish Gini for these via this indicator).

### GDP per Capita
- **File**: `data/external/gdp_data.csv`
- **Indicator**: NY.GDP.PCAP.PP.CD (World Bank)
- **Description**: GDP per capita, PPP (current international $)
- **Verified**: Values match World Bank portal with float precision (e.g.,
  NO = 65,662.33). Minor revisions possible due to PPP rebasing.
- **Coverage**: 28 of 28 countries.

### Unemployment Rate
- **File**: `data/external/unemployment_data.csv`
- **Indicator**: SL.UEM.TOTL.ZS (World Bank)
- **Description**: Unemployment rate, ILO estimate (% of total labor force)
- **Verified**: Spot-checked against World Bank portal (e.g., ES = 15.254,
  CZ = 2.237). All values match to 3 decimal places.
- **Coverage**: 28 of 28 countries.

---

## Institutional Data

### OECD/ICTWSS Institutional Indicators
- **File**: `data/external/institutional_data.csv`
- **Format**: `country,epl,almp_spending,union_density,social_spending,collective_bargaining`
- **Sources**:
  - EPL (Employment Protection Legislation): OECD Indicators of Employment
    Protection, regular contracts, version 2018
  - ALMP spending: OECD Social Expenditure Database (SOCX), % of GDP
  - Union density: ICTWSS Database (Visser), % of employees
  - Social spending: OECD SOCX, total public social expenditure as % of GDP
  - Collective bargaining coverage: ICTWSS Database
- **Verified**: Spot-checked against published values. EPL values match OECD
  online (e.g., DE = 2.12, NL = 2.82). Union density matches ICTWSS (e.g.,
  SE = 65.6, FR = 10.8).
- **Coverage**: 20-23 countries depending on indicator. Non-OECD countries
  (RS, ME, BG, HR) have limited or no coverage.
- **Limitation**: Some indicators may reflect nearest available year (2017-2019)
  rather than exact 2018 values.

---

## AI Exposure Data

### Felten, Raj & Seamans (2021) AIOE
- **File**: `data/external/ai_exposure_data.csv`
- **Format**: `country,ai_exposure_oecd,automation_risk,ai_exposure_felten,social_exposure`
- **Aggregation script**: `scripts/aggregate_aioe.py`
- **Methodology**:
  1. Occupation-level AIOE scores from Felten et al. (2021) at SOC 6-digit
     level (774 occupations), averaged to SOC 2-digit major groups
  2. SOC 2-digit mapped to ISCO-08 1-digit via standard BLS/ILO crosswalk
     (where a SOC group spans two ISCO groups, weight is split 50/50)
  3. Country-level scores computed as employment-weighted averages using
     Eurostat Labour Force Survey (table lfsa_egais, 2018, sex=total, age=15-64)
- **Raw data**:
  - `data/external/raw/AIOE_DataAppendix.xlsx` -- downloaded from
    https://github.com/AIOE-Data/AIOE (Felten et al. Appendix A)
  - `data/external/raw/eurostat_employment_isco08_2018.csv` -- fetched from
    Eurostat JSON API, cached locally
- **Column notes**:
  - `ai_exposure_felten`: The computed country-level AIOE score
  - `ai_exposure_oecd`: Same as ai_exposure_felten (mapped for pipeline
    compatibility with src/models.py which references this column name)
  - `automation_risk`: Placeholder (NaN) -- Frey & Osborne scores not yet added
  - `social_exposure`: Placeholder (NaN) -- computed in notebook 05 as
    AI exposure x institutional weakness
- **Coverage**: 28 of 28 countries (all ESS Round 9 countries)
- **Citation**: Felten E, Raj M, Seamans R (2021). Occupational, industry, and
  geographic exposure to artificial intelligence: A novel dataset and its
  potential uses. *Strategic Management Journal* 42(12):2195-2217.

---

## Reproduction

To regenerate data files from source:

```bash
# Economic data (World Bank API)
python scripts/fetch_oecd_data.py

# AI exposure scores (requires AIOE_DataAppendix.xlsx in data/external/raw/)
python scripts/aggregate_aioe.py
```

ESS microdata and institutional data must be obtained manually from their
respective sources (see URLs above).

---

## Known Gaps

- **Gini**: Missing for 5 countries (CH, IS, ME, RS, GB). Analysis uses
  listwise deletion, reducing country count in models using Gini.
- **Institutional data**: Non-OECD countries lack EPL, ALMP, and social
  spending data. Welfare regime models (notebook 04) are limited to ~20 countries.
- **Automation risk**: Frey & Osborne (2017) country-level scores are not yet
  computed. The `automation_risk` column contains NaN values.
- **OECD API**: The OECD portion of `fetch_oecd_data.py` is a stub (returns
  None). Economic data comes from World Bank despite the script name.
