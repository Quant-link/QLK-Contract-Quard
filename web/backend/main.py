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
# import structlog

# Simple logging
import logging
logger = logging.getLogger(__name__)

# Mock analyzer for demo
class MockAnalyzer:
    def analyze_file(self, filename, content, config=None):
        # Mock analysis results
        return [
            type('Finding', (), {
                'detector': 'reentrancy',
                'severity': type('Severity', (), {'value': 'HIGH'})(),
                'title': 'Potential Reentrancy Vulnerability',
                'description': 'This function may be vulnerable to reentrancy attacks',
                'line_number': 42,
                'column': 10,
                'code_snippet': 'function withdraw() public {',
                'recommendation': 'Use the checks-effects-interactions pattern'
            })()
        ]

# Initialize FastAPI app
app = FastAPI(
    title="ContractQuard API",
    description="AI-augmented smart contract security analysis API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

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

# Simple request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response

# Global analyzer instance and start time
analyzer = MockAnalyzer()
start_time = time.time()

# In-memory storage for analysis results (production'da database kullanılır)
analysis_results = {}

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
async def health_check():
    """Health check endpoint with system status"""
    try:
        # Check analyzer availability
        analyzer_status = "healthy" if analyzer else "unavailable"

        # System uptime (simplified)
        uptime = time.time() - start_time if 'start_time' in globals() else 0

        print("Health check requested")

        return HealthResponse(
            status=analyzer_status,
            version="0.1.0",
            timestamp=datetime.now().isoformat(),
            uptime_seconds=uptime
        )
    except Exception as e:
        print(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_contract(file: UploadFile = File(...)):
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

        print(f"Analysis started: {analysis_id} - {file.filename} ({len(content)} bytes)")

        # Perform analysis
        findings = analyzer.analyze_file(file.filename, content_str)
        
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
        
        # Store analysis result for later retrieval
        analysis_results[analysis_id] = response

        # Log successful analysis
        print(f"Analysis completed: {analysis_id} - {len(findings_dict)} findings in {analysis_duration}ms")

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
        print(f"File encoding error: {e}")
        raise HTTPException(
            status_code=400,
            detail="File encoding error. Please ensure the file is valid UTF-8 text."
        )
    except Exception as e:
        print(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during analysis. Please try again later."
        )

@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID"""
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis with ID {analysis_id} not found"
            )

        result = analysis_results[analysis_id]
        print(f"Retrieved analysis result: {analysis_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving analysis result: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving analysis result"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            try:
                # Wait for messages with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                        websocket
                    )
                else:
                    # Echo message back
                    await manager.send_personal_message(data, websocket)

            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await manager.send_personal_message(
                    json.dumps({"type": "ping", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
            except Exception as e:
                print(f"WebSocket error: {e}")
                break

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
