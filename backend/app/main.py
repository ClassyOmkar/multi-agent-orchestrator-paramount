import os
from dotenv import load_dotenv

# Load env vars BEFORE importing other modules
# Try loading from .env in backend root
load_dotenv() 

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import TaskInput, TaskStatusResponse, ValidateKeyInput
from app.orchestrator import Orchestrator

app = FastAPI(title="Multi-Agent Orchestrator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

@app.post("/tasks", response_model=TaskStatusResponse)
async def create_task(task_input: TaskInput, background_tasks: BackgroundTasks):
    task_id = orchestrator.create_task(task_input.query, task_input.api_key)
    background_tasks.add_task(orchestrator.run_task, task_id)
    return TaskStatusResponse(
        task_id=task_id,
        status="STARTING",
        logs=[]
    )

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    status = orchestrator.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=status["id"],
        status=status["status"],
        logs=status.get("logs", []),
        result=status.get("result")
    )

@app.post("/validate-key")
async def validate_key_endpoint(input_data: ValidateKeyInput):
    is_valid = await orchestrator.validate_key(input_data.api_key)
    return {"valid": is_valid}
