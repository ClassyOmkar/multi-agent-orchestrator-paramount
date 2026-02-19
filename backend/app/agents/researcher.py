from typing import Dict, Any
from .base import Agent
from app.models import AgentStatus
import json
import os
from tavily import TavilyClient

class ResearcherAgent(Agent):
    def __init__(self):
        super().__init__(name="Researcher")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        # DEBUG PRINT
        print(f"DEBUG: ResearcherAgent Initialized. Tavily Key Present? {bool(self.tavily_key)}")
        if self.tavily_key:
             print(f"DEBUG: Key starts with {self.tavily_key[:4]}...")
        
        self.tavily_client = TavilyClient(api_key=self.tavily_key) if self.tavily_key else None

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = AgentStatus.RUNNING
        query = input_data.get("original_query", "")
        plan = input_data.get("plan", [])
        
        if not query and plan:
            query = " ".join(plan[:2])

        print(f"DEBUG: Researcher processing query: '{query}'")

        search_context = ""
        sources = []

        if self.tavily_client and query:
            try:
                print("DEBUG: Attempting Tavily Search...")
                response = self.tavily_client.search(query, search_depth="basic", max_results=3)
                results = response.get("results", [])
                print(f"DEBUG: Tavily returned {len(results)} results.")
                
                for i, res in enumerate(results):
                    content = res.get("content", "")
                    url = res.get("url", "")
                    title = res.get("title", "Source")
                    search_context += f"\nSource {i+1} ({title}): {content}\nURL: {url}\n"
                    sources.append(title)
            except Exception as e:
                print(f"DEBUG: Tavily Search Failed: {e}")
                search_context = f"Search failed: {e}. Relying on internal knowledge."
        else:
            print("DEBUG: No Tavily Client or Query. Skipping search.")
            search_context = "No search tool available. Relying on internal knowledge."

        if self.client:
            system_prompt = (
                "You are an expert Researcher Agent. "
                "You have been provided with real-time search results (Context) for a user query. "
                "Synthesize this information into a detailed summary. "
                "If the context is empty or irrelevant, rely on your internal knowledge but mention that this is general knowledge. "
                "Return valid JSON output only in form: "
                "{\"summary\": \"detailed summary...\", \"sources\": [\"list of source titles or URLs used\"]}"
            )
            
            user_prompt = f"User Query: {query}\n\nSearch Context from Tavily:\n{search_context}"
            
            response = await self._call_llm(system_prompt, user_prompt)
            
            try:
                cleaned = response.replace("```json", "").replace("```", "").strip()
                research_data = json.loads(cleaned)
                if not research_data.get("sources") and sources:
                    research_data["sources"] = sources
            except:
                research_data = {"summary": response, "sources": sources}
        else:
            research_data = {
                "summary": "LLM Client unavailable. Raw Search results: " + search_context[:200],
                "sources": sources
            }
        
        self.status = AgentStatus.COMPLETED
        return {"research_data": research_data, "plan": plan}
