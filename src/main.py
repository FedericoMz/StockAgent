import asyncio
import os
import argparse
from multi_agent_system import MultiAgentSystem


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Financial Analysis Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                      # Use defaults
    python main.py --model gpt-4       # Use GPT-4 model
    python main.py --server-url http://localhost:8001  # Custom server URL
    python main.py --ticker TSLA       # Analyze TSLA
    python main.py --model gpt-3.5-turbo --ticker MSFT --server-url http://localhost:9000
        """
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--server-url",
        default="http://localhost:8000",
        help="MCP server URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--ticker",
        default="AAPL",
        help="Stock ticker to analyze (default: AAPL)"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=6,
        help="Maximum number of conversation turns (default: 6)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress system information output"
    )
    return parser.parse_args()


async def main():
    """Main entry point for the financial analysis system."""
    args = parse_arguments()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Please set your OPENAI_API_KEY environment variable")
        return

    system = None
    try:
        system = MultiAgentSystem(
            model_name=args.model,
            max_turns=args.max_turns,
            mcp_server_url=args.server_url
        )

        if not args.quiet:
            print("Financial Analysis Multi-Agent System")
            print("=" * 40)
            info = system.get_system_info()
            print(f"Model: {info['model_name']}")
            print(f"MCP Server: {info['mcp_server_url']}")
            print(f"Target Ticker: {args.ticker}")
            print("=" * 40)

        result = await system.analyze_stock(args.ticker)
        final_verdict = dict(result)['messages'][-1].content
        print(f"\nFinal Result for {args.ticker}:")
        print(final_verdict)

    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
    finally:
        if system:
            try:
                await system.cleanup()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()