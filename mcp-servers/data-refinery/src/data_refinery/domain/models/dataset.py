from pydantic import BaseModel, Field
from typing import List, Dict, Any


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
    """
    name: str = Field(..., description="The Name of the Column")
    data_type: str = Field(..., description="The simplified data type (e.g, 'int', 'string')")
    missing_percentage: float = Field(..., description="Percentage of Missing values (0.0 to 100.0)")

class DatasetOverview(BaseDatasetInfo):
    """
    Represents the high-level health check of a dataset.

    This model serves as the primary output for the 'inspect_dataset' tool,
    providing the LLM with enough context to decide on next steps (cleaning,
    filtering, or visualization).
    """
    columns: List[ColumnProfile] = Field(..., description="Detailed stats for each column")

