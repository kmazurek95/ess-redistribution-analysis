"""Configuration: paths, variable mappings, regime classifications, data sources."""

from pathlib import Path
from typing import Dict, List

# ============================================================================
# PATH DEFINITIONS
# ============================================================================

# Project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"
MODELS_DIR = OUTPUT_DIR / "models"

# Alias for notebooks
PLOTS_DIR = FIGURES_DIR  # Alias for FIGURES_DIR (used in notebooks)

# Notebook directory
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Documentation directory
DOCS_DIR = PROJECT_ROOT / "docs"

# ============================================================================
# ESS VARIABLE MAPPINGS
# ============================================================================

# Outcome variable
OUTCOME_VAR = "gincdif"  # Government should reduce income differences (1-5 scale)
OUTCOME_VAR_REVERSED = "redist_support"  # After reverse coding (higher = more support)

# Country identifier
COUNTRY_VAR = "cntry"

# Individual-level (Level 1) variables
LEVEL1_VARS = {
    # Core predictors
    "income": "hinctnta",          # Household income decile (1-10)
    "political_trust": "trstprl",  # Trust in parliament (0-10 scale)

    # Demographics
    "age": "agea",                 # Age in years
    "gender": "gndr",              # 1=male, 2=female
    "education": "eduyrs",         # Years of full-time education

    # Meritocracy items (ESS9 Justice & Fairness rotating module)
    "merit_effort": "sofrwrk",     # Society fair when hard-working people earn more (1-5)
    "merit_deserve": "ppldsrv",    # People get what they deserve (1-5)

    # Employment status (to create unemployment history)
    "employment_status": "mnactic", # Main activity last 7 days
    "ever_unemployed": "uemp12m",   # Unemployed seeking work last 12 months
}

# ESS missing value codes
MISSING_CODES = {
    "refusal": 7,
    "dont_know": 8,
    "no_answer": 9,
    "not_applicable": 66,
    "refusal_alt": 77,
    "dont_know_alt": 88,
    "no_answer_alt": 99,
}

# ============================================================================
# COUNTRY LIST (28 countries, Slovakia excluded)
# ============================================================================

COUNTRIES = [
    "AT",  # Austria
    "BE",  # Belgium
    "BG",  # Bulgaria
    "CH",  # Switzerland
    "CY",  # Cyprus
    "CZ",  # Czech Republic
    "DE",  # Germany
    "DK",  # Denmark
    "EE",  # Estonia
    "ES",  # Spain
    "FI",  # Finland
    "FR",  # France
    "GB",  # Great Britain
    "HR",  # Croatia
    "HU",  # Hungary
    "IE",  # Ireland
    "IS",  # Iceland
    "IT",  # Italy
    "LT",  # Lithuania
    "LV",  # Latvia
    "ME",  # Montenegro
    "NL",  # Netherlands
    "NO",  # Norway
    "PL",  # Poland
    "PT",  # Portugal
    "RS",  # Serbia
    "SE",  # Sweden
    "SI",  # Slovenia
]

# Country names (for visualization)
COUNTRY_NAMES = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CH": "Switzerland",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "Great Britain",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IS": "Iceland",
    "IT": "Italy",
    "LT": "Lithuania",
    "LV": "Latvia",
    "ME": "Montenegro",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RS": "Serbia",
    "SE": "Sweden",
    "SI": "Slovenia",
}

# ============================================================================
# WELFARE REGIME CLASSIFICATIONS
# ============================================================================

# Esping-Andersen typology (extended to include Mediterranean and Post-Communist)
WELFARE_REGIMES_ESPING = {
    "Social Democratic": ["DK", "SE", "NO", "FI", "IS"],
    "Conservative/Corporatist": ["DE", "FR", "BE", "AT", "NL", "CH"],
    "Liberal": ["GB", "IE"],
    "Mediterranean": ["ES", "IT", "PT", "CY"],
    "Post-Communist": ["CZ", "EE", "HR", "HU", "LT", "LV", "PL", "SI", "BG", "RS", "ME"],
}

# Varieties of Capitalism classification (Hall & Soskice + extensions)
WELFARE_REGIMES_VOC = {
    "Liberal Market Economies (LME)": ["GB", "IE"],
    "Coordinated Market Economies (CME)": ["DE", "AT", "BE", "NL", "CH", "DK", "SE", "NO", "FI", "IS"],
    "Mediterranean Market Economies (MME)": ["ES", "IT", "PT", "FR", "CY"],
    "Dependent Market Economies (DME)": ["CZ", "EE", "HR", "HU", "LT", "LV", "PL", "SI", "BG", "RS", "ME"],
}

# Reverse mapping (country -> regime) for Esping-Andersen
COUNTRY_TO_REGIME_ESPING: Dict[str, str] = {}
for regime, countries in WELFARE_REGIMES_ESPING.items():
    for country in countries:
        COUNTRY_TO_REGIME_ESPING[country] = regime

# Reverse mapping for VoC
COUNTRY_TO_REGIME_VOC: Dict[str, str] = {}
for regime, countries in WELFARE_REGIMES_VOC.items():
    for country in countries:
        COUNTRY_TO_REGIME_VOC[country] = regime

# ============================================================================
# COUNTRY-LEVEL (Level 2) VARIABLES
# ============================================================================

# Basic economic indicators
LEVEL2_VARS_BASIC = {
    "gini": "Gini coefficient (disposable income, 0-100 scale)",
    "gdp": "GDP per capita (PPP, current international $)",
    "unemployment": "Unemployment rate (%)",
    "political_trust_l2": "Country-level mean political trust (aggregated from L1)",
}

# Institutional indicators
LEVEL2_VARS_INSTITUTIONAL = {
    "epl": "Employment Protection Legislation strictness (OECD, 0-6 scale)",
    "almp": "Active Labor Market Policy spending (% GDP)",
    "union_density": "Trade union density (% of employees)",
    "social_spending": "Social expenditure (% GDP)",
    "collective_bargaining": "Collective bargaining coverage (%)",
}

# AI/Automation exposure indicators
LEVEL2_VARS_AI = {
    "ai_exposure_oecd": "OECD AI exposure index (country-level)",
    "automation_risk": "Frey & Osborne automation probability (country average)",
    "ai_exposure_felten": "Felten, Raj & Seamans AI exposure index",
    "social_exposure": "Social exposure composite (technical exposure × institutional weakness)",
}

# ============================================================================
# DATA FILE PATHS
# ============================================================================

# ESS data
ESS_FILE = RAW_DATA_DIR / "ESS9e03_3.dta"

# Country-level data files
GINI_FILE = EXTERNAL_DATA_DIR / "gini_data.csv"
GDP_FILE = EXTERNAL_DATA_DIR / "gdp_data.csv"
UNEMPLOYMENT_FILE = EXTERNAL_DATA_DIR / "unemployment_data.csv"
INSTITUTIONAL_FILE = EXTERNAL_DATA_DIR / "institutional_data.csv"
AI_EXPOSURE_FILE = EXTERNAL_DATA_DIR / "ai_exposure_data.csv"

# Processed data
PROCESSED_FILE = PROCESSED_DATA_DIR / "analysis_dataset.parquet"

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

PLOT_SETTINGS = {
    "style": "darkgrid",  # seaborn style: white, dark, whitegrid, darkgrid, ticks
    "context": "notebook",
    "palette": "Set2",
    "figure_format": "png",
    "dpi": 300,
    "figure_size": (10, 6),
}

# Regime colors for consistent visualization
REGIME_COLORS = {
    "Social Democratic": "#1f77b4",      # Blue
    "Conservative/Corporatist": "#ff7f0e",  # Orange
    "Liberal": "#2ca02c",                 # Green
    "Mediterranean": "#d62728",           # Red
    "Post-Communist": "#9467bd",          # Purple
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FILE = PROJECT_ROOT / "analysis.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# REPRODUCIBILITY
# ============================================================================

RANDOM_SEED = 42  # For any random operations

