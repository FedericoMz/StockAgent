import os
from typing import Optional, List, Dict, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents import AgentFactory
from mcp_executor import cleanup_mcp_executor


class MultiAgentSystem:
    """
    Main class that orchestrates the multi-agent financial analysis system.
    """

    def __init__(
            self,
            model_name: str = "gpt-4o-mini",
            max_turns: int = 6,
            mcp_server_url: Optional[str] = None
    ):
        """
        Initialize the multi-agent system.

        Args:
            model_name: OpenAI model to use (default: gpt-4o-mini)
            max_turns: Maximum number of turns in the group chat
            mcp_server_url: MCP server URL (if None, will use environment variable or default)
        """
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.max_turns = max_turns

        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key must be set as OPENAI_API_KEY environment variable")

        if mcp_server_url:
            os.environ["MCP_SERVER_URL"] = mcp_server_url
        elif not os.getenv("MCP_SERVER_URL"):
            os.environ["MCP_SERVER_URL"] = "http://localhost:8000"

        self.model_client = OpenAIChatCompletionClient(
            model=self.model_name,
            api_key=self.openai_api_key
        )

        self.agent_factory = AgentFactory(self.model_client)
        self.agents = self._create_agents()
        self.team = self._create_team()

    def _create_agents(self) -> Dict[str, AssistantAgent]:
        """Create all agents for the system."""
        return {
            "sentiment_analyst": self.agent_factory.create_sentiment_agent("SentimentAnalyst"),
            "technical_analyst": self.agent_factory.create_technical_agent("TechnicalAnalyst"),
            "orchestrator": self.agent_factory.create_orchestrator("Orchestrator")
        }

    def _create_team(self) -> RoundRobinGroupChat:
        """Create the team with all agents."""
        participants = list(self.agents.values())

        return RoundRobinGroupChat(
            participants=participants,
            max_turns=self.max_turns,
            termination_condition=TextMentionTermination("FINAL VERDICT")
        )

    async def analyze_stock(self, ticker: str) -> dict:
        """
        Perform comprehensive stock analysis using multiple agents.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Analysis result
        """
        task = (
            f"Provide an analysis for {ticker}'s performance today "
            f"based on both news sentiment and technical analysis."
        )

        print(f"Starting analysis for {ticker}...")

        try:
            result = await self.team.run(task=task)
            print(f"\nAnalysis completed for {ticker}")
            return result

        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up resources."""
        await cleanup_mcp_executor()

    def list_agents(self) -> List[str]:
        """Get list of all agent names."""
        return list(self.agents.keys())

    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the system configuration."""
        return {
            "model_name": self.model_name,
            "max_turns": self.max_turns,
            "agents": self.list_agents(),
            "mcp_server_url": os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        }