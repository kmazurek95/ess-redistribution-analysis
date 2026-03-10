# Notebooks

Run in order. Each notebook depends on outputs from previous ones.

| # | Notebook | What it does |
|---|----------|-------------|
| 01 | `01_data_exploration.ipynb` | Descriptive statistics, distributions, missing data patterns |
| 02 | `02_data_preparation_clean.ipynb` | Clean/merge/transform data into analysis-ready format |
| 03 | `03_replication_analysis.ipynb` | 7-model multilevel sequence (null through cross-level interactions) |
| 04 | `04_welfare_regime_extension.ipynb` | Regime comparisons and institutional mediation (descriptive) |
| 05 | `05_ai_exposure_extension.ipynb` | AI exposure models (M14-M16, all null results) |
| 06 | `06_final_report.ipynb` | Synthesis of findings |

## Requirements

- `pip install -r requirements.txt`
- ESS Round 9 data in `data/raw/ESS9e03_3.dta` (download from ess.sitehost.iu.edu)
- Country-level data in `data/external/` (see `DATA_COLLECTION_GUIDE.md`)

## Minimum viable run

Notebooks 01-03 give you the core 7-model replication. Only need ESS + basic economic indicators (Gini, GDP, unemployment).

## Notes

- All models use `statsmodels.MixedLM` with REML estimation
- Level-1 variables are grand-mean centered, Level-2 variables are z-score standardized
- Complete cases: 31,393 individuals in 26 countries (from 48,436 in 28)
