import yfinance as yf
from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any

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
            
            articles.append(f"Article #{i+1}. {title} - {summary}")
            
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
        #formatted_indicators = ", ".join([ f"{k[0] if isinstance(k, tuple) else k}: {v}" for k, v in indicators.items()])

        #return formatted_indicators
        return indicators
    except Exception as e:
        return f"Error fetching technical analysis: {str(e)}"

# Create FastAPI app for HTTP endpoints
app = FastAPI(title="Financial Analysis MCP Server")

# Create the FastMCP server
mcp = FastMCP("financial-analysis-server")

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolResponse(BaseModel):
    result: str

@app.post("/tools/call", response_model=ToolResponse)
async def call_tool(tool_call: ToolCall):
    """HTTP endpoint to call MCP tools."""
    try:
        if tool_call.name == "news_sentiment_tool":
            ticker_symbol = tool_call.arguments.get("ticker_symbol")
            if not ticker_symbol:
                raise HTTPException(status_code=400, detail="ticker_symbol is required")
            result = news_sentiment_tool(ticker_symbol)
            return ToolResponse(result=result)
        
        elif tool_call.name == "technical_analysis_tool":
            ticker_symbol = tool_call.arguments.get("ticker_symbol")
            if not ticker_symbol:
                raise HTTPException(status_code=400, detail="ticker_symbol is required")
            result = technical_analysis_tool(ticker_symbol)
            return ToolResponse(result=result)
        
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_call.name}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {
                "name": "news_sentiment_tool",
                "description": "Analyze news sentiment for a stock ticker symbol",
                "parameters": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
                    }
                }
            },
            {
                "name": "technical_analysis_tool", 
                "description": "Perform technical analysis for a stock ticker symbol",
                "parameters": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
                    }
                }
            }
        ]
    }

def news_sentiment_tool(ticker_symbol: str) -> str:
    """
    Analyze news sentiment for a given stock ticker.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        News sentiment analysis results
    """
    sentiment_data = fetch_news_sentiment(ticker_symbol)
    return f"News sentiment analysis for {ticker_symbol}: {sentiment_data}"

def technical_analysis_tool(ticker_symbol: str) -> str:
    """
    Perform technical analysis for a given stock ticker.
    
    Args:
        ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Technical analysis indicators
    """
    indicators = fetch_technical_analysis(ticker_symbol)
    return f"Technical analysis for {ticker_symbol}: {indicators}"

if __name__ == "__main__":
    print("Starting Financial Analysis MCP Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)