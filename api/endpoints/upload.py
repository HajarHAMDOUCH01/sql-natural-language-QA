from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from services.file_service import FileService
from services.session_service import session_service
from models.schemas import UploadResponse, DatabaseFile, UploadRequest
import uuid

router = APIRouter()

@router.post("/upload-database", response_model=UploadResponse)
async def upload_database(
        request: UploadRequest,
        file: UploadFile = File(...),
        file_service: FileService = Depends()
):
    # creating a session with api keys 
    session_id = session_service.create_session(request.api_keys)
    db_file = await file_service.save_uploaded_database(file, session_id)
    session_service.update_database_file(session_id, db_file)
    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        message=f"Database '{file.filename} uploaded successfully'",
        file_info = db_file
    )
