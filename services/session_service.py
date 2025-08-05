from models.schemas import APIKeys, DatabaseFile
import uuid
from datetime import datetime

class SessionService:
    sessions = {}

    @staticmethod
    def create_session(api_keys: APIKeys) -> str:
        """create new session and store API keys"""
        session_id = "user_"+str(uuid.uuid4())[:8]
        SessionService.sessions[session_id] = {
            "api_keys": api_keys,
            "created_at": datetime.now(),
            "database_file": None
        }
        return session_id
    
    @staticmethod
    def get_api_keys(session_id: str) -> APIKeys:
        """Get api keys for a session"""
        if session_id not in SessionService.sessions:
            raise ValueError(f"Session {session_id} not found")
        return SessionService.sessions[session_id]["api_keys"]
    
    @staticmethod
    def update_database_file(session_id: str, db_file: DatabaseFile):
        """Assosiate database file with a session"""
        if session_id in SessionService.sessions:
            SessionService.sessions[session_id]["database_file"] = db_file
    