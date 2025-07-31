from models.schemas import APIKeys, DatabaseFile
import uuid
from datetime import datetime

class SessionService:
    def __init__(self):
        self.sessions = {}

    def create_session(self, api_keys: APIKeys) -> str:
        """create new session and store API keys"""
        session_id = "user_"+str(uuid.uuid4())[:8]
        self.sessions[session_id] = {
            "api_keys": api_keys,
            "created_at": datetime.now(),
            "database_file": None
        }
        return session_id
    
    def get_api_keys(self, session_id: str) -> APIKeys:
        """Get api keys for a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]["api_keys"]
    
    def update_database_file(self, session_id: str, db_file: DatabaseFile):
        """Assosiate database file with a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["database_file"] = db_file
    