"""
ContractQuard Backend API
FastAPI application for smart contract security analysis
"""

import os
import sys
import time
import logging
import hashlib
import re
from pathlib import Path
from typing import Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

# Import our models and analyzers
from models import AnalysisResponse, HealthResponse, SeverityLevel
from database import get_db, init_db, Analysis, Finding, CodeMetrics
from analyzers.analyzer_factory import analyzer_factory

# Simple logging
import logging
logger = logging.getLogger(__name__)

# Initialize database
init_db()

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

# Global start time
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
        # Check analyzer factory availability
        supported_languages = analyzer_factory.get_supported_extensions()
        analyzer_status = "healthy" if supported_languages else "unavailable"

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

@app.get("/api/ai-status")
async def ai_status():
    """Get AI integration status and capabilities"""
    try:
        from analyzers.ai_analyzer import AIIntegrationStatus
        from analyzers.huggingface_analyzer import HuggingFaceStatus

        # Get both OpenAI and Hugging Face status
        openai_status = AIIntegrationStatus.get_status()
        hf_status = HuggingFaceStatus.get_status()

        # Combine status information
        combined_status = {
            "ai_providers": {
                "openai": openai_status,
                "huggingface": hf_status
            },
            "active_models": [],
            "total_capabilities": []
        }

        # Add active models
        if openai_status.get("openai_available"):
            combined_status["active_models"].extend(openai_status.get("supported_models", []))

        if hf_status.get("huggingface_available"):
            combined_status["active_models"].extend(hf_status.get("available_models", []))

        # Combine capabilities
        combined_status["total_capabilities"].extend(openai_status.get("capabilities", []))
        combined_status["total_capabilities"].extend(hf_status.get("capabilities", []))

        return combined_status

    except Exception as e:
        return {
            "error": str(e),
            "ai_providers": {
                "openai": {"available": False},
                "huggingface": {"available": False}
            },
            "active_models": [],
            "total_capabilities": []
        }

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

        # Get appropriate analyzer for file type
        language = file_ext[1:]  # Remove the dot
        analyzer = analyzer_factory.get_analyzer(language)

        if not analyzer:
            raise HTTPException(
                status_code=400,
                detail=f"No analyzer available for {language} files"
            )

        # Calculate file hash for caching
        file_hash = hashlib.sha256(content).hexdigest()

        # Broadcast analysis start via WebSocket
        await manager.broadcast(json.dumps({
            "type": "analysis_started",
            "analysis_id": analysis_id,
            "filename": file.filename,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }))

        # Perform real analysis
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

        # Calculate risk score
        risk_score = analyzer.calculate_risk_score(findings)

        # Store in database (with fallback to in-memory)
        try:
            db = next(get_db())

            # Create analysis record
            db_analysis = Analysis(
                id=analysis_id,
                filename=file.filename,
                file_hash=file_hash,
                file_content=content_str,  # Store original content
                language=language,
                file_size=len(content),
                status="COMPLETED",
                risk_score=risk_score,
                total_findings=len(findings_dict),
                analysis_duration_ms=analysis_duration,
                **severity_counts
            )
            db.add(db_analysis)

            # Create finding records
            for finding_dict in findings_dict:
                db_finding = Finding(
                    analysis_id=analysis_id,
                    detector_name=finding_dict["detector"],
                    severity=finding_dict["severity"],
                    category=getattr(findings[findings_dict.index(finding_dict)], 'category', 'Security'),
                    title=finding_dict["title"],
                    description=finding_dict["description"],
                    line_number=finding_dict["line_number"],
                    column_number=finding_dict["column"],
                    code_snippet=finding_dict["code_snippet"],
                    recommendation=finding_dict["recommendation"],
                    confidence=finding_dict["confidence"],
                    impact=finding_dict["impact"],
                    cwe_id=finding_dict["cwe_id"],
                    references=finding_dict["references"]
                )
                db.add(db_finding)

            # Create code metrics
            db_metrics = CodeMetrics(
                analysis_id=analysis_id,
                lines_of_code=len(content_str.splitlines()),
                function_count=len(re.findall(r'function\s+\w+', content_str, re.IGNORECASE)),
                contract_count=len(re.findall(r'contract\s+\w+', content_str, re.IGNORECASE))
            )
            db.add(db_metrics)

            db.commit()
            print(f"Analysis saved to database: {analysis_id}")

        except Exception as e:
            print(f"Database save failed, using in-memory storage: {e}")

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
                "language": language,
                "lines_of_code": len(content_str.splitlines()),
                "risk_score": risk_score,
                **severity_counts
            },
            timestamp=datetime.now().isoformat()
        )

        # Store analysis result for later retrieval (fallback)
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
async def get_analysis_result(analysis_id: str, db: Session = Depends(get_db)):
    """Get analysis result by ID"""
    try:
        # Try database first
        db_analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

        if db_analysis:
            # Get findings from database
            db_findings = db.query(Finding).filter(Finding.analysis_id == analysis_id).all()

            findings_dict = []
            for finding in db_findings:
                findings_dict.append({
                    "id": str(finding.id),
                    "detector": finding.detector_name,
                    "severity": finding.severity,
                    "title": finding.title,
                    "description": finding.description,
                    "line_number": finding.line_number,
                    "column": finding.column_number,
                    "code_snippet": finding.code_snippet,
                    "recommendation": finding.recommendation,
                    "confidence": finding.confidence,
                    "impact": finding.impact,
                    "cwe_id": finding.cwe_id,
                    "references": finding.references or []
                })

            # Prepare response from database
            response = AnalysisResponse(
                analysis_id=str(db_analysis.id),
                status="completed",
                findings=findings_dict,
                metadata={
                    "filename": db_analysis.filename,
                    "file_size": db_analysis.file_size,
                    "total_findings": db_analysis.total_findings,
                    "analysis_duration_ms": db_analysis.analysis_duration_ms,
                    "language": db_analysis.language,
                    "risk_score": db_analysis.risk_score,
                    "critical_count": db_analysis.critical_count,
                    "high_count": db_analysis.high_count,
                    "medium_count": db_analysis.medium_count,
                    "low_count": db_analysis.low_count,
                    "info_count": db_analysis.info_count
                },
                timestamp=db_analysis.created_at.isoformat()
            )

            print(f"Retrieved analysis result from database: {analysis_id}")
            return response

        # Fallback to in-memory storage
        if analysis_id in analysis_results:
            result = analysis_results[analysis_id]
            print(f"Retrieved analysis result from memory: {analysis_id}")
            return result

        # Not found anywhere
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {analysis_id} not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving analysis result: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving analysis result"
        )

@app.get("/api/analyses")
async def get_analysis_history(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Get analysis history with pagination"""
    try:
        analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()

        history = []
        for analysis in analyses:
            history.append({
                "analysis_id": str(analysis.id),
                "filename": analysis.filename,
                "language": analysis.language,
                "status": analysis.status,
                "risk_score": analysis.risk_score,
                "total_findings": analysis.total_findings,
                "critical_count": analysis.critical_count,
                "high_count": analysis.high_count,
                "medium_count": analysis.medium_count,
                "low_count": analysis.low_count,
                "info_count": analysis.info_count,
                "analysis_duration_ms": analysis.analysis_duration_ms,
                "created_at": analysis.created_at.isoformat()
            })

        return {"analyses": history, "total": len(history)}

    except Exception as e:
        print(f"Error retrieving analysis history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis history")

@app.get("/api/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get analysis statistics"""
    try:
        total_analyses = db.query(Analysis).count()

        # Get severity distribution
        critical_count = db.query(Analysis).filter(Analysis.critical_count > 0).count()
        high_count = db.query(Analysis).filter(Analysis.high_count > 0).count()
        medium_count = db.query(Analysis).filter(Analysis.medium_count > 0).count()

        # Get language distribution
        from sqlalchemy import func
        language_stats = db.query(Analysis.language, func.count(Analysis.id)).group_by(Analysis.language).all()

        return {
            "total_analyses": total_analyses,
            "severity_distribution": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count
            },
            "language_distribution": {lang: count for lang, count in language_stats},
            "supported_languages": analyzer_factory.get_supported_extensions()
        }

    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

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

@app.get("/api/analysis/{analysis_id}/code")
async def get_analysis_code(analysis_id: str, db: Session = Depends(get_db)):
    """Get original code content for analysis"""
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Return the actual stored file content
        content = analysis.file_content if analysis.file_content else ""

        return {
            "analysis_id": analysis_id,
            "filename": analysis.filename,
            "language": analysis.language,
            "content": content
        }
    except Exception as e:
        print(f"Error getting analysis code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
