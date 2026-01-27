# region imports 
from fastmcp import FastMCP

# Domain And Infrastructure imports
from data_refinery.domain.models.dataset import DatasetOverview
from data_refinery.infrastructure.pandas_client import PandasDatasetClient


# region initialize mcp server
mcp = FastMCP("data-refinery")

client = PandasDatasetClient()

@mcp.tool
def inspect_dataset(file_uri: str) -> DatasetOverview:
    """_summary_

    Args:
        file_uri (str): _description_

    Returns:
        DatasetOverview: _description_
    """