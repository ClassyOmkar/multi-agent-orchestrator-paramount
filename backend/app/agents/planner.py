from typing import Dict, Any, List
from .base import Agent
from app.models import AgentStatus
import json

class PlannerAgent(Agent):
    def __init__(self):
        super().__init__(name="Planner")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = AgentStatus.RUNNING
        query = input_data.get("query", "")
        
        if self.client:
            # We strictly instruct JSON and provide a fallback structure
            system_prompt = (
                "You are an expert Planner Agent. Your goal is to break down a user's research request "
                "into 4-5 clear, distinct sub-tasks for a Researcher Agent. "
                "Output MUST be valid JSON. "
                "If the query is absolute nonsense (e.g. 'asdfghj'), return {\"error\": \"Invalid input\"}. "
                "Otherwise, return {\"plan\": [\"step 1\", \"step 2\"]}. "
                "Do not include markdown formatting like ```json."
            )
            response = await self._call_llm(system_prompt, query)
            try:
                # Basic cleanup in case LLM wraps code in markdown
                cleaned = response.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                
                # Check for error flag from LLM
                if "error" in data:
                    raise ValueError(f"Planner Validation Failed: {data['error']}")
                
                plan = data.get("plan", [])
                if not plan: # Fallback if plan is empty
                    plan = [f"Analyze {query}", f"Summarize findings for {query}"]
                    
            except ValueError as ve:
                raise ve 
            except Exception as e:
                # If JSON fail, fallback to single step instead of crashing
                plan = [f"Research task: {query}"]
        else:
            # Fallback mock check
            if len(query) < 4:
                 pass # Mock validation could go here

            plan = [
                f"Research background of {query}",
                f"Analyze key findings for {query}",
                f"Draft report on {query}",
                f"Review final document"
            ]
        
        self.status = AgentStatus.COMPLETED
        return {"plan": plan, "original_query": query}
