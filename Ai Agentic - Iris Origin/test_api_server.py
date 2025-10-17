"""
Test AI API Server
=================

Simple API server to test AI processing integration.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.ai_service.simple_processor import SimpleAIProcessor

# Initialize FastAPI
app = FastAPI(
    title="Iris Origin AI API",
    description="AI Processing API for customer service automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize AI processor
try:
    ai_processor = SimpleAIProcessor()
    print("✅ AI Processor initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize AI Processor: {e}")
    ai_processor = None

# Request/Response models
class MessageRequest(BaseModel):
    message: str
    user_id: str = "test_user"

class ProcessingResponse(BaseModel):
    success: bool
    intent: str
    confidence: float
    sentiment: str
    sentiment_score: float
    language: str
    entities: list
    suggested_response: str
    processing_time_ms: float

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Iris Origin AI API",
        "status": "running",
        "version": "1.0.0",
        "ai_processor": "available" if ai_processor else "unavailable"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-17T17:42:00",
        "ai_processor": "ready" if ai_processor else "error"
    }

@app.post("/api/process", response_model=ProcessingResponse)
async def process_message(request: MessageRequest):
    """Process message with AI engine"""
    
    if not ai_processor:
        raise HTTPException(status_code=503, detail="AI Processor not available")
    
    try:
        print(f"Processing message: {request.message[:50]}...")
        
        # Process with AI
        result = await ai_processor.process_message(
            message_text=request.message,
            user_id=request.user_id
        )
        
        # Return structured response
        response = ProcessingResponse(
            success=True,
            intent=result.intent,
            confidence=result.confidence,
            sentiment=result.sentiment,
            sentiment_score=result.sentiment_score,
            language=result.language,
            entities=result.entities,
            suggested_response=result.suggested_response,
            processing_time_ms=result.processing_time_ms
        )
        
        print(f"✅ Processed: {result.intent} ({result.language})")
        return response
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Iris Origin AI API Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")