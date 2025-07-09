import yfinance as yf
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any, Optional, Union, List
import json


def fetch_news_sentiment(ticker_symbol):
    """Fetch news articles for a given ticker symbol"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news

        if not news:
            return "No recent news available for this ticker."

        articles = []
        for i in range(len(news)):
            title = news[i].get('content', {}).get('title', '')
            summary = news[i].get('content', {}).get('summary', '')
            articles.append(f"Article #{i + 1}. {title} - {summary}")

        return articles
    except Exception as e:
        return f"Error fetching news articles: {str(e)}"


def fetch_technical_analysis(ticker_symbol):
    """Fetch technical analysis indicators for a given ticker symbol"""
    try:
        data = yf.download(ticker_symbol, period="1y")
        data.reset_index(inplace=True)

        data["SMA50"] = data["Close"].rolling(window=50).mean()
        data["SMA200"] = data["Close"].rolling(window=200).mean()

        delta = data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        exp1 = data["Close"].ewm(span=12, adjust=False).mean()
        exp2 = data["Close"].ewm(span=26, adjust=False).mean()
        data["MACD"] = exp1 - exp2
        data["MACD_signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
        data["MACD_hist"] = data["MACD"] - data["MACD_signal"]

        latest = data.iloc[-1]
        indicators = latest[["SMA50", "SMA200", "RSI", "MACD", "MACD_signal", "MACD_hist"]]
        return indicators.to_dict()
    except Exception as e:
        return f"Error fetching technical analysis: {str(e)}"

app = FastAPI(title="Financial Analysis MCP Server")

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


# MCP Tool definitions
TOOLS = [
    {
        "name": "news_sentiment_tool",
        "description": "Analyze news sentiment for a given stock ticker",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
                }
            },
            "required": ["ticker_symbol"]
        }
    },
    {
        "name": "technical_analysis_tool",
        "description": "Perform technical analysis for a given stock ticker",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
                }
            },
            "required": ["ticker_symbol"]
        }
    }
]


def handle_list_tools(request_id):
    """Handle tools/list request"""
    return JSONRPCResponse(
        id=request_id,
        result={"tools": TOOLS}
    )


def handle_call_tool(request_id, params):
    """Handle tools/call request"""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "news_sentiment_tool":
            ticker_symbol = arguments.get("ticker_symbol")
            if not ticker_symbol:
                return JSONRPCResponse(
                    id=request_id,
                    error=JSONRPCError(code=-32602, message="ticker_symbol is required")
                )

            result = fetch_news_sentiment(ticker_symbol)
            return JSONRPCResponse(
                id=request_id,
                result={
                    "content": [{
                        "type": "text",
                        "text": f"News sentiment analysis for {ticker_symbol}: {result}"
                    }]
                }
            )

        elif tool_name == "technical_analysis_tool":
            ticker_symbol = arguments.get("ticker_symbol")
            if not ticker_symbol:
                return JSONRPCResponse(
                    id=request_id,
                    error=JSONRPCError(code=-32602, message="ticker_symbol is required")
                )

            result = fetch_technical_analysis(ticker_symbol)
            return JSONRPCResponse(
                id=request_id,
                result={
                    "content": [{
                        "type": "text",
                        "text": f"Technical analysis for {ticker_symbol}: {result}"
                    }]
                }
            )

        else:
            return JSONRPCResponse(
                id=request_id,
                error=JSONRPCError(code=-32601, message=f"Unknown tool: {tool_name}")
            )

    except Exception as e:
        return JSONRPCResponse(
            id=request_id,
            error=JSONRPCError(code=-32603, message=f"Internal error: {str(e)}")
        )


def handle_initialize(request_id, params):
    """Handle initialize request"""
    return JSONRPCResponse(
        id=request_id,
        result={
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "financial-analysis-server",
                "version": "1.0.0"
            }
        }
    )


def handle_single_request(body):
    """Handle a single JSON-RPC request"""
    try:
        rpc_request = JSONRPCRequest(**body)

        if rpc_request.method == "initialize":
            return handle_initialize(rpc_request.id, rpc_request.params or {})

        elif rpc_request.method == "tools/list":
            return handle_list_tools(rpc_request.id)

        elif rpc_request.method == "tools/call":
            return handle_call_tool(rpc_request.id, rpc_request.params or {})

        else:
            return JSONRPCResponse(
                id=rpc_request.id,
                error=JSONRPCError(code=-32601, message=f"Method not found: {rpc_request.method}")
            )

    except Exception as e:
        return JSONRPCResponse(
            error=JSONRPCError(code=-32603, message=f"Internal error: {str(e)}")
        )


@app.post("/mcp")
@app.post("/")
async def mcp_endpoint(request: Request):
    """Single MCP endpoint for all JSON-RPC communication"""
    try:
        body = await request.json()

        # Handle single request
        if isinstance(body, dict):
            response = handle_single_request(body)
            if isinstance(response, JSONRPCResponse):
                response_dict = response.model_dump(exclude_none=True)
                return response_dict
            return response

        # Handle batch requests
        elif isinstance(body, list):
            responses = []
            for req in body:
                response = handle_single_request(req)
                if isinstance(response, JSONRPCResponse):
                    responses.append(response.model_dump(exclude_none=True))
                else:
                    responses.append(response)
            return responses

        else:
            error_response = JSONRPCResponse(
                error=JSONRPCError(code=-32700, message="Parse error")
            )
            return error_response.model_dump(exclude_none=True)

    except json.JSONDecodeError:
        error_response = JSONRPCResponse(
            error=JSONRPCError(code=-32700, message="Parse error")
        )
        return error_response.model_dump(exclude_none=True)
    except Exception as e:
        error_response = JSONRPCResponse(
            error=JSONRPCError(code=-32603, message=f"Internal error: {str(e)}")
        )
        return error_response.model_dump(exclude_none=True)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "server": "financial-analysis-server"}


@app.get("/info")
async def info():
    return {
        "name": "financial-analysis-server",
        "version": "1.0.0",
        "description": "MCP server for financial analysis",
        "protocol": "JSON-RPC 2.0",
        "transport": "Streamable HTTP",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    print("Starting Financial Analysis MCP Server...")
    print("Available tools:")
    print("  - news_sentiment_tool: Get news articles and sentiment for a ticker")
    print("  - technical_analysis_tool: Get technical indicators and trend analysis")
    print("\nMCP endpoint: /mcp (JSON-RPC 2.0)")
    print("Health check: /health")
    print("Info: /info")
    print("\nStarting server on http://0.0.0.0:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000)