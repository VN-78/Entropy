# region imports
import pandas as pd
import io
import boto3
from typing import Any
from urllib.parse import urlparse

# Domain Imports
from data_refinery.domain.interfaces.repository import IDatasetRepository
from data_refinery.domain.models.dataset import DatasetOverview, ColumnProfile
from data_refinery.domain.models.cleaning import CleaningOptions

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
            series = df[col_name]
            
            # 1. Map Pandas Dtypes to simple strings
            dtype = str(series.dtype)
            
            # 2. Calculate Missing %
            missing_count = series.isnull().sum()
            total_count = len(df)
            missing_pct = (missing_count / total_count) * 100 if total_count > 0 else 0.0

            # 3. Calculate Stats for Numeric Columns
            mean_val = None
            std_val = None
            min_val = None
            max_val = None
            outlier_count = None

            if pd.api.types.is_numeric_dtype(series):
                # Calculate basic stats (convert to native python float for JSON serialization)
                try:
                    mean_val = float(series.mean()) if not pd.isna(series.mean()) else None
                    std_val = float(series.std()) if not pd.isna(series.std()) else None
                    min_val = float(series.min()) if not pd.isna(series.min()) else None
                    max_val = float(series.max()) if not pd.isna(series.max()) else None
                    
                    # Calculate Outliers (IQR Method)
                    # We drop NAs for quantile calculation to avoid issues
                    valid_data = series.dropna()
                    if not valid_data.empty:
                        Q1 = valid_data.quantile(0.25)
                        Q3 = valid_data.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        # Count values outside bounds
                        outliers = valid_data[(valid_data < lower_bound) | (valid_data > upper_bound)]
                        outlier_count = int(len(outliers))
                except Exception:
                    # Fallback for edge cases (e.g. all NaNs or mixed types that tricked the check)
                    pass

            columns.append(ColumnProfile(
                name=col_name,
                data_type=dtype,
                missing_percentage=round(missing_pct, 2),
                mean=mean_val,
                std=std_val,
                min=min_val,
                max=max_val,
                outlier_count=outlier_count
            ))

        # 4. Create Sample Rows (handle NaN values for JSON safety)
        # replace(float('nan'), None) ensures JSON compatibility
        sample = df.head(5).replace({float('nan'): None}).to_dict(orient='records')

        return DatasetOverview(
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=columns,
            sample_data=sample
        )

# region clean data 

    def clean_dataset(self, df: pd.DataFrame, options: CleaningOptions) -> pd.DataFrame:
        """
        Applies cleaning rules to the dataset.
        Returns the cleaned DataFrame (does NOT save to file yet).
        """
        # 1. Normalize Headers (Global Rule)
        if options.normalize_headers:
            # - Strip whitespace
            # - Lowercase
            # - Replace spaces with underscores
            # - Remove special characters (keep only alphanumeric and underscores)
            df.columns = (df.columns
                .str.strip()
                .str.lower()
                .str.replace(r'\s+', '_', regex=True)
                .str.replace(r'[^\w]', '', regex=True))

        # 2. Apply Column-Specific Strategies
        for column, strategy in options.strategies.items():
            if column not in df.columns:
                continue  # Skip columns that don't exist (safety check)

            # Strategy: DROP ROW
            if strategy == "drop":
                df = df.dropna(subset=[column])

            # Strategy: FILL ZERO
            elif strategy == "zero":
                # Only apply to numeric columns to prevent errors
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(0)

            # Strategy: FILL MEAN
            elif strategy == "mean":
                if pd.api.types.is_numeric_dtype(df[column]):
                    mean_val = df[column].mean()
                    df[column] = df[column].fillna(mean_val)

            # Strategy: FILL MODE (Most Frequent)
            elif strategy == "mode":
                # mode() returns a Series (there can be ties), so we take the first one ([0])
                if not df[column].mode().empty:
                    mode_val = df[column].mode()[0]
                    df[column] = df[column].fillna(mode_val)

            # Strategy: FILL UNKNOWN
            elif strategy == "unknown":
                # Usually for text columns
                df[column] = df[column].fillna("Unknown")

        return df  # TODO also return the current quality of the data just like in the inspect dataset tool  