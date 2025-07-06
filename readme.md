# StockAgent

A modular multi-agent system for stock analysis using sentiment analysis and technical indicators through AutoGen and a custom MCP yfinance server.

## Features

- **Multi-Agent AutoGen Architecture**: Specialized AutoGen agents for sentiment analysis, technical analysis, and orchestration
- **MCP Integration**: Seamless integration with Model Context Protocol for tool execution
- **Async Support**: Full async/await support with Jupyter notebook compatibility
- **Extensible**: Easy to add new agents and tools!

The app takes a company ticker as input (e.g., _AAPL_ for Apple). The Orchestrator agent coordinates with specialized agents.
The Sentiment Analysis agent fetches and analyzes recent news, while the Technical Analysis agent retrieves technical indicators, both using the yfinance MCP server.
After receiving analysis from both agents, the Orchestrator synthesizes their findings and provides the user with a final verdict on the company's performance.

## Disclaimer
This project is for educational and research purposes only. **It does not constitute financial advice or investment recommendations.**

The code demonstrates how to build multi-agent AI pipelines for automated financial data analysis. It is not intended to provide personalized recommendations on buying, holding, or selling any financial instrument.

Always consult with a licensed financial advisor or investment professional before making any investment decisions. The author assumes no responsibility for any actions taken based on the outputs of this software.

Use this code at your own risk.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Quick Start

### Command Line Usage

Before running the main app, you start the MCP server
```bash
python mcp_server.py
```

Afterwards:
```bash
# Basic usage with defaults (gpt-4o-mini, localhost:8000, AAPL)
python main.py

# Specify ticker to analyze
python main.py --ticker NTDOY

# Specify custom model
python main.py --model gpt-4o

# Specify custom server URL
python main.py --server-url http://localhost:8001

# Combine options
python main.py --model gpt-3.5-turbo --ticker MSFT --server-url http://localhost:9000

# See all options
python main.py --help
```
### Jupyter Notebook Usage

```python
from multi_agent_system import MultiAgentSystem

system = MultiAgentSystem()

result = await system.analyze_stock("AAPL")
print(dict(result)['messages'][-1].content)
await system.cleanup()

```

### Output example for Apple (AAPL)
```bash
Here is a summary of the inputs from the Sentiment and Technical Analysts:

**Sentiment Analysis:**
The news sentiment around AAPL reflects a mix of articles covering various topics, but notably, there was concern regarding Jim Cramer's observations on AAPL's disappointing share performance. This raises questions about investor confidence in Apple's current market positioning. Overall, the sentiment appears to lean towards caution.

**Technical Analysis:**
Technical indicators show:
- **SMA50:** 203.65 (bearish signal with SMAs indicating potential downtrend)
- **SMA200:** 222.67
- **RSI:** 74.80 (indicating overbought conditions)
- **MACD:** 1.77 (indicating momentum but showing signs of weakening)
- **MACD Signal:** 0.05
- **MACD Histogram:** 1.72

The analysis indicates a **death cross**, an overbought RSI, and weakening momentum, all contributing to a negative outlook for AAPL's stock performance.

Given that the **SentimentAnalyst** indicated a cautious sentiment due to Jim Cramer's remarks and the **TechnicalAnalyst** confirmed a **POOR** performance assessment based on the technical indicators, the final verdict stands as follows:

**FINAL VERDICT: POOR performance.**

AAPL is facing challenges in market sentiment and technical signals, which suggest a bearish outlook for the stock.
```
