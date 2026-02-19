import pytest
import asyncio
from app.orchestrator import Orchestrator
from app.models import AgentStatus

@pytest.mark.asyncio
async def test_create_task():
    orchestrator = Orchestrator()
    task_id = orchestrator.create_task("Test Query")
    
    assert task_id is not None
    task = orchestrator.get_task_status(task_id)
    assert task["query"] == "Test Query"
    assert task["status"] == "STARTING"

@pytest.mark.asyncio
async def test_run_task_flow():
    orchestrator = Orchestrator()
    task_id = orchestrator.create_task("Test Query")
    
    # Run the task (Mock agents have sleep, so this will take ~6s)
    await orchestrator.run_task(task_id)
    
    task = orchestrator.get_task_status(task_id)
    assert task["status"] == "COMPLETED"
    assert len(task["logs"]) == 4 # Planner, Researcher, Writer, Reviewer
    assert task["result"] is not None
    assert "Test Query" in task["logs"][0]["output"]["original_query"]
