"""
Automated OECD Data Collection Script

This script fetches basic economic indicators (Gini, GDP, unemployment)
for all ESS Round 9 countries from the OECD API.

Usage:
    python scripts/fetch_oecd_data.py

Requirements:
    pip install requests pandas

Author: Auto-generated for ESS Redistribution Analysis
"""

import logging
import sys
from pathlib import Path

import pandas as pd
import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.utils import setup_logging

logger = setup_logging()


def fetch_oecd_data(dataset_code: str, dimensions: str, params: dict = None) -> pd.DataFrame:
    """
    Fetch data from OECD.Stat API using SDMX-JSON format.

    Args:
        dataset_code: OECD dataset code (e.g., 'IDD' for income distribution)
        dimensions: Dimension filter string (e.g., 'AUT+BEL+DEU.GINI..')
        params: Optional query parameters

    Returns:
        DataFrame with OECD data
    """
    base_url = "https://stats.oecd.org/SDMX-JSON/data"
    url = f"{base_url}/{dataset_code}/{dimensions}/all"

    if params is None:
        params = {}

    logger.info(f"Fetching from OECD API: {dataset_code}")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Parse SDMX-JSON structure
        # Note: This is a simplified parser - OECD SDMX-JSON can be complex
        observations = data.get('dataSets', [{}])[0].get('observations', {})

        if not observations:
            logger.warning(f"No observations found in dataset {dataset_code}")
            return pd.DataFrame()

        # Extract data (structure depends on specific dataset)
        # This is a template - may need adjustment per dataset
        results = []

        for key, value_list in observations.items():
            # Parse key (e.g., "0:1:2" representing dimension positions)
            indices = [int(i) for i in key.split(':')]

            # Value is typically the first element
            value = value_list[0] if isinstance(value_list, list) else value_list

            results.append({
                'key': key,
                'value': value,
                'indices': indices
            })

        df = pd.DataFrame(results)
        logger.info(f"Fetched {len(df)} observations from {dataset_code}")

        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching OECD data: {e}")
        return pd.DataFrame()


def fetch_gini_coefficients(countries: list = None, year: int = 2018) -> pd.DataFrame:
    """
    Fetch Gini coefficients from OECD Income Distribution Database.

    Args:
        countries: List of ISO2 country codes (e.g., ['AT', 'BE', 'DE'])
        year: Year to fetch (default: 2018)

    Returns:
        DataFrame with columns: country, year, gini
    """
    logger.info(f"Fetching Gini coefficients for year {year}...")

    if countries is None:
        countries = config.COUNTRIES

    # Convert to ISO3 codes (OECD uses ISO3)
    iso2_to_iso3 = {
        'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'CH': 'CHE', 'CY': 'CYP',
        'CZ': 'CZE', 'DE': 'DEU', 'DK': 'DNK', 'EE': 'EST', 'ES': 'ESP',
        'FI': 'FIN', 'FR': 'FRA', 'GB': 'GBR', 'HR': 'HRV', 'HU': 'HUN',
        'IE': 'IRL', 'IS': 'ISL', 'IT': 'ITA', 'LT': 'LTU', 'LV': 'LVA',
        'ME': 'MNE', 'NL': 'NLD', 'NO': 'NOR', 'PL': 'POL', 'PT': 'PRT',
        'RS': 'SRB', 'SE': 'SWE', 'SI': 'SVN'
    }

    # Filter to OECD countries only (API won't have non-OECD)
    oecd_members = ['AT', 'BE', 'CH', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR',
                    'GB', 'HU', 'IE', 'IS', 'IT', 'LT', 'LV', 'NL', 'NO', 'PL',
                    'PT', 'SE', 'SI']

    countries_filtered = [c for c in countries if c in oecd_members]

    if len(countries_filtered) < len(countries):
        missing = set(countries) - set(countries_filtered)
        logger.warning(f"Non-OECD countries will be missing: {missing}")

    # Convert to ISO3
    iso3_codes = [iso2_to_iso3[c] for c in countries_filtered]

    # Build dimension string
    countries_str = '+'.join(iso3_codes)

    # OECD Income Distribution Database structure:
    # IDD/{LOCATION}.{MEASURE}.{DEFINITION}.{METHODOLOGY}.{UNIT}/{time}
    dimensions = f"{countries_str}.GINI..../all?startTime={year}&endTime={year}"

    # Attempt to fetch (this is a simplified approach)
    # In practice, you may need to use a dedicated OECD package or manual download

    logger.warning(
        "OECD API access for Gini requires complex SDMX queries. "
        "For production use, consider:\n"
        "1. Using pandasdmx package for robust OECD access\n"
        "2. Manual download from OECD.Stat Explorer\n"
        "3. Using World Bank API as alternative"
    )

    # Placeholder: Return template DataFrame
    # TODO: Implement actual API call or use pandasdmx

    gini_data = []
    for country in countries_filtered:
        # Placeholder values (replace with actual API fetch)
        gini_data.append({
            'country': country,
            'year': year,
            'gini': None  # TODO: Fetch from API
        })

    df = pd.DataFrame(gini_data)

    logger.info(f"Gini data template created for {len(df)} countries")
    logger.info("⚠️  Manual download still required. See DATA_SOURCES.md")

    return df


def fetch_world_bank_data(indicator: str, countries: list = None, year: int = 2018) -> pd.DataFrame:
    """
    Fetch data from World Bank API (alternative to OECD).

    Args:
        indicator: World Bank indicator code (e.g., 'SI.POV.GINI')
        countries: List of ISO2 country codes
        year: Year to fetch

    Returns:
        DataFrame with country, year, value
    """
    logger.info(f"Fetching World Bank indicator: {indicator}")

    if countries is None:
        countries = config.COUNTRIES

    # Convert to ISO3
    iso2_to_iso3 = {
        'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'CH': 'CHE', 'CY': 'CYP',
        'CZ': 'CZE', 'DE': 'DEU', 'DK': 'DNK', 'EE': 'EST', 'ES': 'ESP',
        'FI': 'FIN', 'FR': 'FRA', 'GB': 'GBR', 'HR': 'HRV', 'HU': 'HUN',
        'IE': 'IRL', 'IS': 'ISL', 'IT': 'ITA', 'LT': 'LTU', 'LV': 'LVA',
        'ME': 'MNE', 'NL': 'NLD', 'NO': 'NOR', 'PL': 'POL', 'PT': 'PRT',
        'RS': 'SRB', 'SE': 'SWE', 'SI': 'SVN'
    }

    results = []

    for country in countries:
        iso3 = iso2_to_iso3.get(country)
        if not iso3:
            logger.warning(f"Unknown country code: {country}")
            continue

        url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator}"
        params = {
            'date': year,
            'format': 'json',
            'per_page': 1000
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if len(data) > 1 and data[1]:
                for obs in data[1]:
                    if obs['value'] is not None:
                        results.append({
                            'country': country,
                            'year': obs['date'],
                            'value': obs['value']
                        })

        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching {country}: {e}")
            continue

    df = pd.DataFrame(results)
    logger.info(f"Fetched World Bank data for {len(df)} country-year observations")

    return df


def main():
    """Main execution function."""
    logger.info("Starting automated OECD/World Bank data collection...")

    countries = config.COUNTRIES
    year = 2018

    # Create output directory
    output_dir = config.EXTERNAL_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Option 1: Try OECD (limited to members)
    logger.info("\n=== Attempting OECD API (OECD members only) ===")
    gini_df = fetch_gini_coefficients(countries, year)

    # Option 2: World Bank (broader coverage, but different methodology)
    logger.info("\n=== Fetching from World Bank API (all countries) ===")

    # World Bank indicator codes
    wb_gini = fetch_world_bank_data('SI.POV.GINI', countries, year)
    wb_gdp = fetch_world_bank_data('NY.GDP.PCAP.PP.CD', countries, year)
    wb_unemployment = fetch_world_bank_data('SL.UEM.TOTL.ZS', countries, year)

    # Save World Bank data
    if not wb_gini.empty:
        wb_gini.to_csv(output_dir / 'gini_data_worldbank.csv', index=False)
        logger.info(f"✅ Saved Gini data: {len(wb_gini)} observations")

    if not wb_gdp.empty:
        wb_gdp.to_csv(output_dir / 'gdp_data_worldbank.csv', index=False)
        logger.info(f"✅ Saved GDP data: {len(wb_gdp)} observations")

    if not wb_unemployment.empty:
        wb_unemployment.to_csv(output_dir / 'unemployment_data_worldbank.csv', index=False)
        logger.info(f"✅ Saved unemployment data: {len(wb_unemployment)} observations")

    # Summary
    logger.info("\n=== Data Collection Summary ===")
    logger.info(f"Countries requested: {len(countries)}")
    logger.info(f"Gini coefficients fetched: {len(wb_gini)}")
    logger.info(f"GDP values fetched: {len(wb_gdp)}")
    logger.info(f"Unemployment values fetched: {len(wb_unemployment)}")

    logger.info("\n⚠️  Next Steps:")
    logger.info("1. Review fetched data in data/external/")
    logger.info("2. Rename files to match expected format (remove '_worldbank' suffix)")
    logger.info("3. For OECD-specific data, consider manual download from OECD.Stat")
    logger.info("4. ESS data still requires manual download (see DATA_SOURCES.md)")
    logger.info("5. ICTWSS and AI exposure data require manual download")

    logger.info("\n✅ Automated data collection complete!")


if __name__ == "__main__":
    main()
