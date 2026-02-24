import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import UploadFile
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.s3 = boto3.client('s3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        except ClientError:
            try:
                self.s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
                logger.info(f"Created bucket: {settings.S3_BUCKET_NAME}")
            except Exception as e:
                logger.error(f"Failed to create bucket: {e}")

    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        """
        Uploads a file to S3/MinIO and returns the s3:// URI.
        """
        try:
            self.s3.upload_fileobj(file.file, settings.S3_BUCKET_NAME, object_name)
            # Return standard s3 URI format
            return f"s3://{settings.S3_BUCKET_NAME}/{object_name}"
        except NoCredentialsError:
            raise Exception("S3 Credentials not available")
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise Exception(f"Upload failed: {str(e)}")

storage_service = StorageService()
