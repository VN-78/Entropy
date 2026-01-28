from pydantic import BaseModel, Field
from typing import List, Dict, Any
from data_refinery.domain.models.dataset import BaseDatasetInfo

class SQLQueryRequest(BaseModel):
    """
    Defines the strict contract for running SQL transformations.
    
    This model ensures the Agent provides both the target file and 
    a valid DuckDB-compatible query string.
    """

    file_uri : str = Field(..., description="The absolute path to the file (e.g., '/app/data.csv' or 's3://bucket/data.csv').")

    sql_query : str = Field(..., description="The raw SQL query to execute. CRITICAL: You must use DuckDB's direct file querying syntax (e.g., SELECT * FROM 'path/to/file.csv'). Do NOT use table names.")


class SQLQueryResponse(BaseDatasetInfo):
    """
    Standardized output for a SQL transformation operation.
    
    This model inherits from BaseDatasetInfo to provide immediate context 
    (row count, preview) while also returning the location of the 
    fully processed file (Pass-by-Reference).
    """

    status : bool = Field(..., description="Status of the Query Execution Completed or Failed")

    result_uri : str = Field(..., description="The File Path of the resulting processed file")