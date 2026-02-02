# Investment Research Agent

An AI-powered investment research assistant built with **Google's Agent Development Kit (ADK)**. This agent helps you analyze stocks, compare investments, and research market trends using real-time financial data and AI analysis.

## Features

- **Real-time Stock Analysis**: Get current prices, performance metrics, and trends
- **Fundamental Analysis**: Access key financial metrics (P/E ratio, market cap, revenue growth, etc.)
- **Stock Comparison**: Compare multiple stocks side-by-side
- **News Integration**: Get recent news headlines for any stock
- **AI-Powered Insights**: Google's Gemini AI analyzes data and provides actionable insights
- **Interactive Web UI**: Official Google ADK web interface for easy interaction

## Prerequisites

- Python 3.10 or higher
- Google API Key (get one at [Google AI Studio](https://aistudio.google.com/apikey))

## Quick Start

### 1. Navigate to the project directory

```bash
cd "/Users/tiffanywang/Desktop/AI/Retail Reserch Agent"
```

### 2. Activate the virtual environment

```bash
source venv/bin/activate
```

### 3. Install dependencies (if not already installed)

```bash
pip install -r requirements.txt
```

### 4. Configure your Google API Key

Your API key is already configured in `.env`. If you need to change it:

```bash
GOOGLE_API_KEY=your_api_key_here
```

### 5. Run the agent

Use the convenient run script:

```bash
./run.sh
```

Or run manually:

```bash
source venv/bin/activate
adk web --port 8000
```

### 6. Open in browser

Navigate to: **http://localhost:8000**

You'll see the official Google ADK web interface!

## How to Use

### Example Queries

**Stock Analysis:**
- "What's the current price of Apple (AAPL)?"
- "Analyze Microsoft (MSFT) for me - should I invest?"
- "Get the fundamentals for Tesla (TSLA)"
- "What are the key metrics for Nvidia (NVDA)?"

**Stock Comparison:**
- "Compare Apple and Microsoft"
- "Which is better: Tesla or Ford?"
- "Compare the fundamentals of GOOGL and META"

**News & Trends:**
- "What's the latest news on Apple?"
- "Show me recent news for NVDA"

**Sector Analysis:**
- "Which tech stocks are performing well?"
- "Analyze the AI chip sector"

## Agent Tools

The agent has access to these specialized tools:

### Basic Tools

**1. `get_stock_price(ticker)`**
- Current price and daily/monthly changes
- Recent high/low prices
- Average trading volume
- Performance percentages

**2. `get_stock_fundamentals(ticker)`**
- Company overview (name, sector, industry)
- Valuation metrics (P/E, PEG, Price-to-Book)
- Profitability (profit margin, EPS)
- Analyst targets and 52-week range
- Dividend yield and beta

**3. `get_stock_info(ticker)`**
- Combined overview with price and fundamentals
- Quick snapshot for initial analysis

**4. `compare_stocks(ticker1, ticker2)`**
- Side-by-side comparison of two stocks
- Price and fundamental data for both
- Helpful for investment decisions

### Advanced Financial Analysis Tools

**5. `get_income_statement(ticker)`**
- Total revenue and gross profit
- Operating income and net income
- EBITDA and EPS
- Research & Development spending
- Year-over-year comparisons

**6. `get_balance_sheet(ticker)`**
- Total assets and liabilities
- Shareholder equity
- Current assets vs. current liabilities
- Cash and cash equivalents
- Short-term and long-term debt
- Financial health indicators

**7. `get_cash_flow(ticker)`**
- Operating cash flow
- Capital expenditures
- Free cash flow
- Dividends paid
- Cash position changes

**8. `calculate_valuation_metrics(ticker)`**
- Comprehensive valuation analysis
- P/E ratio assessment (undervalued/overvalued)
- Market cap and EPS analysis
- Price-to-book and PEG ratios
- Analyst price targets
- Automated valuation commentary

## Architecture

### Google ADK Structure

```
Retail Research Agent/
├── agent.py              # Main agent definition with tools
├── __init__.py          # Package initialization
├── .env                 # API key configuration
├── requirements.txt     # Python dependencies
├── run.sh              # Startup script
└── README.md           # Documentation
```

### How It Works

1. **User Query**: You ask a question in the web interface
2. **Agent Processing**: The AI agent (Gemini 1.5 Flash) processes your question
3. **Tool Selection**: The agent decides which tools to use (e.g., get_stock_price, get_stock_fundamentals)
4. **Data Retrieval**: Tools fetch real-time data from Yahoo Finance
5. **AI Analysis**: The agent analyzes the data and generates insights
6. **Response**: You receive a comprehensive, data-driven answer

## Command Line Interface

You can also use the CLI instead of the web interface:

```bash
source venv/bin/activate
adk run
```

Then type your questions directly in the terminal.

## Technologies Used

- **Google ADK**: Agent framework with built-in UI
- **Google Gemini 1.5 Flash**: AI model for analysis
- **yfinance**: Real-time stock market data
- **Python 3.10+**: Core programming language

## Agent Capabilities

The agent can:
- ✅ Fetch real-time stock prices and performance metrics
- ✅ Analyze fundamental financial data
- ✅ Compare multiple stocks
- ✅ Retrieve and summarize recent news
- ✅ Provide investment insights based on data
- ✅ Answer questions about market trends
- ✅ Explain complex financial metrics

## Important Disclaimers

⚠️ **This tool provides information for research purposes only**
- It does NOT provide financial advice
- Always do your own due diligence before making investment decisions
- The AI analysis should not be the sole factor in investment decisions
- Market data may be delayed and may not reflect real-time prices
- Past performance does not guarantee future results

## Known Limitations

### Yahoo Finance API Rate Limiting
This agent uses the free Yahoo Finance API (via yfinance), which has the following limitations:

- **Rate Limits**: Yahoo Finance may block requests if you make too many queries in a short time (Error 429)
- **Data Availability**: Some tickers may not return data due to API issues
- **Reliability**: The free API can be unreliable and may experience outages

**If you encounter errors:**
1. Wait a few minutes before making another request
2. Verify the ticker symbol is correct (use Yahoo Finance website to confirm)
3. Try a different, well-known ticker (e.g., AAPL, MSFT, GOOGL)
4. The agent will still provide general analysis even when real-time data is unavailable

**For production use**, consider:
- Using a paid financial data API (Alpha Vantage, IEX Cloud, Polygon.io)
- Implementing caching to reduce API calls
- Adding rate limiting to your requests

## Troubleshooting

### "adk: command not found"
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### "GOOGLE_API_KEY not configured"
Check that your `.env` file exists and contains a valid API key.

### Import errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Port already in use
Change the port in `run.sh`:
```bash
adk web --port 8001
```

## Advanced Usage

### Custom Tools

You can add more tools to `agent.py` by defining new functions and adding them to the `tools` list:

```python
def my_custom_tool(param: str) -> dict:
    """Description of what this tool does."""
    return {"result": "data"}

root_agent = Agent(
    model='gemini-1.5-flash',
    name='investment_research_agent',
    tools=[
        get_stock_price,
        get_stock_fundamentals,
        my_custom_tool  # Add your tool here
    ]
)
```

### Changing the AI Model

Edit `agent.py` to use a different model:

```python
root_agent = Agent(
    model='gemini-1.5-pro',  # More capable but slower
    # or 'gemini-2.0-flash-exp' for experimental features
    ...
)
```

## License

This project is for educational and research purposes.

## Learn More

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Get Started with Python ADK](https://google.github.io/adk-docs/get-started/python/)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)

## Support

For issues or questions:
1. Check the [Google ADK docs](https://google.github.io/adk-docs/)
2. Ensure your environment is properly set up
3. Verify your API key is valid

---

**Built with Google's Agent Development Kit (ADK)**
