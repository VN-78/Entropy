from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.storage import storage_service
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file to the configured storage (MinIO/S3).
    Returns the 's3://' URI which can be passed to the Agent/MCP tools.
    """
    try:
        # Generate unique filename to prevent overwrites
        extension = file.filename.split(".")[-1] if "." in file.filename else "dat"
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        
        file_uri = await storage_service.upload_file(file, unique_name)
        
        return {
            "filename": file.filename,
            "stored_name": unique_name,
            "uri": file_uri,
            "message": "File uploaded successfully. Pass the 'uri' to the agent."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
