import asyncio
from typing import Any, Coroutine
from mcp_executor import get_mcp_executor


def _handle_async_call(coro: Coroutine) -> Any:
    return asyncio.run(coro)


async def news_sentiment_tool(ticker_symbol: str) -> str:
    """
    Analyze news sentiment for a given stock ticker.

    Args:
        ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        str: News sentiment analysis results
    """
    try:
        mcp_executor = get_mcp_executor()
        result = await mcp_executor.call_tool(
            "news_sentiment_tool", {"ticker_symbol": ticker_symbol}
        )
        return result
    except Exception as e:
        return f"Error in news_sentiment_tool: {str(e)}"


async def technical_analysis_tool(ticker_symbol: str) -> str:
    """
    Perform technical analysis for a given stock ticker.

    Args:
        ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        str: Technical analysis indicators
    """
    try:
        mcp_executor = get_mcp_executor()
        result = await mcp_executor.call_tool(
            "technical_analysis_tool", {"ticker_symbol": ticker_symbol}
        )
        return result
    except Exception as e:
        return f"Error in technical_analysis_tool: {str(e)}"
