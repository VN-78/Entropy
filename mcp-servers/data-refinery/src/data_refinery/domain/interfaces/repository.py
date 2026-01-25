from abc import ABC, abstractmethod
import pandas as pd

class IDatasetRepository(ABC):
    """
    Interface for dataset data access. 
    
    This enforces that any concrete implementation (S3, Local) 
    must provide these specific methods.
    """

    @abstractmethod
    def load_data(self, file_uri: str) -> pd.DataFrame:
        """
        Loads data from a given URI into a Pandas DataFrame.
        
        Args:
            file_uri: The source path (e.g., 's3://bucket/file.csv' or 'local/path.csv')
            
        Returns:
            pd.DataFrame: The loaded data.
        """
        pass