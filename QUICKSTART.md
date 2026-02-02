# Quick Start Guide

## Get Your Free Alpha Vantage API Key

1. Go to: **https://www.alphavantage.co/support/#api-key**
2. Enter your email and get a free API key (takes 30 seconds!)
3. Copy the API key

## Update Your .env File

Edit the `.env` file in the `investment_agent` folder:

```bash
# Replace "demo" with your actual API key
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

## Run Your Investment Research Agent

```bash
cd "/Users/tiffanywang/Desktop/AI/Retail Reserch Agent"
./run.sh
```

## Open Your Browser

Go to: **http://localhost:8001**

## Try These Questions

### Basic Queries
- "What's the current price of IBM?"
- "Analyze Microsoft (MSFT)"
- "Compare IBM and MSFT"
- "Should I invest in Apple (AAPL)?"

### Advanced Financial Analysis
- "Show me the income statement for Tesla (TSLA)"
- "What's the cash flow situation for Nvidia (NVDA)?"
- "Analyze the balance sheet for Microsoft (MSFT)"
- "Give me a comprehensive valuation analysis for Apple (AAPL)"

### Deep Dive Questions
- "Is Tesla (TSLA) overvalued based on its P/E ratio?"
- "How much debt does Ford (F) have compared to its equity?"
- "What's the free cash flow for Amazon (AMZN)?"
- "Compare the profitability of Google (GOOGL) vs Meta (META)"
- "Analyze the financial health of Boeing (BA)"

### Investment Strategy
- "Which is a better value investment: IBM or MSFT?"
- "What are the risks of investing in high P/E tech stocks?"
- "Should I invest in dividend stocks or growth stocks right now?"

## Why Alpha Vantage?

✅ **More Reliable** - No rate limiting issues like Yahoo Finance
✅ **Free Tier** - 25 API calls per day (perfect for testing)
✅ **Better Data** - More comprehensive fundamental data
✅ **All Tickers** - Works with any US stock ticker

## Demo Key Limitations

The demo key only works with major stocks:
- IBM, MSFT, AAPL, etc.

For all tickers, get your free key at: **https://www.alphavantage.co/support/#api-key**

---

**Enjoy researching stocks with AI!** 🚀📈
