from typing import Dict, Any
from .base import Agent
from app.models import AgentStatus

class WriterAgent(Agent):
    def __init__(self):
        super().__init__(name="Writer")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = AgentStatus.RUNNING
        research_data = input_data.get("research_data", {})
        
        if self.client:
            system_prompt = (
                "You are an expert Writer Agent. Write a professional, well-structured Markdown report "
                "based on the provided research summary and sources. "
                "Do not output JSON. Output the Markdown report directly."
            )
            user_prompt = f"Research Data: {research_data}"
            draft = await self._call_llm(system_prompt, user_prompt)
        else:
            draft = (
                "# Executive Summary\n\n"
                f"Based on the research: {research_data.get('summary', 'No summary')}\n\n"
                "## Key Points\n"
                "- Point 1: Significant impact observed.\n"
                "- Point 2: Data trends are positive.\n\n"
                "## Conclusion\n"
                "Further study is recommended."
            )
        
        self.status = AgentStatus.COMPLETED
        return {"draft": draft, "research_data": research_data}
