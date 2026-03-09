"""
Aggregate Felten et al. (2021) AIOE Scores to Country Level

This script computes country-level AI Occupational Exposure (AIOE) scores
for ESS Round 9 countries by combining:
  1. Occupation-level AIOE scores (Felten, Raj & Seamans 2021)
  2. A SOC-2010 to ISCO-08 major group crosswalk
  3. Eurostat Labour Force Survey employment shares by ISCO-08 (2018)

Methodology:
  - AIOE scores at SOC 6-digit level are averaged to SOC 2-digit major groups
  - SOC 2-digit groups are mapped to ISCO-08 1-digit major groups
  - For SOC groups that span two ISCO groups (e.g., SOC 13 Business/Financial
    maps to both ISCO 2 Professionals and ISCO 3 Technicians), the AIOE score
    is split equally (50/50 weight)
  - Country-level scores are the employment-weighted average of ISCO-level
    AIOE scores, using each country's 2018 occupational composition from
    Eurostat LFS

Data sources:
  - AIOE: github.com/AIOE-Data/AIOE -> AIOE_DataAppendix.xlsx, Appendix A
  - Employment: Eurostat table lfsa_egais, year 2018, sex=total, age=15-64
  - Crosswalk: Standard SOC-to-ISCO correspondence (BLS/ILO)

Citation:
  Felten E, Raj M, Seamans R (2021) Occupational, industry, and geographic
  exposure to artificial intelligence: A novel dataset and its potential uses.
  Strategic Management Journal 42(12):2195-2217.

Usage:
  python scripts/aggregate_aioe.py

Output:
  data/external/ai_exposure_data.csv
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import requests

warnings.filterwarnings("ignore", category=UserWarning)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config


# ============================================================
# SOC 2-digit to ISCO-08 1-digit crosswalk
# ============================================================
# Based on BLS/ILO correspondence tables and published literature
# (Autor & Dorn 2013, Goos et al. 2014, IMF WP/2023/216).
# Where a SOC group spans two ISCO groups, the weight is split 50/50.

CROSSWALK = pd.DataFrame([
    ("11", 1, 1.0),   # Management -> Managers
    ("13", 2, 0.5),   # Business/Financial -> Professionals
    ("13", 3, 0.5),   # Business/Financial -> Technicians
    ("15", 2, 1.0),   # Computer/Math -> Professionals
    ("17", 2, 1.0),   # Architecture/Engineering -> Professionals
    ("19", 2, 1.0),   # Life/Physical/Social Science -> Professionals
    ("21", 2, 1.0),   # Community/Social Service -> Professionals
    ("23", 2, 1.0),   # Legal -> Professionals
    ("25", 2, 1.0),   # Education/Training -> Professionals
    ("27", 2, 0.5),   # Arts/Design/Entertainment -> Professionals
    ("27", 3, 0.5),   # Arts/Design/Entertainment -> Technicians
    ("29", 2, 1.0),   # Healthcare Practitioners -> Professionals
    ("31", 3, 1.0),   # Healthcare Support -> Technicians
    ("33", 5, 1.0),   # Protective Service -> Service/Sales
    ("35", 5, 1.0),   # Food Prep/Serving -> Service/Sales
    ("37", 9, 1.0),   # Building/Grounds Cleaning -> Elementary
    ("39", 5, 1.0),   # Personal Care/Service -> Service/Sales
    ("41", 5, 1.0),   # Sales -> Service/Sales
    ("43", 4, 1.0),   # Office/Admin -> Clerical
    ("45", 6, 1.0),   # Farming/Fishing/Forestry -> Skilled Agricultural
    ("47", 7, 1.0),   # Construction/Extraction -> Craft/Trades
    ("49", 7, 1.0),   # Installation/Maintenance/Repair -> Craft/Trades
    ("51", 8, 1.0),   # Production -> Plant/Machine Operators
    ("53", 8, 0.5),   # Transportation -> Operators
    ("53", 9, 0.5),   # Transportation -> Elementary
], columns=["soc_major", "isco_major", "weight"])


def load_aioe_scores(filepath: Path) -> pd.DataFrame:
    """Load AIOE scores and aggregate to SOC 2-digit level."""
    aioe = pd.read_excel(filepath, sheet_name="Appendix A")
    aioe["soc_major"] = aioe["SOC Code"].str[:2]
    soc_aioe = aioe.groupby("soc_major")["AIOE"].mean().reset_index()
    soc_aioe.columns = ["soc_major", "aioe_soc"]
    print(f"  Loaded {len(aioe)} occupations -> {len(soc_aioe)} SOC major groups")
    return soc_aioe


def map_soc_to_isco(soc_aioe: pd.DataFrame) -> pd.DataFrame:
    """Map SOC-level AIOE scores to ISCO-08 major groups via crosswalk."""
    merged = CROSSWALK.merge(soc_aioe, on="soc_major")
    isco_aioe = (
        merged
        .assign(weighted_aioe=lambda x: x["aioe_soc"] * x["weight"])
        .groupby("isco_major")
        .agg(aioe_sum=("weighted_aioe", "sum"), weight_sum=("weight", "sum"))
        .assign(aioe_isco=lambda x: x["aioe_sum"] / x["weight_sum"])
        .reset_index()
    )
    print(f"  Mapped to {len(isco_aioe)} ISCO-08 major groups")
    return isco_aioe[["isco_major", "aioe_isco"]]


def fetch_eurostat_employment(cache_path: Path) -> pd.DataFrame:
    """Fetch or load cached Eurostat LFS employment by ISCO-08 (2018)."""
    if cache_path.exists():
        print(f"  Loading cached Eurostat data from {cache_path}")
        return pd.read_csv(cache_path)

    print("  Fetching Eurostat LFS data (lfsa_egais, 2018)...")
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfsa_egais"
    params = {
        "format": "JSON",
        "lang": "en",
        "time": "2018",
        "sex": "T",
        "age": "Y15-64",
        "wstatus": "EMP",
    }
    resp = requests.get(url, params=params, timeout=60, verify=False)
    resp.raise_for_status()
    data = resp.json()

    geo_index = data["dimension"]["geo"]["category"]["index"]
    isco_index = data["dimension"]["isco08"]["category"]["index"]
    n_geo = len(geo_index)
    n_time = data["size"][-1]

    isco_targets = {f"OC{i}": i for i in range(1, 10)}
    ess_geo = set(config.COUNTRIES) | {"UK"}  # Eurostat uses UK, ESS uses GB

    records = []
    for isco_code, isco_pos in isco_index.items():
        if isco_code not in isco_targets:
            continue
        for geo_code, geo_pos in geo_index.items():
            if geo_code not in ess_geo:
                continue
            flat_idx = isco_pos * n_geo * n_time + geo_pos * n_time
            val = data["value"].get(str(flat_idx))
            if val is not None:
                records.append({
                    "geo": geo_code,
                    "isco_major": isco_targets[isco_code],
                    "employment_thousands": val,
                })

    df = pd.DataFrame(records)
    df.to_csv(cache_path, index=False)
    print(f"  Fetched {len(df)} records for {df['geo'].nunique()} countries")
    return df


def compute_country_scores(
    isco_aioe: pd.DataFrame, employment: pd.DataFrame
) -> pd.DataFrame:
    """Compute employment-weighted country-level AIOE scores."""
    # Map Eurostat UK -> ESS GB
    employment = employment.copy()
    employment["country"] = employment["geo"].replace({"UK": "GB"})

    merged = employment.merge(isco_aioe, on="isco_major")

    country_scores = (
        merged
        .groupby("country")
        .apply(
            lambda g: np.average(g["aioe_isco"], weights=g["employment_thousands"]),
            include_groups=False,
        )
        .reset_index()
    )
    country_scores.columns = ["country", "ai_exposure_felten"]
    country_scores = country_scores.sort_values("country").reset_index(drop=True)
    return country_scores


def main():
    print("=" * 60)
    print("  AIOE Country-Level Aggregation")
    print("  Felten, Raj & Seamans (2021) -> Eurostat LFS 2018")
    print("=" * 60)

    raw_dir = config.EXTERNAL_DATA_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Load AIOE
    aioe_path = raw_dir / "AIOE_DataAppendix.xlsx"
    if not aioe_path.exists():
        print(f"\n  ERROR: {aioe_path} not found.")
        print("  Download from: https://github.com/AIOE-Data/AIOE")
        sys.exit(1)

    print("\n[1/4] Loading AIOE occupation-level scores...")
    soc_aioe = load_aioe_scores(aioe_path)

    # Step 2: Crosswalk
    print("\n[2/4] Mapping SOC -> ISCO-08 via crosswalk...")
    isco_aioe = map_soc_to_isco(soc_aioe)

    # Step 3: Eurostat employment
    print("\n[3/4] Loading Eurostat employment data...")
    cache_path = raw_dir / "eurostat_employment_isco08_2018.csv"
    employment = fetch_eurostat_employment(cache_path)

    # Step 4: Aggregate
    print("\n[4/4] Computing country-level scores...")
    scores = compute_country_scores(isco_aioe, employment)

    # Map Felten AIOE to ai_exposure_oecd column (used by models in src/models.py)
    # This is the project's primary AI exposure measure; the column name is
    # retained for pipeline compatibility with data_prep.py and models.py.
    scores["ai_exposure_oecd"] = scores["ai_exposure_felten"]
    scores["automation_risk"] = np.nan  # Placeholder for Frey & Osborne
    scores["social_exposure"] = np.nan  # Computed in notebook 05

    # Reorder to match pipeline expectations (data_loader.py)
    scores = scores[["country", "ai_exposure_oecd", "automation_risk",
                      "ai_exposure_felten", "social_exposure"]]

    # Save
    output_path = config.AI_EXPOSURE_FILE
    scores.to_csv(output_path, index=False)
    print(f"\n  Saved to {output_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  Results: {len(scores)} countries")
    print(f"  Range: {scores['ai_exposure_felten'].min():.4f} "
          f"to {scores['ai_exposure_felten'].max():.4f}")
    print(f"  Mean:  {scores['ai_exposure_felten'].mean():.4f}")
    print(f"  SD:    {scores['ai_exposure_felten'].std():.4f}")
    print(f"{'='*60}")

    # Print ranking
    print(f"\n  {'Country':<6} {'AIOE':>8}")
    print(f"  {'-'*14}")
    for _, row in scores.sort_values("ai_exposure_felten", ascending=False).iterrows():
        print(f"  {row['country']:<6} {row['ai_exposure_felten']:>8.4f}")


if __name__ == "__main__":
    main()
