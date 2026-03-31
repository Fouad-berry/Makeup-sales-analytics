"""
tests/test_pipeline.py — Tests unitaires du pipeline ELT
"""

import pandas as pd
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_df():
    """Dataset minimal pour les tests."""
    return pd.DataFrame({
        "Sale_ID": [1, 2, 2, 3, 4],           # doublon sur 2
        "Date": ["2025-01-01", "2025-02-01", "2025-02-01", "2025-03-01", "2025-04-01"],
        "Brand": ["MAC", "Dior", "Dior", "NARS", "L'Oreal"],
        "Product_Type": ["lipstick", "Blush", "Blush", "Mascara", "eyeliner"],
        "Country": ["France", "UK", "UK", "USA", "Germany"],
        "Sales_Channel": ["Online", "Mall", "Mall", "Retail Store", "Online"],
        "Payment_Method": ["Card", "Cash", "Cash", "Digital Wallet", "Card"],
        "Price_USD": [50.0, 80.0, 80.0, -5.0, 30.0],   # prix négatif sur 4
        "Units_Sold": [10, 5, 5, 20, 15],
        "Revenue_USD": [500.0, 400.0, 400.0, -100.0, 450.0],
    })


class TestClean:
    def test_removes_duplicates(self, sample_df):
        from elt.transform.transform import clean
        result = clean(sample_df)
        assert result["Sale_ID"].duplicated().sum() == 0

    def test_removes_negative_price(self, sample_df):
        from elt.transform.transform import clean
        result = clean(sample_df)
        assert (result["Price_USD"] <= 0).sum() == 0

    def test_removes_negative_revenue(self, sample_df):
        from elt.transform.transform import clean
        result = clean(sample_df)
        assert (result["Revenue_USD"] <= 0).sum() == 0

    def test_capitalizes_product_type(self, sample_df):
        from elt.transform.transform import clean
        result = clean(sample_df)
        for val in result["Product_Type"]:
            assert val == val.capitalize()


class TestEnrich:
    def test_adds_temporal_columns(self, sample_df):
        from elt.transform.transform import clean, enrich
        df = enrich(clean(sample_df))
        for col in ["Year", "Month", "Quarter", "Month_Name", "Day_of_Week"]:
            assert col in df.columns

    def test_adds_price_segment(self, sample_df):
        from elt.transform.transform import clean, enrich
        df = enrich(clean(sample_df))
        assert "Price_Segment" in df.columns
        assert df["Price_Segment"].notnull().all()

    def test_revenue_per_unit_positive(self, sample_df):
        from elt.transform.transform import clean, enrich
        df = enrich(clean(sample_df))
        assert (df["Revenue_Per_Unit"] > 0).all()

    def test_quarter_values(self, sample_df):
        from elt.transform.transform import clean, enrich
        df = enrich(clean(sample_df))
        valid_quarters = {"Q1", "Q2", "Q3", "Q4"}
        assert set(df["Quarter"].unique()).issubset(valid_quarters)


class TestDataQuality:
    def test_no_null_in_key_columns(self, sample_df):
        from elt.transform.transform import clean
        df = clean(sample_df)
        for col in ["Brand", "Product_Type", "Country", "Revenue_USD"]:
            assert df[col].isnull().sum() == 0

    def test_revenue_equals_price_times_units(self, sample_df):
        """Vérifie la cohérence prix × unités ≈ revenue."""
        from elt.transform.transform import clean
        df = clean(sample_df)
        computed = (df["Price_USD"] * df["Units_Sold"]).round(2)
        diff = abs(computed - df["Revenue_USD"].round(2))
        # tolérance de 1% (arrondi possible)
        assert (diff / df["Revenue_USD"] < 0.01).all()