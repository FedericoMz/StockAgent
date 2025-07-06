"""
Financial Analysis Multi-Agent System

A modular multi-agent system for comprehensive stock analysis using sentiment analysis
and technical indicators through AutoGen and MCP.
"""

from multi_agent_system import MultiAgentSystem
from agents import AgentFactory
from mcp_executor import MCPToolExecutor, get_mcp_executor
from tools import news_sentiment_tool, technical_analysis_tool

__version__ = "1.0.0"
__author__ = "Federico Mazzoni"
__email__ = "mazzoni.federico1@gmail.com"

__all__ = [
    "MultiAgentSystem",
    "AgentFactory", 
    "MCPToolExecutor",
    "get_mcp_executor",
    "news_sentiment_tool",
    "technical_analysis_tool"
]