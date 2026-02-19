from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"

class TaskInput(BaseModel):
    query: str
    api_key: Optional[str] = None

class ValidateKeyInput(BaseModel):
    api_key: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    current_agent: Optional[str] = None
    result: Optional[str] = None
    logs: List[Dict[str, Any]] = [] # Restored missing logs field
