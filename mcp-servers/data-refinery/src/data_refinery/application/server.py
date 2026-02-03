# region imports 
from mcp.server.fastmcp import FastMCP
import uuid
from pathlib import Path
from typing import Dict, List, Any

# Domain And Infrastructure imports
from data_refinery.domain.models.dataset import DatasetOverview
from data_refinery.domain.models.sql import SQLQueryResponse
from data_refinery.domain.models.cleaning import CleaningOptions, CleaningResponse
from data_refinery.infrastructure.pandas_client import PandasDatasetClient
from data_refinery.infrastructure.duckdb_client import DuckDBClient


# region initialize mcp server
mcp = FastMCP(
    name = "data-refinery",
    # host = "localhost", provide host and port in the run command instead
    # port = 8050,
    )

client = PandasDatasetClient()
db_client = DuckDBClient()

# region Inspect-data tool  
@mcp.tool()
def inspect_dataset(file_uri: str) -> DatasetOverview:
    """
    Inspects a CSV dataset to understand its structure, schema, and data quality.
    
    CRITICAL: Always run this tool FIRST before performing any analysis or visualization 
    to understand column names and types.

    It calculates:
    - Row/Column counts
    - Missing value percentages (to identify dirty data)
    - Data types for every column
    - Basic statistics for numeric columns (mean, std, min, max, outlier counts)
    - A sample of 5 rows to understand context
    
    Args:
        file_uri: The absolute path to the file. 
            - Local: '/home/user/data/file.csv'
            - S3: 's3://my-bucket/data.csv'
    """

    # load the data 
    df = client.load_data(file_uri)

    # analyze the data 
    status = client.analyze(df)

    return status

# region run_sql_query tool
@mcp.tool()
def run_sql_query(file_uri: str, sql_query: str) -> SQLQueryResponse:
    """
    Executes a SQL query against a file and saves the result to a new file.

    Use this tool to filter, sort, or aggregate data.
    
    CRITICAL SYNTAX RULES:
    1. The query MUST reference the 'file_uri' directly in the FROM clause.
    2. DO NOT use generic table names like 'users' or 'data'.
    3. The tool returns a 'result_uri' (path to the new file), NOT the full data.

    Args:
        file_uri: The absolute path to the source file (e.g., '/app/data.csv').
        sql_query: The DuckDB SQL query string.
        
    Examples:
        Correct: "SELECT name, age FROM '/app/data.csv' WHERE age > 25"
        Incorrect: "SELECT name, age FROM users WHERE age > 25"
    """
    # 1. Input Integrity Check
    if file_uri not in sql_query:
        # Fail fast if the agent forgot to include the file path
        raise ValueError(
            f"Invalid Query: You must select directly from the file path. "
            f"Expected: SELECT ... FROM '{file_uri}' ..."
        )

    # 2. Execution Delegation
    try:
        response = db_client.execute_and_write(sql_query)
        return response
    except Exception as e:
        # In MCP, raising an exception usually returns a clear error to the client.
        # This is better than returning a partial "success=False" object.
        raise RuntimeError(f"Tool Execution Error: {str(e)}")


# region clean_data_tool
@mcp.tool()
def clean_dataset(file_uri: str, options: CleaningOptions) -> CleaningResponse:
    """
    Apply data cleaning operations (imputation, normalization) to a dataset.

    This tool loads a file, applies the specified 'CleaningOptions', and saves 
    the result to a new Parquet file. It is the PRIMARY way to handle missing 
    values (NaNs) and inconsistent headers.

    Args:
        file_uri: The absolute path to the input file (e.g., 's3://bucket/raw.csv').
        options: A CleaningOptions object containing the specific rules.
            The 'strategies' dictionary maps column names to actions:
            - "drop": Remove rows.
            - "mean": Fill with average (numeric only).
            - "mode": Fill with most frequent (text/numeric).
            - "zero": Fill with 0 (numeric only).
            - "unknown": Fill with 'Unknown' (text only).

    Returns:
        CleaningResponse: Metadata about the cleaned file (row count, new path).
    """
    try:
        # 1. Load the data
        df = client.load_data(file_uri)
        
        # 2. Apply the cleaning logic (The function you just wrote)
        cleaned_df = client.clean_dataset(df, options)
        
        # 3. Save Artifact (Pass-by-Reference)
        # We generate a unique ID so we don't overwrite previous work
        file_id = uuid.uuid4().hex[:8]
        output_filename = f"cleaned_{file_id}.parquet"
        
        # Ensure the directory exists (using your configured temp path)
        output_path = Path("/home/vn-78/VN_78/Programming/Personal/Projects/Final-Year-Project/Entropy/test/temp") / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as Parquet (preserves the new clean schema)
        cleaned_df.to_parquet(output_path)
        
        # 4. Return the DISTINCT CleaningResponse
        return CleaningResponse(
            status=True,
            total_rows=len(cleaned_df),
            total_columns=len(cleaned_df.columns),
            sample_data=cleaned_df.head(5).to_dict(orient='records'),
            result_uri=str(output_path)
        )

    except Exception as e:
        raise RuntimeError(f"Cleaning Failed: {str(e)}")

# region main
if __name__ == "__main__":
    mcp.run(transport="stdio")

