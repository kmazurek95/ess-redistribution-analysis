# Notebook Execution Guide

This directory contains Jupyter notebooks for the complete ESS redistribution analysis. Execute notebooks **in sequence** (01 → 06) as each notebook depends on outputs from previous ones.

---

## Notebook Sequence

### 01. Data Exploration (`01_data_exploration.ipynb`)

**Purpose:** Initial exploration of ESS Round 9 data and country-level indicators

**Inputs:**
- `data/raw/ESS9e03_3.dta` (ESS Round 9)
- `data/external/gini_data.csv`
- `data/external/gdp_data.csv`
- `data/external/institutional_data.csv` (optional)
- `data/external/ai_exposure_data.csv` (optional)

**Outputs:**
- Descriptive statistics (Table 1 replication)
- Distribution plots by country
- Missing data analysis
- Correlation matrix

**Key Questions Answered:**
- What is the distribution of redistribution support across countries?
- How much variation exists within vs. between countries?
- What are the missing data patterns?
- Are there any data quality issues?

**Estimated Time:** 30-45 minutes

---

### 02. Data Preparation (`02_data_preparation.ipynb`)

**Purpose:** Clean, transform, and merge all datasets into analysis-ready format

**Inputs:**
- Raw ESS data
- Country-level economic data
- Institutional indicators
- AI exposure indicators

**Outputs:**
- `data/processed/analysis_dataset.parquet` (main analysis file)
- Data validation report

**Transformations:**
1. Reverse code `gincdif` → `redist_support`
2. Create meritocracy index from two items
3. Grand-mean center Level-1 variables (income, political trust, age, education, meritocracy)
4. Z-score standardize Level-2 variables (Gini, GDP, unemployment, institutional indicators)
5. Assign welfare regime classifications (Esping-Andersen + VoC)
6. Merge individual and country-level data
7. Create derived variables (female dummy, political trust L2)

**Key Outputs:**
- `redist_support` — Outcome variable (higher = more support)
- `hinctnta_c` — Income (centered)
- `trstprl_c` — Political trust (centered)
- `gini_z` — Gini coefficient (standardized)
- `welfare_regime` — Esping-Andersen classification
- `voc_regime` — Varieties of Capitalism classification

**Estimated Time:** 20-30 minutes

---

### 03. Replication Analysis (`03_replication_analysis.ipynb`)

**Purpose:** Replicate the 7-model sequence from original master's thesis

**Inputs:**
- `data/processed/analysis_dataset.parquet`

**Outputs:**
- Model objects (Models 1-7)
- Regression table (Table 2 replication)
- Model diagnostics (VIF, ICC, R²)
- Interaction plots (income × Gini, political trust × GDP)
- Random effects plots

**Model Sequence:**

| Model | Specification |
|-------|---------------|
| **Model 1** | Null model (ICC calculation) |
| **Model 2** | Add income (Level-1) |
| **Model 3** | Add political trust (Level-1) |
| **Model 4** | Add all Level-1 controls (age, gender, education, unemployment, meritocracy) |
| **Model 5** | Add Level-2 variables (Gini, GDP, unemployment, political trust L2) |
| **Model 6** | Random slopes for income and political trust |
| **Model 7** | Cross-level interactions (income × Gini, political trust × GDP) |

**Key Findings (Expected):**
- ICC ~0.10-0.15 (10-15% variance at country level)
- Income → negative effect on redistribution support (self-interest)
- Political trust → positive effect on redistribution support (legitimacy)
- **Income × Gini interaction:** Higher inequality weakens negative effect of income

**Estimated Time:** 60-90 minutes (model fitting can be slow)

---

### 04. Welfare Regime Extension (`04_welfare_regime_extension.ipynb`)

**Purpose:** Extend analysis with welfare regime theory and institutional mediation

**Inputs:**
- `data/processed/analysis_dataset.parquet`
- Institutional indicators (EPL, ALMP, union density, social spending)

**Outputs:**
- Models 8-13 (regime and institutional models)
- Box/violin plots by welfare regime
- Institutional scatter plots (EPL vs. redistribution, colored by regime)
- Institutional mediation typology

**Analysis Sections:**

**A. Welfare Regime Analysis (Esping-Andersen)**
- Model 8: Regime as Level-2 predictor
- Model 9: Income × Regime interaction
- Model 10: Political trust × Regime interaction

**B. Varieties of Capitalism (Alternative Classification)**
- Compare LME vs. CME vs. MME vs. DME

**C. Institutional Mediation Analysis**
- Model 11: EPL + ALMP + union density + social spending as Level-2 predictors
- Model 12: Income × EPL interaction (does employment protection buffer self-interest?)
- Model 13: Income × ALMP interaction (does active labor market policy buffer self-interest?)

**D. Typology Construction**
- Cluster countries by institutional mediation profile
- Identify ideal-type cases for qualitative study

**Key Research Questions:**
- Do welfare regimes differ in redistribution preferences?
- Do stronger institutions (EPL, ALMP) weaken the income-redistribution link?
- Can we construct a typology of "institutional mediation profiles"?

**Connection to REPAIR:**
- Demonstrates comparative institutional analysis
- Shows how institutions mediate economic effects on preferences
- Builds typology approach for PhD's comparative indicator task

**Estimated Time:** 90-120 minutes

---

### 05. AI Exposure Extension (`05_ai_exposure_extension.ipynb`)

**Purpose:** Analyze AI/automation exposure and "social exposure" composite

**Inputs:**
- `data/processed/analysis_dataset.parquet`
- AI exposure indicators (OECD, Frey & Osborne, Felten et al.)

**Outputs:**
- Models 14-16 (AI exposure models)
- AI exposure by country (bar chart)
- AI exposure by welfare regime (scatter + box plots)
- Social exposure typology

**Analysis Sections:**

**A. AI Exposure Descriptives**
- Country-level AI exposure distribution
- Correlation with institutional indicators
- Regime clustering patterns

**B. AI Exposure Models**
- Model 14: AI exposure as Level-2 predictor → **null** (p = 0.857)
- Model 15: AI exposure × Regime interaction → **null** (all p > 0.19)
- Model 16: Social exposure composite → **null** (p = 0.857)

**C. Social Exposure Composite**
- Construct: AI exposure (technical) × Institutional weakness
- Rationale: Countries with high technical exposure BUT weak institutions are most vulnerable
- Result: Social exposure does not significantly predict redistribution preferences. The direct technological threat pathway is not supported.

**D. Typology of Social Exposure**
- **High exposure, strong institutions:** Countries like Denmark (high AI exposure, strong ALMP/reskilling)
- **High exposure, weak institutions:** Countries like Poland (high AI exposure, weak ALMP)
- **Low exposure, strong institutions:** Countries like Norway
- **Low exposure, weak institutions:** Countries like Bulgaria

**E. Case Selection for Qualitative Study**
- Identify ideal-type cases from each quadrant
- Justification for in-depth institutional analysis

**Key Research Questions:**
- Does AI exposure shape redistribution preferences?
- Do welfare institutions moderate the political effects of automation risk?
- What is the concept of "social exposure" (technical × institutional)?
- Which countries are most vulnerable to AI-driven labor market disruption?

**Connection to REPAIR:**
- **Objective 1:** Analyzes how welfare regimes are affected by AI-driven automation
- Constructs comparative indicators of social exposure (PhD task)
- Demonstrates typology construction method
- Identifies cases for mixed-methods follow-up

**Estimated Time:** 90-120 minutes

---

### 06. Final Report (`06_final_report.ipynb`)

**Purpose:** Synthesize all findings into a final report

**Inputs:**
- All previous notebooks' outputs
- Model objects from Models 1-16

**Outputs:**
- Complete report with:
  - Title & Abstract
  - Introduction (research questions, REPAIR connection)
  - Data & Methods
  - Results (3 parts: replication, regime/institutional, AI exposure)
  - Discussion (institutional buffering, welfare state adaptation)
  - Conclusion (demonstrated skills, future PhD extensions)
- Publication-quality tables and figures
- References

**Report Structure:**

**I. Introduction**
- Research questions
- Theoretical framework (redistribution preferences → institutional mediation → welfare state transformation)
- Explicit mapping to REPAIR Objectives 1 & 4

**II. Data and Methods**
- ESS Round 9 (2018), n=36,159, 28 countries
- Multilevel modeling approach
- Variable transformations (centering, standardization)
- Typology construction method

**III. Results**

*Part A: Replication (Models 1-7)*
- Income × Gini interaction finding
- Random slopes variation
- Model comparison table

*Part B: Welfare Regimes and Institutional Mediation (Models 8-13)*
- Regime differences
- Institutional buffering: Do EPL/ALMP moderate income effects?
- Institutional mediation typology

*Part C: AI Exposure and Social Exposure (Models 14-16)*
- AI exposure effects
- Regime × AI interactions
- Social exposure typology
- Ideal-type cases identified

**IV. Discussion**

*Institutional Buffering Hypothesis*
- Do stronger labor market institutions weaken self-interest effects?
- Implications: Countries with strong ALMP may maintain social solidarity even under AI disruption

*Welfare State Adaptation Pathways*
- Social Democratic regimes: Universalism + reskilling infrastructure
- Liberal regimes: Marketization + residual safety nets
- Post-Communist regimes: Weak institutions + high vulnerability
- Regime-specific recalibration strategies

*Methodological Contribution*
- Comparative indicators/typology construction as foundation for REPAIR comparative database
- Social exposure concept: technical × institutional
- Mixed-methods orientation: quantitative → ideal-type case selection

**V. Conclusion**

*Key Findings*
1. Income × Gini interaction confirms self-interest is context-dependent
2. Institutional indicators (EPL, ALMP) moderate income effects
3. AI exposure interacts with welfare regimes
4. Social exposure typology identifies vulnerable countries

*Demonstrated PhD Competencies*
-Comparative institutional analysis
-Quantitative cross-national data analysis
-Typology/indicator construction
-Mixed-methods orientation
-Theoretical development (institutional mediation)

*Future PhD Extensions*
- Temporal analysis (ESS Rounds 9-11, 2018-2023)
- Qualitative case studies of ideal-type cases
- Causal mechanisms via survey experiments
- Policy implications for ALMP reform, lifelong learning, UBI debates
- Contribution to REPAIR comparative database

**VI. References**

**VII. Appendix**
- Robustness checks
- Additional diagnostics
- Supplementary tables

**Estimated Time:** 120-180 minutes

---

## Quick Start

If you're short on time, prioritize:

**Minimum viable analysis:**
1. Run notebook 02 (data preparation)
2. Run notebook 03 (replication)
3. → This gives you the core 7-model sequence

**For PhD application:**
1. Run notebooks 02-04
2. → This includes regime and institutional analysis (demonstrates REPAIR skills)

**Complete analysis:**
1. Run all notebooks 01-06
2. → Full portfolio piece with all extensions

---

## Technical Notes

### Python Environment

Ensure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### R Dependency (pymer4)

pymer4 requires R with lme4 package:
```bash
# Install R first, then:
R -e "install.packages('lme4', repos='https://cran.rstudio.com/')"
```

### Data Requirements

**Required:**
- ESS Round 9 (`data/raw/ESS9e03_3.dta`)
- Basic economic indicators (Gini, GDP, unemployment)

**Optional (but recommended):**
- Institutional indicators (for notebooks 04-05)
- AI exposure indicators (for notebook 05)

See `data/external/DATA_SOURCES.md` for acquisition instructions.

### Expected Runtime

| Notebook | Runtime |
|----------|---------|
| 01 | 30-45 min |
| 02 | 20-30 min |
| 03 | 60-90 min |
| 04 | 90-120 min |
| 05 | 90-120 min |
| 06 | 120-180 min |
| **Total** | **6-9 hours** |

**Note:** Model fitting (notebooks 03-05) can be slow. Consider running overnight or in background.

---

## Notebook Templates

Each notebook follows this template structure:

```markdown
# [Title]

**Author:** Kaleb Mazurek
**Date:** [Date]
**Purpose:** [Purpose statement]

---

## Setup

import pandas as pd
import numpy as np
from src.data_loader import load_ess_data
from src.utils import setup_logging

logger = setup_logging()

---

## 1. [Section Title]

[Markdown explanation]

[Code cell]

[Output cell]

[Interpretation cell]

---

## Summary

[Key takeaways]
```

---

## Troubleshooting

**Issue: pymer4 not finding R**
- Solution: Set environment variable `R_HOME` to your R installation path

**Issue: Model fitting fails**
- Check for missing data in key variables
- Verify all transformations completed (centered/standardized variables exist)
- Try simpler model first (e.g., Model 1) to diagnose

**Issue: Plots not displaying**
- Ensure `%matplotlib inline` is in setup cell
- Check that output directories exist (`outputs/figures/`)

**Issue: Memory errors**
- ESS Round 9 is large (~36k observations)
- Consider using subset for testing (e.g., `df.sample(5000)`)
- Close other applications

---

## Using the Notebooks

### Jupyter Lab (Recommended)
```bash
jupyter lab
# Navigate to notebooks/ directory
```

### Jupyter Notebook (Classic)
```bash
jupyter notebook
# Navigate to notebooks/ directory
```

### VS Code
- Open project in VS Code
- Install Python and Jupyter extensions
- Open .ipynb files directly

---

## Next Steps After Notebooks

Once you've completed the analysis:

1. **Review outputs:**
   - Tables saved in `outputs/tables/`
   - Figures saved in `outputs/figures/`
   - Models saved in `outputs/models/`

2. **Share with advisors:**
   - Send notebook 06 (final report)
   - Include key figures from `outputs/figures/`
   - Share GitHub repository link

3. **Prepare for PhD application:**
   - Extract key findings for research proposal
   - Identify 2-3 ideal-type cases for qualitative study
   - Outline data collection plan for REPAIR comparative database

4. **Extend the analysis (optional):**
   - Add ESS Rounds 10-11 for temporal trends
   - Conduct robustness checks
   - Test alternative specifications

---

## Contact

For questions or issues:
- **Author:** Kaleb Mazurek
- **GitHub:** https://github.com/kmazurek95/ess-redistribution-analysis

---

**Last Updated:** February 2026
