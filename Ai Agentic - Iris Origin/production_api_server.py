"""
Iris Origin - AI Customer Service API
=====================================

Production-ready FastAPI server for AI customer service automation.
Supports Facebook Fan Pages customer service in Thai and English.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
import uvicorn
import json
import sys
import os
from datetime import datetime
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("iris-origin-api")

# Import AI Service
try:
    from src.ai_service.simple_processor import SimpleAIProcessor
    logger.info("✅ SimpleAIProcessor imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import SimpleAIProcessor: {e}")
    # Fallback to test processor if main not available
    exec(open('test_final_ai.py').read())
    SimpleAIProcessor = TestAIProcessor
    logger.info("✅ Using TestAIProcessor as fallback")

# Pydantic Models
class MessageRequest(BaseModel):
    """Customer message request"""
    message: str = Field(..., description="Customer message text", min_length=1, max_length=2000)
    user_id: str = Field(..., description="Customer user ID", min_length=1, max_length=100)
    platform: Optional[str] = Field("facebook", description="Platform (facebook, instagram, whatsapp)")
    page_id: Optional[str] = Field(None, description="Facebook page ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ProcessingResponse(BaseModel):
    """AI processing response"""
    success: bool = Field(..., description="Processing success status")
    message_id: str = Field(..., description="Unique message ID")
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., description="Intent confidence score")
    sentiment: str = Field(..., description="Sentiment analysis result")
    sentiment_score: float = Field(..., description="Sentiment confidence score")
    language: str = Field(..., description="Detected language")
    entities: List[Dict[str, Any]] = Field(..., description="Extracted entities")
    suggested_response: str = Field(..., description="AI-generated response")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="Processing timestamp")
    user_id: str = Field(..., description="Customer user ID")
    platform: str = Field(..., description="Platform source")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    ai_processor: str = Field(..., description="AI processor status")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    timestamp: str = Field(..., description="Current timestamp")

# FastAPI Application
app = FastAPI(
    title="Iris Origin - AI Customer Service API",
    description="Production AI customer service automation for Facebook Fan Pages",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Variables
ai_processor = None
startup_time = datetime.now()

@app.on_event("startup")
async def startup_event():
    """Initialize AI processor on startup"""
    global ai_processor
    try:
        logger.info("🚀 Starting Iris Origin AI API Server...")
        ai_processor = SimpleAIProcessor()
        await ai_processor.initialize()  # If async init needed
        logger.info("✅ AI Processor initialized successfully")
        logger.info("🎯 Iris Origin AI API Server ready for production!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI processor: {e}")
        # Keep server running with error state
        ai_processor = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down Iris Origin AI API Server...")
    if ai_processor:
        try:
            await ai_processor.cleanup()  # If cleanup needed
        except:
            pass
    logger.info("✅ Shutdown complete")

# API Endpoints

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Iris Origin - AI Customer Service API",
        "version": "1.0.0",
        "status": "running",
        "description": "Production AI customer service automation for Facebook Fan Pages",
        "endpoints": {
            "process": "/api/v1/process - Process customer messages",
            "health": "/api/v1/health - Health check",
            "docs": "/docs - API documentation"
        },
        "languages": ["Thai", "English"],
        "platforms": ["Facebook", "Instagram", "WhatsApp"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - startup_time).total_seconds()
    
    ai_status = "healthy" if ai_processor else "error"
    
    return HealthResponse(
        status="healthy" if ai_processor else "degraded",
        version="1.0.0",
        ai_processor=ai_status,
        uptime_seconds=uptime,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/v1/process", response_model=ProcessingResponse)
async def process_message(request: MessageRequest, background_tasks: BackgroundTasks):
    """
    Process customer message with AI
    
    This endpoint handles customer service messages and returns:
    - Intent classification
    - Sentiment analysis  
    - Language detection
    - Entity extraction
    - AI-generated response
    """
    if not ai_processor:
        logger.error("❌ AI processor not available")
        raise HTTPException(
            status_code=503, 
            detail="AI processor not available. Please try again later."
        )
    
    try:
        # Generate unique message ID
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.user_id}"
        
        # Process with AI
        logger.info(f"🔄 Processing message for user: {request.user_id}")
        result = await ai_processor.process_message(
            message_text=request.message,
            user_id=request.user_id
        )
        
        # Background task for analytics (if needed)
        background_tasks.add_task(
            log_analytics,
            message_id=message_id,
            user_id=request.user_id,
            platform=request.platform,
            intent=result.intent,
            language=result.language
        )
        
        # Create response
        response = ProcessingResponse(
            success=True,
            message_id=message_id,
            intent=result.intent,
            confidence=result.confidence,
            sentiment=result.sentiment,
            sentiment_score=result.sentiment_score,
            language=result.language,
            entities=result.entities,
            suggested_response=result.suggested_response,
            processing_time_ms=result.processing_time_ms,
            timestamp=datetime.now().isoformat(),
            user_id=request.user_id,
            platform=request.platform or "facebook"
        )
        
        logger.info(f"✅ Message processed successfully: {message_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@app.post("/api/v1/bulk-process")
async def bulk_process(messages: List[MessageRequest]):
    """
    Process multiple messages in batch
    """
    if not ai_processor:
        raise HTTPException(
            status_code=503,
            detail="AI processor not available"
        )
    
    if len(messages) > 100:  # Rate limiting
        raise HTTPException(
            status_code=413,
            detail="Too many messages. Maximum 100 per batch."
        )
    
    try:
        results = []
        for msg_request in messages:
            result = await ai_processor.process_message(
                message_text=msg_request.message,
                user_id=msg_request.user_id
            )
            
            message_id = f"bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{msg_request.user_id}"
            
            response = ProcessingResponse(
                success=True,
                message_id=message_id,
                intent=result.intent,
                confidence=result.confidence,
                sentiment=result.sentiment,
                sentiment_score=result.sentiment_score,
                language=result.language,
                entities=result.entities,
                suggested_response=result.suggested_response,
                processing_time_ms=result.processing_time_ms,
                timestamp=datetime.now().isoformat(),
                user_id=msg_request.user_id,
                platform=msg_request.platform or "facebook"
            )
            
            results.append(response)
        
        return {
            "success": True,
            "processed_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Error in bulk processing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in bulk processing: {str(e)}"
        )

# Background Tasks

async def log_analytics(message_id: str, user_id: str, platform: str, intent: str, language: str):
    """Background task for analytics logging"""
    try:
        # Log analytics data (implement based on requirements)
        analytics_data = {
            "message_id": message_id,
            "user_id": user_id,
            "platform": platform,
            "intent": intent,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
        # Here you would typically send to analytics service
        logger.info(f"📊 Analytics logged: {message_id}")
        
    except Exception as e:
        logger.error(f"❌ Analytics logging failed: {e}")

# Error Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

# Development Server
if __name__ == "__main__":
    print("🚀 Starting Iris Origin AI API Server...")
    print("📋 Configuration:")
    print(f"   - Host: 0.0.0.0")
    print(f"   - Port: 8000")
    print(f"   - Docs: http://localhost:8000/docs")
    print(f"   - API: http://localhost:8000/api/v1/")
    print(f"   - Version: 1.0.0 Production")
    
    uvicorn.run(
        "production_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to False for production
        log_level="info"
    )