from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

from api.endpoints import upload, query

from services.file_service import FileService
from services.query_service import QueryService
from services.session_service import SessionService

app = FastAPI(
    title="Natural Language Control over SQLite Database",
    description="API that converts natural language questions into sql queries and executes them",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_file_service() -> FileService:
    """Provides FileService instance"""
    return FileService()

def get_query_service() -> QueryService:
    """Provides QueryService instance"""
    return QueryService

def get_session_service() -> SessionService:
    """Provides SessionService instance"""
    return SessionService

app.dependency_overrides[FileService] = get_file_service
app.dependency_overrides[QueryService] = get_query_service
app.dependency_overrides[SessionService] = get_session_service

app.include_router(
    upload.router,
    prefix="api/v1/upload",
    tags=["File Uploaded"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    query.router,
    prefix="/api/v1/query",
    tags=["Query Processing"],
    responses={404: {"description": "Not found"}},
)

@app.get("/")
async def root():
    