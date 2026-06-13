from __future__ import annotations

import logging
from typing import Any
from backend.core.config import settings

logger = logging.getLogger(__name__)


class FoundryAgentClient:
    """
    Client for calling saved Microsoft Azure AI Foundry Agents.
    Uses the official azure-ai-projects SDK if available.
    """

    def __init__(
        self,
        project_endpoint: str | None = None,
        agent_name: str | None = None,
        agent_version: str | None = None,
        api_key: str | None = None,
    ) -> None:
        # Default to configured settings if not provided
        self.project_endpoint = project_endpoint or settings.FOUNDRY_PROJECT_ENDPOINT
        self.agent_name = agent_name or settings.FOUNDRY_AGENT_NAME
        self.agent_version = agent_version or settings.FOUNDRY_AGENT_VERSION
        self.api_key = api_key or settings.FOUNDRY_API_KEY

    @property
    def enabled(self) -> bool:
        return bool(self.project_endpoint and self.agent_name)

    async def call_agent(self, prompt: str) -> str:
        """
        Backward-compatible wrapper to call the agent.
        """
        res = await self.chat_completion_raw("", prompt)
        if res["ok"]:
            return res["content"]
        else:
            raise RuntimeError(res.get("detail", "Foundry Agent call failed"))

    async def chat_completion_raw(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """
        Calls the saved Foundry Agent and returns the normalized result.
        Uses DefaultAzureCredential if api_key is not configured, or if SDK is present.
        """
        if not self.enabled:
            return {
                "ok": False,
                "provider": "MicrosoftFoundryAgent",
                "agent_name": self.agent_name or "FailureLens1",
                "agent_version": self.agent_version or "1",
                "content": "",
                "detail": "Foundry Agent configuration is missing (project_endpoint or agent_name)"
            }

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
            from azure.core.credentials import AzureKeyCredential
        except ImportError as exc:
            logger.warning("azure-ai-projects or azure-identity SDK is not installed. SDK auth not configured.")
            return {
                "ok": False,
                "provider": "MicrosoftFoundryAgent",
                "agent_name": self.agent_name,
                "agent_version": self.agent_version,
                "content": "",
                "detail": f"SDK auth is not configured: {exc}"
            }

        try:
            if self.api_key:
                credential = AzureKeyCredential(self.api_key)
            else:
                credential = DefaultAzureCredential()

            # Initialize Azure AI Project client using connection string
            project_client = AIProjectClient.from_connection_string(
                connection_string=self.project_endpoint,
                credential=credential
            )
            
            # Retrieve agent and thread
            agent = project_client.agents.get_agent(self.agent_name)
            thread = project_client.agents.create_thread()
            
            combined_prompt = f"System Instruction: {system_prompt}\n\nUser Message: {user_prompt}" if system_prompt else user_prompt
            
            project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=combined_prompt
            )
            
            run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
            
            # Poll for completion
            import asyncio
            while run.status in ["queued", "in_progress"]:
                await asyncio.sleep(0.5)
                run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
                
            if run.status != "completed":
                return {
                    "ok": False,
                    "provider": "MicrosoftFoundryAgent",
                    "agent_name": self.agent_name,
                    "agent_version": self.agent_version,
                    "content": "",
                    "detail": f"Agent run ended with status: {run.status}"
                }

            messages = project_client.agents.list_messages(thread_id=thread.id)
            content = ""
            if messages.data and messages.data[0].content:
                content = messages.data[0].content[0].text.value

            return {
                "ok": True,
                "provider": "MicrosoftFoundryAgent",
                "agent_name": self.agent_name,
                "agent_version": self.agent_version,
                "content": content,
                "detail": "Success"
            }
        except Exception as exc:
            logger.error("Error calling Azure Foundry Agent: %s", str(exc))
            return {
                "ok": False,
                "provider": "MicrosoftFoundryAgent",
                "agent_name": self.agent_name,
                "agent_version": self.agent_version,
                "content": "",
                "detail": f"Foundry Agent call failed: {exc}"
            }
