from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from typing_extensions import Annotated, TypedDict

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class APIKeys(BaseModel):
    """User's API keys"""
    gemini_api_key: str
    langchain_api_key: str

class DatabaseFile(BaseModel):
    """Model representing an uploaded database file"""
    file_name: str
    session_id: str
    file_size: int
    upload_timestamp: datetime
    file_path: str

    class Config:
        from_attributes = True

class UploadRequest(BaseModel):
    """Request model for file upload"""
    api_keys: APIKeys

class UploadResponse(BaseModel):
    """Response model for successful upload"""
    session_id: str
    filename: str
    message: str
    file_info: DatabaseFile


class QueryRequest(BaseModel):
    """Natural language query request"""
    question: str
    api_keys: APIKeys

class QueryOutput(TypedDict):
    """Generated SQL query output"""
    query: Annotated[str, ..., "Syntactically valid SQL query"]

class SQLQuery(BaseModel):
    """SQL query model"""
    query: QueryOutput
    session_id: str

class QueryResult(BaseModel):
    """Query execution result"""
    data: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float

class GeneratedAnswer(BaseModel):
    """Final answer to user's question"""
    answer: str
    sql_query: str
    row_count: int