"""
Data models untuk Autonomous Agent
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from enum import Enum

class TaskType(str, Enum):
    """Jenis task yang dapat dijalankan agent"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    READ_DOM = "read_dom"
    CUSTOM = "custom"

class AgentRequest(BaseModel):
    """Request model untuk agent task"""
    goal: str
    task_type: Optional[TaskType] = TaskType.CUSTOM
    parameters: Optional[Dict[str, Any]] = {}
    max_iterations: Optional[int] = 10
    timeout: Optional[int] = 300  # seconds

class ToolCall(BaseModel):
    """Model untuk tool call"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None

class AgentStep(BaseModel):
    """Model untuk satu langkah agent"""
    step_number: int
    planning: str
    tool_call: ToolCall
    observation: str
    success: bool

class AgentResponse(BaseModel):
    """Response model untuk agent task"""
    task_id: str
    goal: str
    status: str  # "running", "completed", "failed", "stopped"
    steps: List[AgentStep]
    final_result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class BrowserState(BaseModel):
    """Model untuk state browser"""
    current_url: Optional[str] = None
    page_title: Optional[str] = None
    dom_summary: Optional[str] = None
    screenshot_path: Optional[str] = None

