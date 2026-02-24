# region imports
import pandas as pd
import io
import os
from typing import Any, Tuple, Optional
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
    
    def _get_storage_options(self) -> Optional[dict]:
        """Returns storage options for s3fs/boto3 if S3 config is present in env."""
        endpoint = os.environ.get("S3_ENDPOINT_URL")
        key = os.environ.get("S3_ACCESS_KEY")
        secret = os.environ.get("S3_SECRET_KEY")
        
        if endpoint and key and secret:
            return {
                "client_kwargs": {"endpoint_url": endpoint},
                "key": key,
                "secret": secret
            }
        return None

    def load_data(self, file_uri) -> pd.DataFrame:
        """
        Smart loader: checks if URI is S3 or Local, and handles CSV or Parquet.
        """
        storage_opts = self._get_storage_options() if file_uri.startswith("s3://") else None
        
        if file_uri.endswith(".parquet"):
            return pd.read_parquet(file_uri, storage_options=storage_opts)
        else:
            # Default to CSV
            return pd.read_csv(file_uri, storage_options=storage_opts)

    def save_dataframe(self, df: pd.DataFrame, file_uri: str):
        """
        Smart saver: saves to local or S3 based on URI.
        """
        if file_uri.startswith("s3://"):
            storage_opts = self._get_storage_options()
            df.to_parquet(file_uri, storage_options=storage_opts)
        else:
            # Ensure parent dir exists for local files
            os.makedirs(os.path.dirname(file_uri), exist_ok=True)
            df.to_parquet(file_uri)

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

    def clean_dataset(self, df: pd.DataFrame, options: CleaningOptions) -> Tuple[pd.DataFrame, DatasetOverview]:
        """
        Applies cleaning rules to the dataset.
        Returns the cleaned DataFrame and its new quality overview.
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

        # 2. Date Normalization
        if options.date_columns:
            for date_cfg in options.date_columns:
                col = date_cfg.column_name
                if col in df.columns:
                    try:
                        # Convert to datetime objects first (handles various input formats)
                        # errors='coerce' turns unparseable strings into NaT
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        
                        # Apply target string format
                        # Note: This converts the column to Object/String type
                        if date_cfg.output_format:
                            df[col] = df[col].dt.strftime(date_cfg.output_format)
                    except Exception:
                        # If a column is completely incompatible, we skip it to prevent crashing
                        pass

        # 3. Apply Column-Specific Strategies
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

        # 4. Generate Quality Report for the Cleaned Data
        overview = self.analyze(df)

        return df, overview