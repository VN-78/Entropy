# region imports 
from fastmcp import FastMCP

# Domain And Infrastructure imports
from data_refinery.domain.models.dataset import DatasetOverview
from data_refinery.infrastructure.pandas_client import PandasDatasetClient


# region initialize mcp server
mcp = FastMCP("data-refinery")

client = PandasDatasetClient()

# region Inspect-data tool
@mcp.tool
def inspect_dataset(file_uri: str) -> DatasetOverview:
    """
    Reads a CSV file (local or S3) and returns a statistical summary.
    
    Args:
        file_uri: The path to the file. 
                  Use 's3://bucket/key.csv' for S3 
                  or '/absolute/path/to/local.csv' for local files.
    """

    # load the data 
    df = client.load_data(file_uri)

    # analyze the data 
    status = client.analyze(df)

    return status 

# region main
if __name__ == "__main__":
    mcp.run()

