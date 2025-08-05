from fastapi import APIRouter, Depends, HTTPException
from services.query_service import QueryService
from services.file_service import FileService
from services.session_service import SessionService
from models.schemas import QueryRequest
import logging

# ✅ Configuration du logging pour voir les erreurs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ask-question/{session_id}")
async def ask_question(
    session_id: str,
    request: QueryRequest,
    file_service: FileService = Depends(),
    query_service: QueryService = Depends(),
    session_service: SessionService = Depends()
):
    try:
        logger.info(f"Processing question for session: {session_id}")
        logger.info(f"Question: {request.question}")
        
        # Récupérer les clés API de la session
        api_keys = session_service.get_api_keys(session_id)
        logger.info("API keys retrieved successfully")
        
        # Récupérer le fichier de base de données
        db_file = file_service.get_database_file(session_id)
        logger.info(f"Database file found: {db_file.file_path}")

        # Traiter la question
        result = await query_service.process_question(
            question=request.question,
            session_id=session_id,
            db_path=db_file.file_path,
            api_keys=api_keys
        )
        
        logger.info("Question processed successfully")
        return {
            "session_id": session_id,
            "question": request.question,
            "result": result
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")  # ✅ Affiche la stack trace complète
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
