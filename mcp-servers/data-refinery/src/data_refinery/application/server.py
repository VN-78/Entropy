# region imports 
from mcp.server.fastmcp import FastMCP

# Domain And Infrastructure imports
from data_refinery.domain.models.dataset import DatasetOverview
from data_refinery.domain.models.sql import SQLQueryResponse
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
    Executes a SQL query on a dataset using DuckDB.
    
    Args:
        file_uri: The absolute path to the file.
        sql_query: The SQL query string. MUST use the file path logic:
                   SELECT * FROM 'path/to/file.csv' WHERE age > 30
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


# region main
if __name__ == "__main__":
    mcp.run(transport="stdio")

