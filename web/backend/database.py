"""
Database models and configuration for ContractQuard
"""

import os
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey, DECIMAL, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import uuid

# Database configuration - Use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contractquard.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class Analysis(Base):
    """Analysis record in database"""
    __tablename__ = "analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_content = Column(Text, nullable=True)  # Store original file content
    language = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    risk_score = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    analysis_duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    metrics = relationship("CodeMetrics", back_populates="analysis", uselist=False, cascade="all, delete-orphan")

class Finding(Base):
    """Security finding record"""
    __tablename__ = "findings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey('analyses.id'), nullable=False)
    detector_name = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    line_number = Column(Integer, nullable=False)
    column_number = Column(Integer, default=0)
    code_snippet = Column(Text)
    recommendation = Column(Text)
    confidence = Column(String(20), default="HIGH")
    impact = Column(String(20), default="MEDIUM")
    cwe_id = Column(Integer)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="findings")

class CodeMetrics(Base):
    """Code quality metrics"""
    __tablename__ = "code_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey('analyses.id'), nullable=False)
    lines_of_code = Column(Integer, default=0)
    cyclomatic_complexity = Column(Integer, default=0)
    function_count = Column(Integer, default=0)
    contract_count = Column(Integer, default=0)
    dependency_count = Column(Integer, default=0)
    test_coverage = Column(DECIMAL(5,2), default=0.0)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="metrics")

# Database dependency
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    """Create all database tables"""
    # Drop and recreate to ensure schema is up to date
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

# Initialize database
def init_db():
    """Initialize database with tables"""
    create_tables()
