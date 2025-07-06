import asyncio
from typing import Any
from mcp_executor import get_mcp_executor


def _handle_async_call(coro) -> Any:
    """
    Handle async calls in both sync and async contexts.
    Supports nested event loops in Jupyter notebooks.
    """
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(coro)
        while not task.done():
            pass
        return task.result()
    except RuntimeError:
        return asyncio.run(coro)


def news_sentiment_tool(ticker_symbol: str) -> str:
    """
    Analyze news sentiment for a given stock ticker.
    
    Args:
        ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        str: News sentiment analysis results
    """
    mcp_executor = get_mcp_executor()
    return _handle_async_call(
        mcp_executor.call_tool("news_sentiment_tool", {"ticker_symbol": ticker_symbol})
    )


def technical_analysis_tool(ticker_symbol: str) -> str:
    """
    Perform technical analysis for a given stock ticker.
    
    Args:
        ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        str: Technical analysis indicators
    """
    mcp_executor = get_mcp_executor()
    return _handle_async_call(
        mcp_executor.call_tool("technical_analysis_tool", {"ticker_symbol": ticker_symbol})
    )