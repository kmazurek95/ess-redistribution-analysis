"""Unit tests for data preparation functions."""

import numpy as np
import pandas as pd
import pytest

from src.data_prep import (
    reverse_code,
    create_meritocracy_index,
    center_variables,
    standardize_variables,
    assign_welfare_regime,
)


@pytest.fixture
def sample_df():
    np.random.seed(42)
    return pd.DataFrame({
        'cntry': ['AT', 'AT', 'BE', 'BE', 'DE', 'DE'] * 10,
        'gincdif': [1, 2, 3, 4, 5, 1] * 10,
        'hinctnta': [3, 7, 5, 8, 2, 9] * 10,
        'trstprl': [5.5, 7.2, 3.1, 8.9, 4.5, 6.0] * 10,
        'fairelc': [2, 3, 4, 5, 1, 3] * 10,
        'dscrgrp': [3, 4, 2, 5, 2, 4] * 10,
        'agea': [25, 45, 35, 55, 30, 60] * 10,
        'eduyrs': [12, 16, 14, 18, 10, 15] * 10,
    })


@pytest.fixture
def sample_country_data():
    return pd.DataFrame({
        'country': ['AT', 'BE', 'DE'],
        'gini': [29.4, 27.2, 31.5],
        'gdp': [53267, 49532, 51680],
        'epl': [2.35, 2.54, 2.84],
    })


def test_reverse_code_basic():
    series = pd.Series([1, 2, 3, 4, 5])
    result = reverse_code(series, max_val=5, min_val=1)
    expected = pd.Series([5, 4, 3, 2, 1])
    pd.testing.assert_series_equal(result, expected)


def test_reverse_code_with_missing():
    series = pd.Series([1, 2, np.nan, 4, 5])
    result = reverse_code(series, max_val=5, min_val=1)

    assert result.isna().sum() == 1
    assert result.iloc[0] == 5
    assert result.iloc[1] == 4


def test_reverse_code_different_scale():
    series = pd.Series([0, 5, 10])
    result = reverse_code(series, max_val=10, min_val=0)
    expected = pd.Series([10, 5, 0])
    pd.testing.assert_series_equal(result, expected)


def test_create_meritocracy_index(sample_df):
    result = create_meritocracy_index(sample_df)

    assert 'meritocracy' in result.columns
    assert result['meritocracy'].notna().all()

    expected = (sample_df['fairelc'] + sample_df['dscrgrp']) / 2
    pd.testing.assert_series_equal(result['meritocracy'], expected, check_names=False)


def test_create_meritocracy_index_with_missing(sample_df):
    sample_df.loc[0, 'fairelc'] = np.nan
    result = create_meritocracy_index(sample_df)

    assert pd.isna(result.loc[0, 'meritocracy'])
    assert result.loc[1, 'meritocracy'] == (sample_df.loc[1, 'fairelc'] + sample_df.loc[1, 'dscrgrp']) / 2


def test_create_meritocracy_index_custom_name(sample_df):
    result = create_meritocracy_index(sample_df, index_name='merit_index')

    assert 'merit_index' in result.columns
    assert 'meritocracy' not in result.columns


def test_center_variables_grand_mean(sample_df):
    result = center_variables(sample_df, vars_to_center=['hinctnta', 'trstprl'])

    assert 'hinctnta_c' in result.columns
    assert 'trstprl_c' in result.columns
    assert abs(result['hinctnta_c'].mean()) < 1e-10
    assert abs(result['trstprl_c'].mean()) < 1e-10


def test_center_variables_group_mean(sample_df):
    result = center_variables(
        sample_df,
        vars_to_center=['hinctnta'],
        group_var='cntry'
    )

    for country in sample_df['cntry'].unique():
        country_data = result[result['cntry'] == country]
        assert abs(country_data['hinctnta_c'].mean()) < 1e-10


def test_center_variables_custom_suffix(sample_df):
    result = center_variables(
        sample_df,
        vars_to_center=['hinctnta'],
        suffix='_centered'
    )

    assert 'hinctnta_centered' in result.columns
    assert 'hinctnta_c' not in result.columns


def test_center_variables_preserves_variance(sample_df):
    result = center_variables(sample_df, vars_to_center=['hinctnta'])

    original_var = sample_df['hinctnta'].var()
    centered_var = result['hinctnta_c'].var()
    assert abs(original_var - centered_var) < 1e-10


def test_standardize_variables_basic(sample_country_data):
    result = standardize_variables(sample_country_data, vars_to_standardize=['gini', 'gdp'])

    assert 'gini_z' in result.columns
    assert 'gdp_z' in result.columns
    assert abs(result['gini_z'].mean()) < 1e-10
    assert abs(result['gini_z'].std() - 1.0) < 1e-10


def test_standardize_variables_custom_suffix(sample_country_data):
    result = standardize_variables(
        sample_country_data,
        vars_to_standardize=['gini'],
        suffix='_standardized'
    )

    assert 'gini_standardized' in result.columns
    assert 'gini_z' not in result.columns


def test_standardize_variables_zero_variance():
    """Zero-variance column should be skipped."""
    df = pd.DataFrame({
        'constant': [5, 5, 5, 5],
        'varying': [1, 2, 3, 4]
    })

    result = standardize_variables(df, vars_to_standardize=['constant', 'varying'])

    assert 'constant_z' not in result.columns
    assert 'varying_z' in result.columns


def test_assign_welfare_regime_esping(sample_df):
    result = assign_welfare_regime(sample_df, classification='esping_andersen')

    assert 'welfare_regime' in result.columns

    at_regime = result[result['cntry'] == 'AT']['welfare_regime'].iloc[0]
    assert at_regime == 'Conservative/Corporatist'

    be_regime = result[result['cntry'] == 'BE']['welfare_regime'].iloc[0]
    assert at_regime == 'Conservative/Corporatist'

    de_regime = result[result['cntry'] == 'DE']['welfare_regime'].iloc[0]
    assert de_regime == 'Conservative/Corporatist'


def test_assign_welfare_regime_voc(sample_df):
    result = assign_welfare_regime(sample_df, classification='voc', regime_var_name='voc_regime')

    assert 'voc_regime' in result.columns

    de_voc = result[result['cntry'] == 'DE']['voc_regime'].iloc[0]
    assert de_voc == 'Coordinated Market Economies (CME)'


def test_assign_welfare_regime_custom_name(sample_df):
    result = assign_welfare_regime(
        sample_df,
        classification='esping_andersen',
        regime_var_name='custom_regime'
    )

    assert 'custom_regime' in result.columns
    assert 'welfare_regime' not in result.columns


def test_assign_welfare_regime_all_countries():
    import config

    df = pd.DataFrame({'cntry': config.COUNTRIES})
    result = assign_welfare_regime(df)

    assert result['welfare_regime'].notna().all()

    unique_regimes = result['welfare_regime'].unique()
    assert len(unique_regimes) == 5


def test_full_transformation_pipeline(sample_df):
    df = sample_df.copy()

    df['redist_support'] = reverse_code(df['gincdif'], max_val=5)
    df = create_meritocracy_index(df)
    df = center_variables(df, vars_to_center=['hinctnta', 'trstprl', 'agea'])
    df = assign_welfare_regime(df)

    assert 'redist_support' in df.columns
    assert 'meritocracy' in df.columns
    assert 'hinctnta_c' in df.columns
    assert 'trstprl_c' in df.columns
    assert 'agea_c' in df.columns
    assert 'welfare_regime' in df.columns
    assert abs(df['hinctnta_c'].mean()) < 1e-10
    assert df['welfare_regime'].notna().all()


def test_empty_dataframe():
    df = pd.DataFrame()
    result = center_variables(df, vars_to_center=['nonexistent'])
    assert len(result) == 0


def test_all_missing_values():
    df = pd.DataFrame({
        'var1': [np.nan, np.nan, np.nan],
        'var2': [np.nan, np.nan, np.nan]
    })

    result = center_variables(df, vars_to_center=['var1', 'var2'])

    assert 'var1_c' in result.columns
    assert result['var1_c'].isna().all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
