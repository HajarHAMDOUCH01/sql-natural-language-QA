from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from services.file_service import FileService
from services.session_service import SessionService
from models.schemas import UploadResponse, DatabaseFile, UploadRequest, APIKeys
import uuid, json

router = APIRouter()

@router.post("/upload-database", response_model=UploadResponse)
async def upload_database(
        api_keys_json: str = Form(..., alias="api_keys"),
        file: UploadFile = File(...),
        file_service: FileService = Depends(),
        session_service: SessionService = Depends()  # ✅ Utilisez l'instance
):
    try:
        # creating a session with api keys 
        api_keys_data = json.loads(api_keys_json)
        api_keys = APIKeys(**api_keys_data)  # ✅ Créez l'objet APIKeys correctement
        
        session_id = session_service.create_session(api_keys)  # ✅ Utilisez l'instance
        if session_id: 
            print("user session saved in self.sessions")
        else: 
            print("user not saved in self sessions")
        
        db_file = await file_service.save_uploaded_database(file, session_id)
        session_service.update_database_file(session_id, db_file)  # ✅ Utilisez l'instance
        
        return UploadResponse(
            session_id=session_id,
            filename=file.filename,
            message=f"Database '{file.filename}' uploaded successfully",
            file_info = db_file
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for api_keys")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")