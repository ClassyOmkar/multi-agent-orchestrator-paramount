import uuid
import asyncio
from typing import Dict, Optional
from app.models import TaskStatusResponse, AgentStatus
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.reviewer import ReviewerAgent
from openai import AsyncOpenAI

# Hardcoded Key as requested by User
HARDCODED_API_KEY = "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"

class Orchestrator:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.reviewer = ReviewerAgent()

    async def validate_key(self, api_key: str) -> bool:
        """
        Validates an API key by making a minimal call to the provider.
        """
        if not api_key: 
            return False
            
        base_url = "https://api.x.ai/v1"
        if api_key.startswith("gsk_"):
             base_url = "https://api.groq.com/openai/v1"
        
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        try:
            # Try listing models as a lightweight check
            await client.models.list()
            return True
        except:
            return False

    def create_task(self, query: str, api_key: Optional[str] = None) -> str:
        task_id = str(uuid.uuid4())
        
        # Use provided key or fallback to hardcoded
        final_api_key = api_key if api_key and api_key.strip() else HARDCODED_API_KEY
        
        self.tasks[task_id] = {
            "id": task_id,
            "query": query,
            "api_key": final_api_key,
            "status": "STARTING",
            "current_agent": None,
            "logs": [],
            "result": None,
            "updated_at": asyncio.get_event_loop().time()
        }
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)
    
    async def run_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return

        # Propagate API key to agents for this task execution
        api_key = task.get("api_key")
        self.planner.set_api_key(api_key)
        self.researcher.set_api_key(api_key)
        self.writer.set_api_key(api_key)
        self.reviewer.set_api_key(api_key)

        try:
            # 1. Planner
            task["status"] = "PLANNING"
            task["current_agent"] = "Planner"
            planner_output = await self.planner.process({"query": task["query"]})
            task["logs"].append({"agent": "Planner", "output": planner_output})
            
            # 2. Researcher
            task["status"] = "RESEARCHING"
            task["current_agent"] = "Researcher"
            # Pass original query + plan
            if isinstance(planner_output, dict):
                 planner_output["original_query"] = task["query"]
            
            researcher_output = await self.researcher.process(planner_output)
            task["logs"].append({"agent": "Researcher", "output": researcher_output})

            # 3. Writer
            task["status"] = "WRITING"
            task["current_agent"] = "Writer"
            writer_output = await self.writer.process(researcher_output)
            task["logs"].append({"agent": "Writer", "output": writer_output})

            # 4. Reviewer
            task["status"] = "REVIEWING"
            task["current_agent"] = "Reviewer"
            reviewer_output = await self.reviewer.process(writer_output)
            task["logs"].append({"agent": "Reviewer", "output": reviewer_output})
            
            # Finalize
            if reviewer_output.get("approved"):
                task["status"] = "COMPLETED"
                task["result"] = reviewer_output.get("final_report")
            else:
                task["status"] = "NEEDS_REVISION"
                # Loop back logic would go here
            
        except Exception as e:
            task["status"] = "FAILED"
            task["error"] = str(e)
            print(f"Task {task_id} failed: {e}")
        
        task["current_agent"] = None
