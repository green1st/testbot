"""
Autonomous Agent - Main Application
"""
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn

from agent.orchestrator import AgentOrchestrator
from agent.models import AgentRequest, AgentResponse

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Agent API",
    description="API untuk agent otomatis dengan kemampuan browser automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent orchestrator
orchestrator = AgentOrchestrator()

app.add_event_handler("startup", orchestrator.initialize)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Autonomous Agent API is running", "status": "healthy"}

@app.post("/agent/execute", response_model=AgentResponse)
async def execute_agent_task(request: AgentRequest):
    """Execute agent task"""
    try:
        result = await orchestrator.execute_task(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status")
async def get_agent_status():
    """Get current agent status"""
    return await orchestrator.get_status()

@app.post("/agent/stop")
async def stop_agent():
    """Stop current agent task"""
    return await orchestrator.stop_current_task()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

