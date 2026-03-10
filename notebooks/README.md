# Notebooks

Run in order. Each notebook depends on outputs from previous ones.

| # | Notebook | Purpose |
|---|----------|---------|
| 01 | Data exploration | Descriptive statistics, distributions, missing data |
| 02 | Data preparation | Merge, transform, center/standardize, export |
| 03 | Replication analysis | 7-model multilevel sequence for redistribution |
| 04 | Welfare regime extension | Regime comparisons (descriptive) |
| 05 | AI exposure extension | AI exposure models (M14-M16, all null) |
| 06 | Dual-domain comparison | Trust vs redistribution: ICC, interactions, simulations |

Notebooks 01-03 give the core redistribution analysis. Notebook 05 tests
AI exposure (null finding). Notebook 06 compares redistribution with
institutional trust and runs simulations for both.

The trust models and simulations can also be run independently via
`scripts/trust_model_analysis.py`.

## Requirements

- Python 3.8+ with statsmodels, pandas, numpy, matplotlib, seaborn
- ESS Round 9 data in `data/raw/ESS9e03_3.dta`
- Country-level data in `data/external/`

## Notes

- All models use statsmodels MixedLM with REML estimation
- Level-1 variables are grand-mean centered, Level-2 are z-scored
- Complete cases: 31,393 (redistribution) and 31,033 (trust) in 25-26 countries
