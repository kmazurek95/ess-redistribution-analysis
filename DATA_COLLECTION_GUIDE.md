# Data Collection Guide

## Required Data

| Data | Source | Collection | Output File |
|------|--------|-----------|-------------|
| ESS Round 9 | ess.sitehost.iu.edu | Manual download (requires free account) | `data/raw/ESS9e03_3.dta` |
| Gini, GDP, Unemployment | World Bank API | `python scripts/fetch_oecd_data.py` | `data/external/{gini,gdp,unemployment}_data.csv` |
| EPL, ALMP, Social spending | OECD.Stat | Manual download from stats.oecd.org | `data/external/institutional_data.csv` |
| Union density, Bargaining | ICTWSS v6.1 | Manual download from ictwss.org | Merged into `institutional_data.csv` |
| AI exposure (Felten AIOE) | Felten et al. (2021) | `python scripts/aggregate_aioe.py` | `data/external/ai_exposure_data.csv` |

## Quick Start

1. Download ESS Round 9 Stata file, place in `data/raw/`
2. Run `python scripts/fetch_oecd_data.py` for economic indicators
3. Run notebooks in order: 01 through 05

Notebooks 01-03 (core analysis) need only ESS + economic indicators. Notebooks 04-05 need institutional and AI exposure data.

## Coverage Gaps

OECD institutional data covers 21 of 28 countries. Missing: BG, CY, HR, IS, ME, RS, and partially others. Non-OECD countries are handled through subsample analysis.

AI exposure data (Felten AIOE) covers all 28 countries after aggregation via Eurostat LFS employment weights. See `scripts/aggregate_aioe.py`.

## File Structure

```
data/
  raw/
    ESS9e03_3.dta
  external/
    gini_data.csv
    gdp_data.csv
    unemployment_data.csv
    institutional_data.csv
    ai_exposure_data.csv
    raw/AIOE_DataAppendix.xlsx
    raw/eurostat_employment_isco08_2018.csv
```
