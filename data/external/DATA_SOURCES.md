# Data Sources and Acquisition Instructions

This document provides detailed instructions for obtaining all data required for the ESS redistribution analysis.

---

## 1. European Social Survey (ESS) Round 9

**What:** Individual-level survey data on attitudes, beliefs, and behavior patterns

**Year:** 2018

**Sample:** ~50,000 respondents across 29 countries (we use 28, excluding Slovakia)

### How to Obtain

1. **Visit:** https://ess.sitehost.iu.edu/
2. **Register:** Create free account (required for data download)
3. **Navigate to:** Data > Data and Documentation by Year/Round > Round 9 (2018)
4. **Download:** Integrated file (all countries combined)
   - File: `ESS9e03_3.dta` (Stata format, recommended)
   - Alternative: `ESS9e03_3.sav` (SPSS format)
5. **Save to:** `data/raw/ESS9e03_3.dta`

**Citation:**
```
ESS Round 9: European Social Survey Round 9 Data (2018). Data file edition 3.1.
Sikt - Norwegian Agency for Shared Services in Education and Research, Norway -
Data Archive and distributor of ESS data for ESS ERIC. doi:10.21338/NSD-ESS9-2018.
```

**Variables Used:**
- See `docs/VARIABLE_CODEBOOK.md` for complete list
- Core variables: gincdif, hinctnta, trstprl, cntry, agea, gndr, eduyrs, fairelc, dscrgrp

---

## 2. OECD Economic Indicators (2018)

### 2a. Gini Coefficient (Income Inequality)

**Source:** OECD Income Distribution Database

**What:** Gini coefficient of disposable income (after taxes and transfers)

**Scale:** 0-100 (higher = more inequality)

#### Option 1: Manual Download via OECD.Stat

1. Visit: https://stats.oecd.org/Index.aspx?DataSetCode=IDD
2. Select:
   - Measure: "Gini (disposable income, post taxes and transfers)"
   - Countries: All available (AT, BE, CZ, DE, DK, EE, ES, FI, FR, GB, HR, HU, IE, IS, IT, LT, LV, NL, NO, PL, PT, SE, SI, CH)
   - Year: 2018 (or nearest available: 2017 for some countries)
3. Export to CSV
4. Save as: `data/external/gini_data.csv`

**Expected CSV Format:**
```csv
country,year,gini
AT,2018,29.4
BE,2018,27.2
BG,2018,39.6
...
```

#### Option 2: OECD API (Python)

```python
import requests
import pandas as pd

url = "https://stats.oecd.org/SDMX-JSON/data/IDD/AUT+BEL+BGR+CZE+DNK.GINI.INCOMES.../all"
response = requests.get(url)
# Parse JSON and extract data
# See OECD SDMX JSON documentation for details
```

### 2b. GDP per Capita (PPP)

**Source:** OECD National Accounts

**What:** Gross Domestic Product per capita, PPP adjusted (constant international $)

#### Manual Download

1. Visit: https://data.oecd.org/gdp/gross-domestic-product-gdp.htm
2. Select:
   - Measure: "GDP per capita, PPP"
   - Countries: All ESS Round 9 countries
   - Year: 2018
3. Export to CSV
4. Save as: `data/external/gdp_data.csv`

**Expected CSV Format:**
```csv
country,year,gdp
AT,2018,53267
BE,2018,49532
BG,2018,22453
...
```

### 2c. Unemployment Rate

**Source:** OECD Employment Database

**What:** Harmonized unemployment rate (% of labor force)

#### Manual Download

1. Visit: https://data.oecd.org/unemp/unemployment-rate.htm
2. Select:
   - Countries: All ESS countries
   - Year: 2018
3. Export to CSV
4. Save as: `data/external/unemployment_data.csv`

**Expected CSV Format:**
```csv
country,year,unemployment
AT,2018,4.9
BE,2018,6.0
BG,2018,5.2
...
```

**Note:** For non-OECD countries (BG, HR, CY, ME, RS), use Eurostat or ILO data

---

## 3. Institutional Indicators

### 3a. Employment Protection Legislation (EPL) Strictness

**Source:** OECD Employment Protection Database

**What:** Index of strictness of employment protection legislation for regular contracts

**Scale:** 0-6 (higher = stricter protection)

**Year:** 2018 (or 2019 if 2018 unavailable)

#### How to Obtain

1. Visit: https://www.oecd.org/employment/emp/oecdindicatorsofemploymentprotection.htm
2. Navigate to: "Download data" section
3. Download: Excel file with EPL indicators
4. Extract: Variable `EPRC_V4` (EPL for regular contracts, version 4)
5. Compile into CSV with format below

**Expected CSV Column:** `epl` (values 0-6)

### 3b. Active Labor Market Policy (ALMP) Spending

**Source:** OECD Social Expenditure Database (SOCX)

**What:** Public spending on active labor market programmes as % of GDP

**Year:** 2018

#### How to Obtain

1. Visit: https://www.oecd.org/social/expenditure.htm
2. Navigate to: SOCX database query tool
3. Select:
   - Programme: "Active labour market programmes (Category 2-7)"
   - Countries: All available
   - Year: 2018
4. Export spending as % of GDP
5. Save values to CSV

**Expected CSV Column:** `almp_spending` (values 0-3, typically 0.1-1.5%)

### 3c. Union Density

**Source:** ICTWSS Database (Institutional Characteristics of Trade Unions, Wage Setting, State Intervention and Social Pacts)

**What:** Trade union density rate (% of wage/salary earners who are union members)

**Year:** 2018

#### How to Obtain

1. Visit: https://www.ictwss.org/downloads
2. Download: ICTWSS database (Version 6.1 or latest)
3. Extract: Variable `UD` (Union Density)
4. Filter to year 2018
5. Save values to CSV

**Expected CSV Column:** `union_density` (values 0-100, typically 5-80%)

### 3d. Social Spending

**Source:** OECD SOCX

**What:** Total public social expenditure as % of GDP

**Year:** 2018

#### How to Obtain

1. Visit: https://data.oecd.org/socialexp/social-spending.htm
2. Select:
   - Measure: "Public, % of GDP"
   - Countries: All ESS countries
   - Year: 2018
3. Export to CSV
4. Save values to CSV

**Expected CSV Column:** `social_spending` (values 0-35, typically 15-30%)

### 3e. Collective Bargaining Coverage

**Source:** ICTWSS Database

**What:** Adjusted collective bargaining coverage (% of employees covered by collective agreements)

**Year:** 2018

#### How to Obtain

1. From ICTWSS database (same as 3c)
2. Extract: Variable `AdjCov` (Adjusted coverage rate)
3. Save values to CSV

**Expected CSV Column:** `collective_bargaining` (values 0-100, typically 10-99%)

### Complete Institutional Data CSV Format

Save all institutional indicators in: `data/external/institutional_data.csv`

```csv
country,epl,almp_spending,union_density,social_spending,collective_bargaining
AT,2.35,0.51,26.8,26.9,98
BE,2.54,1.12,50.3,29.0,96
BG,NA,NA,18.8,NA,NA
CH,1.77,0.45,15.8,16.7,49
CY,NA,NA,50.3,NA,NA
CZ,2.85,0.22,12.0,19.2,47
DE,2.84,0.51,16.5,25.1,56
DK,2.32,1.63,67.2,28.3,84
EE,2.39,0.18,4.5,17.7,20
ES,2.47,0.53,13.6,24.7,78
FI,2.17,0.86,60.3,29.1,89
FR,2.82,0.98,10.8,31.2,98
GB,1.17,0.20,23.4,20.6,26
HR,2.57,0.08,24.6,NA,NA
HU,1.92,0.42,8.2,18.1,23
IE,1.50,0.43,24.8,13.4,44
IS,NA,0.39,90.4,NA,NA
IT,2.68,0.44,34.4,28.2,80
LT,2.47,0.10,7.7,16.2,7
LV,2.47,0.23,12.6,16.2,14
ME,NA,NA,NA,NA,NA
NL,2.94,1.01,16.4,16.7,79
NO,2.33,0.37,50.4,25.3,67
PL,2.21,0.33,12.7,21.3,15
PT,3.01,0.51,15.6,23.8,73
RS,NA,NA,25.4,NA,NA
SE,2.52,1.16,66.1,26.1,90
SI,2.76,0.22,21.5,21.2,65
```

**Notes:**
- NA indicates data not available (typical for non-OECD countries: BG, CY, HR, IS, ME, RS)
- Some values are from nearest available year (2017 or 2019)
- Code handles missing values gracefully (see `src/data_loader.py`)

---

## 4. AI/Automation Exposure Indicators

### 4a. OECD AI Exposure Index

**Source:** OECD Employment Outlook 2023, Chapter 3

**What:** Country-level AI exposure based on occupational composition and task content

**Year:** Latest available (2020-2022)

#### How to Obtain

1. Visit: https://www.oecd.org/employment/outlook/
2. Download: OECD Employment Outlook 2023
3. Navigate to: Chapter 3 on AI and employment
4. Extract: Country-level AI exposure index from tables/supplementary data
5. Alternative: Contact OECD for dataset access

**Expected CSV Column:** `ai_exposure_oecd` (standardized index, mean=0, sd=1)

### 4b. Frey & Osborne Automation Risk (Country Aggregated)

**Source:** Frey & Osborne (2017) occupation-level probabilities + Eurostat Labor Force Survey

**What:** Weighted average of automation probabilities by country employment composition

**Year:** 2018 employment composition

#### How to Obtain

**Step 1: Get Frey & Osborne probabilities**

1. Citation: Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? *Technological Forecasting and Social Change*, 114, 254-280.
2. Data: Available in paper's online appendix or from https://www.oxfordmartin.ox.ac.uk/downloads/academic/The_Future_of_Employment.pdf
3. Contains: Automation probability for 702 US occupations

**Step 2: Get country employment composition**

1. Visit: Eurostat Labor Force Survey
2. Download: Employment by occupation (ISCO-08) for each ESS country, year 2018
3. URL: https://ec.europa.eu/eurostat/web/lfs/data/database

**Step 3: Aggregate to country level**

```python
# Pseudocode
for country in ESS_countries:
    employment_shares = get_occupation_shares(country, year=2018)
    automation_probs = get_frey_osborne_probs()
    country_automation_risk = weighted_average(automation_probs, weights=employment_shares)
```

**Expected CSV Column:** `automation_risk` (values 0-1, typically 0.4-0.6)

### 4c. Felten, Raj & Seamans AI Exposure Index

**Source:** Felten et al. (2021)

**What:** AI exposure by occupation based on AI progress in specific abilities

**Year:** 2018

#### How to Obtain

1. Citation: Felten, E., Raj, M., & Seamans, R. (2021). Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses. *Strategic Management Journal*, 42(12), 2195-2217.
2. Data: Available from authors' websites or Harvard Dataverse
3. Aggregate to country level using same method as 4b (employment composition weights)

**Expected CSV Column:** `ai_exposure_felten` (standardized index)

### 4d. Social Exposure Composite (Conceptual Contribution)

**What:** Composite measure combining technical AI exposure with institutional weakness

**Construction:**

```
social_exposure = ai_exposure_technical × institutional_weakness

Where:
  ai_exposure_technical = OECD AI exposure index (or Frey & Osborne)
  institutional_weakness = inverted composite of (EPL + ALMP + social_spending)
```

**This is created in the analysis code** (see `src/data_prep.py`)

### Complete AI Exposure CSV Format

Save all AI indicators in: `data/external/ai_exposure_data.csv`

```csv
country,ai_exposure_oecd,automation_risk,ai_exposure_felten,social_exposure
AT,0.12,0.48,0.34,NA
BE,-0.05,0.45,0.29,NA
BG,NA,0.55,NA,NA
CH,0.08,0.47,0.32,NA
CY,NA,NA,NA,NA
CZ,0.25,0.52,0.40,NA
DE,0.18,0.50,0.36,NA
DK,-0.15,0.43,0.25,NA
EE,0.30,0.53,0.42,NA
ES,0.10,0.49,0.35,NA
FI,-0.12,0.44,0.27,NA
FR,0.05,0.47,0.31,NA
GB,0.02,0.46,0.30,NA
HR,NA,0.51,NA,NA
HU,0.35,0.54,0.44,NA
IE,-0.08,0.45,0.28,NA
IS,NA,NA,NA,NA
IT,0.15,0.49,0.35,NA
LT,0.28,0.52,0.41,NA
LV,0.32,0.53,0.42,NA
ME,NA,NA,NA,NA
NL,-0.10,0.44,0.26,NA
NO,-0.18,0.42,0.24,NA
PL,0.38,0.55,0.45,NA
PT,0.20,0.50,0.37,NA
RS,NA,NA,NA,NA
SE,-0.20,0.41,0.23,NA
SI,0.22,0.51,0.38,NA
```

**Notes:**
- `social_exposure` column initially NA, will be calculated in analysis
- AI exposure values are approximate/illustrative — actual data must be obtained from sources
- OECD index is standardized (mean≈0, sd≈1)
- Automation risk is probability scale (0-1)

---

## 5. Alternative Data Sources

### World Bank API (for basic economic indicators)

If OECD data is unavailable for non-OECD countries, use World Bank:

**Python Example:**
```python
import wbdata

# Gini coefficient
gini_data = wbdata.get_dataframe({"SI.POV.GINI": "gini"}, country="all")

# GDP per capita (PPP)
gdp_data = wbdata.get_dataframe({"NY.GDP.PCAP.PP.CD": "gdp_ppp"}, country="all")

# Unemployment
unemp_data = wbdata.get_dataframe({"SL.UEM.TOTL.ZS": "unemployment"}, country="all")
```

**Indicator Codes:**
- Gini: `SI.POV.GINI`
- GDP per capita PPP: `NY.GDP.PCAP.PP.CD`
- Unemployment: `SL.UEM.TOTL.ZS`

---

## 6. Optional: ESS Rounds 10 & 11 (For Robustness Checks)

### ESS Round 10 (2020)

**Coverage:** COVID period
**Use:** Robustness check, pre/post COVID comparison

Download from: https://ess.sitehost.iu.edu/ (same process as Round 9)

### ESS Round 11 (2022-2023)

**Coverage:** Post-COVID period
**Use:** Temporal trends analysis

Download from: https://ess.sitehost.iu.edu/ (same process as Round 9)

---

## Data Quality Notes

### Expected Data Availability

| Data Type | OECD Members | EU Non-OECD | Non-EU |
|-----------|--------------|-------------|--------|
| ESS | ✓ | ✓ | ✓ |
| Gini, GDP, Unemployment | ✓ | Partial (Eurostat) | Limited |
| EPL, ALMP | ✓ | Limited | ✗ |
| ICTWSS | ✓ | ✓ | Partial |
| AI Exposure | ✓ | Limited | ✗ |

**Countries with likely missing institutional/AI data:**
- BG (Bulgaria) — EU but recent OECD accession
- CY (Cyprus) — EU, limited OECD data
- HR (Croatia) — EU, recent OECD accession
- IS (Iceland) — OECD but small, some data gaps
- ME (Montenegro) — Non-EU, non-OECD
- RS (Serbia) — Non-EU, non-OECD

**Mitigation:** Code handles missing data gracefully; extension analyses can focus on subset with complete institutional data (~20 countries)

---

## Citations

### Data Sources

```bibtex
@misc{ess2018,
  title={European Social Survey Round 9 Data},
  author={{ESS ERIC}},
  year={2018},
  publisher={Sikt - Norwegian Agency for Shared Services in Education and Research},
  doi={10.21338/NSD-ESS9-2018}
}

@misc{oecd_idd,
  title={Income Distribution Database},
  author={{OECD}},
  year={2023},
  url={https://www.oecd.org/social/income-distribution-database.htm}
}

@misc{ictwss,
  title={Institutional Characteristics of Trade Unions, Wage Setting, State Intervention and Social Pacts (ICTWSS) database},
  author={Visser, Jelle},
  year={2021},
  version={6.1},
  url={https://www.ictwss.org/}
}

@article{frey2017future,
  title={The future of employment: How susceptible are jobs to computerisation?},
  author={Frey, Carl Benedikt and Osborne, Michael A},
  journal={Technological Forecasting and Social Change},
  volume={114},
  pages={254--280},
  year={2017}
}

@article{felten2021occupational,
  title={Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses},
  author={Felten, Edward and Raj, Manav and Seamans, Robert},
  journal={Strategic Management Journal},
  volume={42},
  number={12},
  pages={2195--2217},
  year={2021}
}
```

---

## Contact for Data Issues

If you encounter issues obtaining data:

1. **ESS:** Contact ESS Data Archive (data@europeansocialsurvey.org)
2. **OECD:** OECD.Stat support (https://stats.oecd.org/contacts/)
3. **ICTWSS:** Jelle Visser (j.visser@uva.nl)
4. **AI Exposure:** Edward Felten (felten@cs.princeton.edu) or OECD Employment team

---

**Last Updated:** March 2026
