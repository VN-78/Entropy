import pytest
import pandas as pd
import numpy as np
from data_refinery.infrastructure.pandas_client import PandasDatasetClient

def test_analyze_numeric_stats():
    """
    Test that analyze calculates mean, std, min, max, and outliers for numeric columns.
    """
    # 1. Setup Data
    # 5 data points: 10, 20, 30, 40, 1000
    # Pandas default quantile is linear interpolation.
    data = {
        "age": [10, 20, 30, 40, 1000],  
        "name": ["A", "B", "C", "D", "E"]
    }
    df = pd.DataFrame(data)
    client = PandasDatasetClient()

    # 2. Run Analysis
    overview = client.analyze(df)
    
    # 3. Verify
    # Find the 'age' column profile
    age_col = next(c for c in overview.columns if c.name == "age")
    
    # Mean: (10+20+30+40+1000)/5 = 1100/5 = 220
    assert age_col.mean == 220.0
    assert age_col.min == 10.0
    assert age_col.max == 1000.0
    
    # Outlier calculation verification:
    # Q1 (25%) of [10, 20, 30, 40, 1000]
    # In pandas, quantile(0.25) depends on interpolation. Default is 'linear'.
    # ranks: 0->10, 1->20, 2->30, 3->40, 4->1000
    # 0.25 * (5-1) = 1.0 -> index 1 -> 20.
    # 0.75 * (5-1) = 3.0 -> index 3 -> 40.
    # IQR = 40 - 20 = 20.
    # Upper Bound = 40 + 1.5*20 = 70.
    # 1000 > 70 -> Outlier.
    assert age_col.outlier_count == 1
    
    # Check 'name' column (should be None for stats)
    name_col = next(c for c in overview.columns if c.name == "name")
    assert name_col.mean is None
    assert name_col.outlier_count is None

def test_analyze_all_nans():
    """Test behavior with all NaN column."""
    df = pd.DataFrame({"val": [None, None, None]})
    client = PandasDatasetClient()
    overview = client.analyze(df)
    
    col = overview.columns[0]
    # Mean of all NaNs is usually NaN, which we might have converted to None or kept as NaN.
    # In my code: `mean_val = float(series.mean()) if not pd.isna(series.mean()) else None`
    assert col.mean is None
    assert col.min is None

def test_analyze_mixed_types():
    """Test that it doesn't crash on mixed types."""
    # Pandas might treat this as object dtype
    df = pd.DataFrame({"mixed": [1, "two", 3.0]})
    client = PandasDatasetClient()
    overview = client.analyze(df)
    
    col = overview.columns[0]
    # Since it's object dtype, is_numeric_dtype should be false
    assert col.data_type == "object"
    assert col.mean is None
