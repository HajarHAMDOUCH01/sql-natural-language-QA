from fastapi import APIRouter, Depends, HTTPException
from services.query_service import QueryService
from services.file_service import FileService
from services.session_service import SessionService
from models.schemas import QueryRequest

router = APIRouter()

@router.post("/ask-question/{session_id}")
async def ask_question(
    session_id: str,
    request: QueryRequest,
    file_service: FileService = Depends(),
    query_service: QueryService = Depends(),
    session_service: SessionService = Depends()
):
    api_keys = session_service.get_api_keys(session_id)
    db_file = file_service.get_database_file(session_id)

    result = await query_service.process_question(
        question=request.question,
        session_id=session_id,
        db_path=db_file.file_path,
        api_keys=api_keys
    )

    return {
        "session_id": session_id,
        "question": request.question,
        "result": result
    }