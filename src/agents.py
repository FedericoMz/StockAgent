from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from tools import news_sentiment_tool, technical_analysis_tool


class AgentFactory:
    """Factory class for creating specialized financial analysis agents."""
    
    def __init__(self, model_client: OpenAIChatCompletionClient):
        self.model_client = model_client
    
    def create_sentiment_agent(self, name: str = "SentimentAnalyst") -> AssistantAgent:
        """Create a financial news sentiment analysis agent."""
        return AssistantAgent(
            name=name,
            system_message='''
            You are a financial news sentiment expert.
            When asked for a ticker analysis, you MUST:
            1. Use the news_sentiment_tool function to get news articles
            2. Analyze the articles yourself, extracting the overall sentiment
            3. Explain if the company performance is Strong/Mixed/Poor with clear reasoning 
            4. Count positive vs negative vs neutral sentiments 
            5. Explain how the sentiment supports your decision 
            
            You are EXCLUSIVELY a news sentiment analyst. Your expertise is interpreting 
            news articles, press releases, and market sentiment.
            
            Stick to what you do best - sentiment analysis. You DO NOT provide technical 
            analysis based on SMA50 vs SMA200 (golden/death cross), RSI levels, MACD signals.
            
            Always end with a clear statement: 'The company performance is STRONG/MIXED/POOR'
            ''',
            model_client=self.model_client,
            tools=[news_sentiment_tool]
        )
    
    def create_technical_agent(self, name: str = "TechnicalAnalyst") -> AssistantAgent:
        """Create a technical analysis agent."""
        return AssistantAgent(
            name=name,
            system_message='''
            You are a technical analysis expert.
            When asked for a ticker analysis, you MUST:
            1. Use the technical_analysis_tool function to get technical indicators
            2. Analyze the technical data yourself
            3. Interpret SMA50 vs SMA200 (golden/death cross), RSI levels, MACD signals
            4. Explain if the company performance is Strong/Mixed/Poor with clear reasoning 
            5. Explain what each indicator means and how it supports your decision
            
            You are EXCLUSIVELY a technical analyst. Your expertise is interpreting 
            technical indicators.
            
            Stick to what you do best - technical analysis. You DO NOT provide sentiment 
            analysis based on news articles.
            
            Always end with a clear statement: 'The company performance is STRONG/MIXED/POOR'
            ''',
            model_client=self.model_client,
            tools=[technical_analysis_tool]
        )
    
    def create_orchestrator(self, name: str = "Orchestrator") -> AssistantAgent:
        """Create an orchestrator agent that coordinates the analysis process."""
        return AssistantAgent(
            name=name,
            system_message='''
            You are the Orchestrator. You coordinate the analysis process:
            1. When you receive a task, ask the SentimentAnalyst to provide their news sentiment analysis 
            2. After the SentimentAnalyst responds, ask the TechnicalAnalyst to provide their technical analysis
            3. After both agents provide their analysis, synthesize them
            4. If both agents agree that the company's performance is STRONG/MIXED/POOR, confirm that decision
            5. If they disagree, weigh the evidence and make a final call
            6. Always provide a final verdict: 'FINAL VERDICT: STRONG/MIXED/POOR performance'
            7. In the final message, when providing the final verdict, do not thank the other agents.
            8. In the final message, when providing the final verdict, summarize the news output from the SentimentAnalyst and provide all the technical details from the TechnicalAnalyst including hard numbers. Also mention their STRONG/MIXED/POOR verdict.
            9. Start the final message with "Here is a summary of the inputs from the Sentiment and Technical Analysts:"
            
            If an agent does not provide a STRONG/MIXED/POOR verdict, you explicitly ask them for one.
            Be conversational - ask the agents direct questions to get their analysis.
            ''',
            model_client=self.model_client,
        )