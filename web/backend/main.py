"""
ContractQuard Backend API
FastAPI application for smart contract security analysis
"""

import os
import sys
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime
import uuid

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from contractquard.core.analyzer import ContractQuardAnalyzer
from contractquard.core.config import Config
from contractquard.core.findings import Severity

# Initialize FastAPI app
app = FastAPI(
    title="ContractQuard API",
    description="AI-augmented smart contract security analysis API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analyzer instance
analyzer = ContractQuardAnalyzer()

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
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_contract(file: UploadFile = File(...)):
    """Analyze uploaded smart contract file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.sol', '.rs', '.go')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only .sol, .rs, and .go files are supported."
            )
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Perform analysis
        config = Config()
        findings = analyzer.analyze_file(file.filename, content_str, config)
        
        # Convert findings to dict format
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
                "recommendation": finding.recommendation
            })
        
        # Prepare response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            findings=findings_dict,
            metadata={
                "filename": file.filename,
                "file_size": len(content),
                "total_findings": len(findings_dict),
                "critical_count": len([f for f in findings_dict if f["severity"] == "CRITICAL"]),
                "high_count": len([f for f in findings_dict if f["severity"] == "HIGH"]),
                "medium_count": len([f for f in findings_dict if f["severity"] == "MEDIUM"]),
                "low_count": len([f for f in findings_dict if f["severity"] == "LOW"]),
                "info_count": len([f for f in findings_dict if f["severity"] == "INFO"])
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Broadcast analysis completion via WebSocket
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "analysis_id": analysis_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
