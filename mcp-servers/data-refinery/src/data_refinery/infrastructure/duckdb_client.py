# region imports 
import duckdb
import uuid
from pathlib import Path
from typing import Dict, List, Any


# region DuckDB client

# This creates an in-memory database connection
# It disappears when the script ends
conn = duckdb.connect(database=':memory:')

class DuckDBClient:
    """
    Handles ephemeral SQL execution using DuckDB.
    """

