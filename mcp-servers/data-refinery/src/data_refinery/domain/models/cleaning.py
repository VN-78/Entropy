from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional
from data_refinery.domain.models.dataset import BaseDatasetInfo, DatasetOverview

# We define the valid strategies as a Type for clarity
# This helps IDEs and future developers know what strings are allowed
CleaningStrategy = Literal["drop", "zero", "mean", "mode", "unknown"]

class DateColumnConfig(BaseModel):
    """
    Configuration for standardizing date columns.
    
    Attributes:
        column_name: The name of the column to parse.
        output_format: The desired output format (default: YYYY-MM-DD).
    """
    column_name: str = Field(..., description="The name of the column to parse.")
    output_format: str = Field("%Y-%m-%d", description="The desired output format (default: YYYY-MM-DD).")

class CleaningOptions(BaseModel):
    """
    Configuration instructions for the data cleaning engine.

    This model enforces strict validation on the cleaning strategies to ensure
    downstream tools do not receive ambiguous instructions.

    Attributes:
        normalize_headers (bool): If True, renames columns to snake_case
            (e.g., 'First Name' -> 'first_name'). Defaults to True.
        strategies (Dict[str, CleaningStrategy]): A dictionary mapping column
            names to their specific cleaning action.
        date_columns (List[DateColumnConfig]): A list of columns to convert to 
            standard date format.
    
    Example:
        >>> options = CleaningOptions(
        ...     normalize_headers=True,
        ...     strategies={"age": "mean", "email": "drop"},
        ...     date_columns=[{"column_name": "created_at", "output_format": "%Y-%m-%d"}]
        ... )
    """
    normalize_headers: bool = Field(
        True, 
        description="If True, Convert columns headers to snake_case (e.g., 'First Name' -> 'first_name')."
    )
    
    strategies: Dict[str, CleaningStrategy] = Field(
        ...,
        description=(
            "A dictionary mapping column names to cleaning strategies.\n"
            "Valid strategies:\n"
            "- 'drop': Remove rows with missing values in this column.\n"
            "- 'zero': Fill missing values with 0 (Numeric only).\n"
            "- 'mean': Fill with the column average (Numeric only).\n"
            "- 'mode': Fill with the most frequent value (Good for Text/Category).\n"
            "- 'unknown': Fill with the string 'Unknown' (Text only)."
        ),
        json_schema_extra={"example":{"age": "mean", "email": "drop", "city": "mode"}}
    )
    
    date_columns: Optional[list[DateColumnConfig]] = Field(
        None,
        description="List of columns to convert to standard date format."
    )
    
class CleaningResponse(DatasetOverview):
    """
    Standardized output for a data cleaning operation.

    This model encapsulates the result of applying cleaning strategies (imputation,
    normalization, etc.) to a dataset. It inherits from DatasetOverview to provides 
    immediate feedback on the dataset's new shape (row count, sample data, and column stats) 
    while pointing the Agent to the persisted artifact.

    Attributes:
        status: Indicates if the cleaning process completed successfully.
        result_uri: The absolute file path to the newly saved, cleaned Parquet file.
    """
    
    status : bool = Field(..., description="Status of the Cleaning process (True=Success, False=Failed)")
    result_uri : str = Field(..., description="The absolute path to the cleaned file (e.g., '/tmp/cleaned_data.parquet')")