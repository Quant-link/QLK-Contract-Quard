"""
ContractQuard Backend API
FastAPI application for smart contract security analysis
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from contractquard.core.analyzer import ContractQuardAnalyzer
from contractquard.core.config import Config
from contractquard.core.findings import Severity

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="ContractQuard API",
    description="AI-augmented smart contract security analysis API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.contractquard.com"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000",
        "https://contractquard.com",
        "https://*.contractquard.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=get_remote_address(request),
        user_agent=request.headers.get("user-agent", "")
    )

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        client_ip=get_remote_address(request)
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global analyzer instance and start time
analyzer = ContractQuardAnalyzer()
start_time = time.time()

# Pydantic models
class AnalysisRequest(BaseModel):
    filename: str
    content: str
    config: Optional[dict] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    findings: list
    metadata: dict
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    uptime_seconds: Optional[float] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# API Routes
@app.get("/api/health", response_model=HealthResponse)
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint with system status"""
    try:
        # Check analyzer availability
        analyzer_status = "healthy" if analyzer else "unavailable"

        # System uptime (simplified)
        uptime = time.time() - start_time if 'start_time' in globals() else 0

        logger.info("Health check requested", client_ip=get_remote_address(request))

        return HealthResponse(
            status=analyzer_status,
            version="0.1.0",
            timestamp=datetime.now().isoformat(),
            uptime_seconds=uptime
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/analyze", response_model=AnalysisResponse)
@limiter.limit("10/minute")
async def analyze_contract(request: Request, file: UploadFile = File(...)):
    """Analyze uploaded smart contract file with comprehensive validation"""
    start_analysis_time = time.time()
    analysis_id = str(uuid.uuid4())

    try:
        # Comprehensive file validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        # File extension validation
        allowed_extensions = {'.sol', '.rs', '.go'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{file_ext}'. Only {', '.join(allowed_extensions)} files are supported."
            )

        # File size validation (10MB limit)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )

        # Content validation
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File must be valid UTF-8 encoded text"
            )

        # Basic content validation
        if len(content_str.strip()) == 0:
            raise HTTPException(status_code=400, detail="File cannot be empty")

        if len(content_str) > 1_000_000:  # 1MB text limit
            raise HTTPException(
                status_code=413,
                detail="File content too large. Maximum 1MB of text allowed"
            )

        logger.info(
            "Analysis started",
            analysis_id=analysis_id,
            filename=file.filename,
            file_size=len(content),
            client_ip=get_remote_address(request)
        )

        # Perform analysis
        config = Config()
        findings = analyzer.analyze_file(file.filename, content_str, config)
        
        # Convert findings to dict format with enhanced data
        findings_dict = []
        for finding in findings:
            findings_dict.append({
                "id": str(uuid.uuid4()),
                "detector": finding.detector,
                "severity": finding.severity.value,
                "title": finding.title,
                "description": finding.description,
                "line_number": finding.line_number,
                "column": finding.column,
                "code_snippet": finding.code_snippet,
                "recommendation": finding.recommendation,
                "confidence": getattr(finding, 'confidence', 'HIGH'),
                "impact": getattr(finding, 'impact', 'MEDIUM'),
                "cwe_id": getattr(finding, 'cwe_id', None),
                "references": getattr(finding, 'references', [])
            })

        # Calculate analysis duration
        analysis_duration = int((time.time() - start_analysis_time) * 1000)

        # Prepare enhanced metadata
        severity_counts = {
            "critical_count": len([f for f in findings_dict if f["severity"] == "CRITICAL"]),
            "high_count": len([f for f in findings_dict if f["severity"] == "HIGH"]),
            "medium_count": len([f for f in findings_dict if f["severity"] == "MEDIUM"]),
            "low_count": len([f for f in findings_dict if f["severity"] == "LOW"]),
            "info_count": len([f for f in findings_dict if f["severity"] == "INFO"])
        }

        # Prepare response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            findings=findings_dict,
            metadata={
                "filename": file.filename,
                "file_size": len(content),
                "total_findings": len(findings_dict),
                "analysis_duration_ms": analysis_duration,
                "language": file_ext[1:],  # Remove the dot
                "lines_of_code": len(content_str.splitlines()),
                **severity_counts
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Log successful analysis
        logger.info(
            "Analysis completed successfully",
            analysis_id=analysis_id,
            filename=file.filename,
            total_findings=len(findings_dict),
            duration_ms=analysis_duration,
            client_ip=get_remote_address(request)
        )

        # Broadcast analysis completion via WebSocket
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "analysis_id": analysis_id,
            "status": "completed",
            "findings_count": len(findings_dict),
            "duration_ms": analysis_duration,
            "timestamp": datetime.now().isoformat()
        }))

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except UnicodeDecodeError as e:
        logger.error(
            "File encoding error",
            analysis_id=analysis_id,
            filename=file.filename,
            error=str(e),
            client_ip=get_remote_address(request)
        )
        raise HTTPException(
            status_code=400,
            detail="File encoding error. Please ensure the file is valid UTF-8 text."
        )
    except Exception as e:
        logger.error(
            "Analysis failed with unexpected error",
            analysis_id=analysis_id,
            filename=file.filename,
            error=str(e),
            error_type=type(e).__name__,
            client_ip=get_remote_address(request)
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error during analysis. Please try again later."
        )

@app.get("/api/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID (placeholder for future database integration)"""
    # This would typically fetch from a database
    # For now, return a placeholder response
    return JSONResponse(
        status_code=404,
        content={"detail": "Analysis result not found. Results are currently not persisted."}
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
            else:
                # Echo message back
                await manager.send_personal_message(data, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
