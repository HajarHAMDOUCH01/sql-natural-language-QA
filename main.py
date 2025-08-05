from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
from pathlib import Path

# ✅ Configuration du logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from api.endpoints import upload, query
from services.file_service import FileService
from services.query_service import QueryService
from services.session_service import SessionService

app = FastAPI(
    title="Natural Language Control over SQLite Database",
    description="API that converts natural language questions into sql queries and executes them",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_file_service() -> FileService:
    return FileService()

def get_query_service() -> QueryService:
    return QueryService()

def get_session_service() -> SessionService:
    return SessionService()

app.dependency_overrides[FileService] = get_file_service
app.dependency_overrides[QueryService] = get_query_service
app.dependency_overrides[SessionService] = get_session_service

app.include_router(
    upload.router,
    prefix="/api/v1/upload",
    tags=["File Upload"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    query.router,
    prefix="/api/v1/query",
    tags=["Query Processing"],
    responses={404: {"description": "Not found"}},
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Natural Language to SQL API is running",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message" : "Welcome to Natural Language to Database Management API",
        "version" : "1.0.0",
        "docs" : "/docs",
        "redoc" : "/redoc",
        "health" : "/health",
        "endpoints" : {
            "upload" : "/api/v1/upload/",
            "query" : "/api/v1/query/"
        }
    }

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    print(f"Starting Natural Language to Database Management API ...")
    print(f"Server will run on: http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Debug mode: {debug}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )