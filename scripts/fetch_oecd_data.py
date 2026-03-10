"""
Fetch basic economic indicators (Gini, GDP, unemployment) for ESS Round 9
countries from the OECD and World Bank APIs.

Note: OECD Gini data was ultimately downloaded manually and lives in
data/external/. The API functions here served as exploratory scaffolding.
"""

import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.utils import setup_logging

logger = setup_logging()

ISO2_TO_ISO3 = {
    'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'CH': 'CHE', 'CY': 'CYP',
    'CZ': 'CZE', 'DE': 'DEU', 'DK': 'DNK', 'EE': 'EST', 'ES': 'ESP',
    'FI': 'FIN', 'FR': 'FRA', 'GB': 'GBR', 'HR': 'HRV', 'HU': 'HUN',
    'IE': 'IRL', 'IS': 'ISL', 'IT': 'ITA', 'LT': 'LTU', 'LV': 'LVA',
    'ME': 'MNE', 'NL': 'NLD', 'NO': 'NOR', 'PL': 'POL', 'PT': 'PRT',
    'RS': 'SRB', 'SE': 'SWE', 'SI': 'SVN'
}


def fetch_oecd_data(dataset_code: str, dimensions: str, params: dict = None) -> pd.DataFrame:
    """Fetch data from OECD.Stat API (SDMX-JSON format)."""
    base_url = "https://stats.oecd.org/SDMX-JSON/data"
    url = f"{base_url}/{dataset_code}/{dimensions}/all"

    if params is None:
        params = {}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        observations = data.get('dataSets', [{}])[0].get('observations', {})
        if not observations:
            logger.warning(f"No observations found in dataset {dataset_code}")
            return pd.DataFrame()

        results = []
        for key, value_list in observations.items():
            indices = [int(i) for i in key.split(':')]
            value = value_list[0] if isinstance(value_list, list) else value_list
            results.append({'key': key, 'value': value, 'indices': indices})

        return pd.DataFrame(results)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching OECD data: {e}")
        return pd.DataFrame()


def fetch_gini_coefficients(countries: list = None, year: int = 2018) -> pd.DataFrame:
    """Return a template DataFrame for Gini coefficients.

    OECD Gini data requires complex SDMX queries and was collected manually.
    See data/external/ for the actual data files.
    """
    if countries is None:
        countries = config.COUNTRIES

    oecd_members = ['AT', 'BE', 'CH', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR',
                    'GB', 'HU', 'IE', 'IS', 'IT', 'LT', 'LV', 'NL', 'NO', 'PL',
                    'PT', 'SE', 'SI']

    countries_filtered = [c for c in countries if c in oecd_members]

    if len(countries_filtered) < len(countries):
        missing = set(countries) - set(countries_filtered)
        logger.warning(f"Non-OECD countries will be missing: {missing}")

    # Data was collected manually via OECD.Stat Explorer and stored in data/external/.
    gini_data = [{'country': c, 'year': year, 'gini': None} for c in countries_filtered]
    df = pd.DataFrame(gini_data)
    logger.info(f"Gini template created for {len(df)} countries (actual data in data/external/)")
    return df


def fetch_world_bank_data(indicator: str, countries: list = None, year: int = 2018) -> pd.DataFrame:
    """Fetch a single indicator from the World Bank API."""
    if countries is None:
        countries = config.COUNTRIES

    results = []
    for country in countries:
        iso3 = ISO2_TO_ISO3.get(country)
        if not iso3:
            logger.warning(f"Unknown country code: {country}")
            continue

        url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator}"
        params = {'date': year, 'format': 'json', 'per_page': 1000}

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

    return pd.DataFrame(results)


def main():
    countries = config.COUNTRIES
    year = 2018

    output_dir = config.EXTERNAL_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    gini_df = fetch_gini_coefficients(countries, year)

    wb_gini = fetch_world_bank_data('SI.POV.GINI', countries, year)
    wb_gdp = fetch_world_bank_data('NY.GDP.PCAP.PP.CD', countries, year)
    wb_unemployment = fetch_world_bank_data('SL.UEM.TOTL.ZS', countries, year)

    if not wb_gini.empty:
        wb_gini.to_csv(output_dir / 'gini_data_worldbank.csv', index=False)
    if not wb_gdp.empty:
        wb_gdp.to_csv(output_dir / 'gdp_data_worldbank.csv', index=False)
    if not wb_unemployment.empty:
        wb_unemployment.to_csv(output_dir / 'unemployment_data_worldbank.csv', index=False)

    logger.info(
        f"Collection complete: {len(wb_gini)} Gini, {len(wb_gdp)} GDP, "
        f"{len(wb_unemployment)} unemployment observations"
    )


if __name__ == "__main__":
    main()
