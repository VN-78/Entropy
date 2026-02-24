# region imports 
import duckdb
import uuid
import os
from pathlib import Path
from typing import Dict, List, Any

# model imports 
from data_refinery.domain.models.sql import SQLQueryResponse

# region DuckDB client
class DuckDBClient:
    """
    Infrastructure service for executing SQL transformations.

    Responsibilities:
    1. Execute SQL queries safely.
    2. Manage the lifecycle of result artifacts (files).
    3. Map raw database results to Domain Models.
    """

    def __init__(self, artifact_dir: str = "/home/vn-78/VN_78/Programming/Personal/Projects/Final-Year-Project/Entropy/test/temp"):
        """
        Ensures that an folder is availabe to store the Generated file
        
        Args:
            artifact_dir: Where we save the results of queries.
        """
        self.artifact_path = Path(artifact_dir)
        # Ensure the directory exists; fail loudly if we don't have permissions
        try:
            self.artifact_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise RuntimeError(f"Critical: Cannot write to artifact directory: {artifact_dir}")

    def _configure_s3(self, conn: duckdb.DuckDBPyConnection):
        """Configures the DuckDB connection for S3 access if credentials exist."""
        endpoint = os.environ.get("S3_ENDPOINT_URL")
        key = os.environ.get("S3_ACCESS_KEY")
        secret = os.environ.get("S3_SECRET_KEY")
        
        if endpoint and key and secret:
            try:
                # Install/Load httpfs extension for S3 support
                conn.execute("INSTALL httpfs; LOAD httpfs;")
                
                # Configure S3/MinIO
                conn.execute(f"SET s3_endpoint='{endpoint.replace('http://', '').replace('https://', '')}';")
                conn.execute(f"SET s3_access_key_id='{key}';")
                conn.execute(f"SET s3_secret_access_key='{secret}';")
                conn.execute("SET s3_url_style='path';")
                conn.execute("SET s3_use_ssl=false;") # Assumes local MinIO without SSL
            except Exception as e:
                # Log or ignore if extension fails? Better to warn.
                print(f"Warning: Failed to configure S3 for DuckDB: {e}")

    def execute_and_write(self, sql_query: str) -> SQLQueryResponse:
        """
        Executes a SQL query and materializes the result to a Parquet file.

        This method creates an ephemeral DuckDB connection to run the provided
        SQL query. It calculates metadata (row/column counts), samples the data,
        and saves the full result set to the configured artifact directory.

        Args:
            sql_query: A raw SQL query string. Must use valid DuckDB syntax
            and reference files directly (e.g., "SELECT * FROM 'file.csv'").

        Returns:
            SQLQueryResponse: An object containing execution status, metadata
            (row/column counts), sample data, and the URI of the saved
            Parquet file.

        Raises:
            ValueError: If the SQL syntax is malformed.
            FileNotFoundError: If the query references a file or table that
            does not exist.
            RuntimeError: If an unexpected error occurs during execution or
            file writing.
        """
        # 1. Ephemeral Connection
        # We create a new connection per request to ensure isolation.
        # DuckDB handles this very cheaply.
        conn = duckdb.connect(database=':memory:')
        
        # Configure S3 if needed
        self._configure_s3(conn)

        try:
            # 2. Lazy Execution
            # conn.sql() creates a "Relation" - it validates syntax but 
            # doesn't load all data into Python memory yet.
            relation = conn.sql(sql_query)

            # 3. Validation (The "Peek" Phase)
            # We fetch basic stats immediately. 
            # Note: For massive data, count() is expensive, but necessary here.
            row_count = relation.shape[0]
            col_count = relation.shape[1]
            columns = relation.columns

            # 4. Sampling
            # limit(5) ensures we only fetch 5 rows into Python memory
            sample_rows = relation.limit(5).fetchall()
            
            # Convert tuples [('Value', 10), ...] to Dicts [{'col': 'Value', ...}]
            # This is required because Pydantic expects List[Dict]
            sample_data: List[Dict[str, Any]] = [
                dict(zip(columns, row)) for row in sample_rows
            ]

            # 5. Materialization (The "Write" Phase)
            # Generate a unique ID for this result artifact
            file_id = uuid.uuid4().hex[:8]
            output_filename = f"result_{file_id}.parquet"
            output_uri = self.artifact_path / output_filename

            # Write to Parquet (High performance, type-safe)
            relation.write_parquet(str(output_uri))

            # 6. Return the Contract
            return SQLQueryResponse(
                status=True,
                total_rows=row_count,
                total_columns=col_count,
                sample_data=sample_data,
                result_uri=str(output_uri)
            )

        except duckdb.ParserException as e:
            # Malformed SQL
            raise ValueError(f"SQL Syntax Error: {str(e)}")
        except duckdb.CatalogException as e:
            # Missing file or table
            raise FileNotFoundError(f"Data Access Error: {str(e)}")
        except Exception as e:
            # Catch-all for unexpected system failures
            raise RuntimeError(f"Execution Failed: {str(e)}")
        finally:
            # Clean up the connection to free memory
            conn.close()
