# region imports
import pandas as pd
import io
import boto3
from typing import Any
from urllib.parse import urlparse

# Domain Imports
from data_refinery.domain.interfaces.repository import IDatasetRepository
from data_refinery.domain.models.dataset import DatasetOverview, ColumnProfile

# region load_data  
class PandasDatasetClient(IDatasetRepository):
    """
    Implementation to load Data from both local files and S3 URLs using pandas as the engine
    """
    def load_data(self, file_uri) -> pd.DataFrame:
        """
        Smart loader: checks if URI is S3 or Local.
        """
        if file_uri.startswith("s3://"):
            return self._load_from_s3(file_uri)
        else:
            return pd.read_csv(file_uri)
        
    def _load_from_s3(self, s3_uri) -> pd.DataFrame:
        """Private helper to handle AWS S3 streaming."""
        # Parse s3://bucket/key
        parsed = urlparse(s3_uri)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        
        # Initialize Boto3 client (assumes you have ~/.aws/credentials set up)
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)
        
        # Read the stream directly into Pandas
        return pd.read_csv(io.BytesIO(obj['Body'].read()))

# region analyze data 

    def analyze(self, df: pd.DataFrame) -> DatasetOverview:
        """
        The 'Business Logic'. 
        Converts raw DataFrame -> Clean Domain Model.
        """
        columns = []
        
        for col_name in df.columns:
            # 1. Map Pandas Dtypes to simple strings
            dtype = str(df[col_name].dtype)
            
            # 2. Calculate Missing %
            missing_count = df[col_name].isnull().sum()
            total_count = len(df)
            missing_pct = (missing_count / total_count) * 100 if total_count > 0 else 0.0

            columns.append(ColumnProfile(
                name=col_name,
                data_type=dtype,
                missing_percentage=round(missing_pct, 2)
            ))

        # 3. Create Sample Rows (handle NaN values for JSON safety)
        # replace(float('nan'), None) ensures JSON compatibility
        sample = df.head(5).replace({float('nan'): None}).to_dict(orient='records')

        return DatasetOverview(
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=columns,
            sample_data=sample
        )