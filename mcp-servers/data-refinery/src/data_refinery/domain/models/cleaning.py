from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional

# We define the valid strategies as a Type for clarity
# This helps IDEs and future developers know what strings are allowed
CleaningStrategy = Literal["drop", "zero", "mean", "mode", "unknown"]

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
    
    Example:
        >>> options = CleaningOptions(
        ...     normalize_headers=True,
        ...     strategies={"age": "mean", "email": "drop"}
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
        example={"age": "mean", "email": "drop", "city": "mode"}
    )
    
    