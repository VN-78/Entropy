# region imports 
from mcp.server.fastmcp import FastMCP

# Domain And Infrastructure imports
from data_refinery.domain.models.dataset import DatasetOverview
from data_refinery.infrastructure.pandas_client import PandasDatasetClient


# region initialize mcp server
mcp = FastMCP(
    name = "data-refinery",
    # host = "localhost", provide host and port in the run command instead
    # port = 8050,
    )

client = PandasDatasetClient()

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

# region main
if __name__ == "__main__":
    mcp.run(transport="stdio")

