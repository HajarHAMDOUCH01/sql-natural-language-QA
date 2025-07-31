from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class APIKeys(BaseModel):
    """User's API keys"""
    gemini_api_key: str
    langchain_api_key: str

class DatabaseFile(BaseModel):
    """Model representing an uploaded database file"""
    filename: str
    session_id: str
    file_size: int
    upload_timestamp: datetime
    file_path: str

    class Config:
        from_attributes = True

class UploadRequest(BaseModel):
    """Request model for succeful upload"""
    # session_id: Optional[str] = None
    api_keys: APIKeys

class UploadResponse(BaseModel):
    """Response model for succesful upload"""
    session_id: str
    filename: str
    message: str
    file_info: DatabaseFile

class QueryRequest(BaseModel):
    """the query the user sends in natural language"""
    question: str
    api_keys: APIKeys

