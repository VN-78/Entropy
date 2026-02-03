import pytest
import pandas as pd
from data_refinery.domain.models.cleaning import CleaningOptions, DateColumnConfig
from data_refinery.infrastructure.pandas_client import PandasDatasetClient

def test_date_normalization_model():
    """Test that CleaningOptions correctly validates date_columns."""
    options = CleaningOptions(
        normalize_headers=True,
        strategies={},
        date_columns=[
            DateColumnConfig(column_name="joined_at", output_format="%d/%m/%Y")
        ]
    )
    assert options.date_columns[0].column_name == "joined_at"
    assert options.date_columns[0].output_format == "%d/%m/%Y"

def test_clean_dataset_date_normalization():
    """Test actual dataframe cleaning with date normalization."""
    client = PandasDatasetClient()
    
    # Create sample data
    # Note: 01/02/2023 is ambiguous, but pandas defaults to month-first (US) usually, 
    # or infers. 2023-01-01 is unambiguous.
    df = pd.DataFrame({
        "Created Date": ["2023-01-01", "2023-02-01", "invalid_date", None],
        "Value": [1, 2, 3, 4]
    })
    
    # Options: Normalize headers (Created Date -> created_date) + Date Normalization
    options = CleaningOptions(
        normalize_headers=True,
        strategies={},
        date_columns=[
            DateColumnConfig(column_name="created_date", output_format="%Y-%m-%d")
        ]
    )
    
    # Unpack tuple: (DataFrame, DatasetOverview)
    cleaned, _ = client.clean_dataset(df, options)
    
    # Check header normalization
    assert "created_date" in cleaned.columns
    
    # Check date values
    # "2023-01-01" -> "2023-01-01"
    assert cleaned["created_date"].iloc[0] == "2023-01-01"
    assert cleaned["created_date"].iloc[1] == "2023-02-01"
    
    # Invalid date should be NaT, and strftime usually keeps it as NaN/NaT
    # If the column became Object/String because of strftime, NaN might be present.
    assert pd.isna(cleaned["created_date"].iloc[2]) or cleaned["created_date"].iloc[2] == "NaT"
