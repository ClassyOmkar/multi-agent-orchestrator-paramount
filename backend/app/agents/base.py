from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models import AgentStatus
import os
from openai import AsyncOpenAI

class Agent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus.IDLE
        self.client: Optional[AsyncOpenAI] = None
        self.model = "grok-2-latest"  # Default to Grok model

    def set_api_key(self, api_key: str):
        if api_key:
            if api_key.startswith("gsk_"):
                # Detect Groq Key
                self.client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                # Updated to latest supported model
                self.model = "llama-3.3-70b-versatile" 
            else:
                # Default to xAI/Grok
                self.client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1"
                )
                self.model = "grok-2-latest"

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            # Fallback for when no key is provided
            return "No API Key provided. Mocking response."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            # Return a structured error string we can parse on frontend if needed, 
            # but ideally we log it here.
            return f"LLM_ERROR: {str(e)}"

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return the result asynchronously.
        """
        pass

    def get_status(self) -> AgentStatus:
        return self.status
