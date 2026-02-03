from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BaseDatasetInfo(BaseModel):
    """
    Fundamental metadata shared by all dataset operations.
    
    This base model captures the essential 'shape' and content preview of a dataset,
    allowing downstream tools (like SQL results or full inspections) to provide 
    immediate context without requiring redundant tool calls.
    """
    total_rows: int = Field(..., description="Total number of rows in the dataset")
    total_columns: int = Field(..., description="Total number of columns in the dataset")

    # We use List[Dict[str, Any]] to represent generic JSON rows
    sample_data: List[Dict[str, Any]] = Field(..., description="A sample of the first 5 rows")

class ColumnProfile(BaseModel):
    """
    Summarizes the statistical properties of a single column.

    Attributes:
        name: The header name of the column.
        data_type: The simplified Python type (e.g., 'int', 'float', 'string').
        missing_percentage: The ratio of null values to total rows (0-100).
        mean: The average value (numeric columns only).
        std: The standard deviation (numeric columns only).
        min: The minimum value (numeric columns only).
        max: The maximum value (numeric columns only).
        outlier_count: Number of potential outliers (1.5 * IQR rule).
    """
    name: str = Field(..., description="The Name of the Column")
    data_type: str = Field(..., description="The simplified data type (e.g, 'int', 'string')")
    missing_percentage: float = Field(..., description="Percentage of Missing values (0.0 to 100.0)")
    
    # New Statistical Fields (Optional, as they don't apply to text)
    mean: Optional[float] = Field(None, description="Average value for numeric columns")
    std:  Optional[float] = Field(None, description="Standard deviation for numeric columns")
    min:  Optional[float] = Field(None, description="Minimum value")
    max:  Optional[float] = Field(None, description="Maximum value")
    outlier_count: Optional[int] = Field(None, description="Count of values outside 1.5 * IQR range")


class DatasetOverview(BaseDatasetInfo):
    """
    Represents the high-level health check of a dataset.

    This model serves as the primary output for the 'inspect_dataset' tool,
    providing the LLM with enough context to decide on next steps (cleaning,
    filtering, or visualization).
    """
    columns: List[ColumnProfile] = Field(..., description="Detailed stats for each column")

