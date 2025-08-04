import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
from models.schemas import DatabaseFile
from langchain_community.utilities import SQLDatabase

class FileService:
    def __init__(self):
        self.storage_dir = Path("storage/databases")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def save_uploaded_database(self, file: UploadFile, session_id: str) -> DatabaseFile:
        """save the uploaded database file file to a session specific folder"""
        # concatenation de chemins de fichiers 
        session_folder = self.storage_dir / f"session_{session_id}"
        session_folder.mkdir(exist_ok=True)

        file_name = file.filename
        file_path = session_folder / file_name

        content = await file.read()
        file_size = len(content)

        #ouvrir le fichier dans le mode d'ecriture binaire
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        if not self._is_valid_sqlite(file_path):
            os.remove(file_path)
            raise ValueError(f"'{file_name}' is not a valid SQLite database")
        db_file = DatabaseFile(
            file_name = file_name,
            session_id=session_id,
            file_size = file_size,
            upload_timestamp = datetime.now(),
            file_path = str(file_path)
        )
        return db_file
    
    def get_database_file(self, session_id: str, filename: str = None) -> DatabaseFile:
        """
        Get database file info for session
        If filename not provided, look for any .db file in the session folder
        """
        session_folder = self.storage_dir / f"session_{session_id}"
        if not session_folder.exists():
            raise FileNotFoundError(f"No session folder found for {session_id}")
        
        if filename:
            file_path = session_folder / filename
        else:
            db_files = list(session_folder.glob("*.db"))
            if not db_files:
                raise FileNotFoundError(f"No databse files found in session {session_id}")
            file_path = db_files[0]
        if not file_path.exists():
            raise FileNotFoundError(f"Database file not found: {file_path}")
        
        stat = file_path.stat()

        return DatabaseFile(
            filename=filename,
            session_id=session_id,
            file_size = stat.st_size,
            upload_timestamp=datetime.fromtimestamp(stat.st_mtime),
            file_path=str(file_path)
        )
    
    def initialize_db(database_file: DatabaseFile):
        db = SQLDatabase.from_uri(f"sqlite:////{database_file.file_path}")
        return db
    
    def _is_valid_sqlite(self, file_path):
        """check if file is a valid SQLite database"""
        try:
            conn = sqlite3.connect(file_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
            return True
        except Exception:
            return False