"""
Investment Research Agent using Google's Agent Development Kit (ADK)
This agent helps analyze stocks and assets for investment decisions.
Uses Financial Modeling Prep API for reliable stock data (250 free calls/day).
"""

import os
import tempfile
from typing import Dict, Any
from datetime import datetime
import requests
from google.adk.agents.llm_agent import Agent
from google.cloud import discoveryengine_v1 as discoveryengine
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Handle Google Cloud credentials
# Option 1: Direct file path via GOOGLE_APPLICATION_CREDENTIALS (for local dev)
# Option 2: JSON string via GOOGLE_APPLICATION_CREDENTIALS_JSON (for production/Render)
credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
gcp_credentials = None

if credentials_json:
    try:
        # Create a temporary file to store credentials from JSON string
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write(credentials_json)
            credentials_path = f.name
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        # Load credentials with proper scopes and quota project
        gcp_credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        # Set quota project to the datastore's project
        project_id = os.getenv('GCP_PROJECT_ID')
        if project_id:
            gcp_credentials = gcp_credentials.with_quota_project(project_id)
        print(f"✓ Google Cloud credentials loaded from environment variable (JSON)")
    except Exception as e:
        print(f"⚠ Warning: Could not process GCP credentials: {e}")
elif credentials_path:
    # Ensure the env var is set (dotenv may have loaded it)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    if os.path.exists(credentials_path):
        # Load credentials with proper scopes and quota project
        gcp_credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        # Set quota project to the datastore's project
        project_id = os.getenv('GCP_PROJECT_ID')
        if project_id:
            gcp_credentials = gcp_credentials.with_quota_project(project_id)
        print(f"✓ Google Cloud credentials loaded from file: {credentials_path}")
    else:
        print(f"⚠ Warning: Credentials file not found: {credentials_path}")
else:
    print("ℹ No Google Cloud credentials configured")

# Configure Vertex AI Search to connect to your data store
# Get configuration from environment variables
VERTEX_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
VERTEX_LOCATION = os.getenv('VERTEX_LOCATION', 'us')
VERTEX_DATA_STORE_ID = os.getenv('VERTEX_DATA_STORE_ID')

# Initialize Discovery Engine client for direct API access
vertex_search_available = False

if VERTEX_PROJECT_ID and VERTEX_DATA_STORE_ID and gcp_credentials:
    try:
        # Test connection by creating client with regional endpoint and explicit credentials
        client_options = {
            "api_endpoint": f"{VERTEX_LOCATION}-discoveryengine.googleapis.com"}
        test_client = discoveryengine.SearchServiceClient(
            credentials=gcp_credentials,
            client_options=client_options)
        vertex_search_available = True
        print(f"✓ Vertex AI Search initialized successfully")
        print(f"  Project: {VERTEX_PROJECT_ID}")
        print(f"  Location: {VERTEX_LOCATION}")
        print(f"  Data Store: {VERTEX_DATA_STORE_ID}")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize Vertex AI Search: {e}")
        print(f"  Agent will work without research context grounding.")
        vertex_search_available = False
elif not gcp_credentials:
    print("ℹ Vertex AI Search not available - no credentials configured.")
else:
    print("ℹ Vertex AI Search not configured.")
    print("  Set GCP_PROJECT_ID, VERTEX_LOCATION, and VERTEX_DATA_STORE_ID in .env to enable.")


def search_investment_research(query: str) -> Dict[str, Any]:
    """
    Search curated investment research, frameworks, and methodologies from your data store.
    Use this tool to find answers about investment approaches, valuation methods, and best practices.

    Args:
        query: Search query about investment methodology, frameworks, or concepts

    Returns:
        Dictionary containing relevant research results with titles, snippets, and sources
    """
    if not vertex_search_available:
        return {
            "status": "info",
            "message": "Vertex AI Search is not available. The agent will continue without research context grounding. This feature requires Google Cloud authentication which is configured for local development only."
        }

    try:
        # Create client with regional endpoint and explicit credentials
        client_options = {
            "api_endpoint": f"{VERTEX_LOCATION}-discoveryengine.googleapis.com"}
        client = discoveryengine.SearchServiceClient(
            credentials=gcp_credentials,
            client_options=client_options)

        # Build serving config path manually to ensure correct project ID is used
        serving_config = f"projects/{VERTEX_PROJECT_ID}/locations/{VERTEX_LOCATION}/collections/default_collection/dataStores/{VERTEX_DATA_STORE_ID}/servingConfigs/default_search"

        # Create search request with content extraction enabled
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
                max_snippet_count=3,
            ),
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=1,
                max_extractive_segment_count=3,
            ),
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=5,
                include_citations=True,
            ),
        )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=10,
            content_search_spec=content_search_spec,
        )

        # Execute search
        response = client.search(request)

        # Get the AI-generated summary if available
        summary_text = ""
        if response.summary and response.summary.summary_text:
            summary_text = response.summary.summary_text

        # Parse results with enhanced content extraction
        results = []
        for idx, result in enumerate(response.results, 1):
            doc_data = result.document.derived_struct_data

            # Extract content from multiple sources
            content_parts = []

            # Try extractive_answers first (most relevant)
            extractive_answers = doc_data.get('extractive_answers', [])
            for answer in extractive_answers:
                if hasattr(answer, 'get'):
                    content = answer.get('content', '')
                    if content:
                        content_parts.append(content)

            # Try extractive_segments
            extractive_segments = doc_data.get('extractive_segments', [])
            for segment in extractive_segments:
                if hasattr(segment, 'get'):
                    content = segment.get('content', '')
                    if content and content not in content_parts:
                        content_parts.append(content)

            # Try snippets
            snippets = doc_data.get('snippets', [])
            for snippet in snippets:
                if hasattr(snippet, 'get'):
                    content = snippet.get('snippet', '')
                    if content and content not in content_parts:
                        content_parts.append(content)

            # Combine all content
            combined_content = ' ... '.join(content_parts) if content_parts else ''

            results.append({
                "citation_number": idx,
                "title": doc_data.get('title', 'Untitled Research Document'),
                "content": combined_content if combined_content else 'Content available in source document',
                "link": doc_data.get('link', ''),
                "source": "Proprietary Research Database"
            })

        if not results:
            return {
                "status": "success",
                "query": query,
                "message": "No results found in your research database for this query.",
                "results": []
            }

        return {
            "status": "success",
            "query": query,
            "summary": summary_text if summary_text else None,
            "results_count": len(results),
            "results": results,
            "note": "These are proprietary research documents. Cite the document title when using insights."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error searching investment research: {str(e)}"
        }


def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for investment news, analyst reports, and company information using Tavily.
    Use this to find recent news, earnings announcements, analyst opinions, or industry trends.

    Args:
        query: Search query (e.g., "AAPL earnings", "Tesla news", "semiconductor industry trends")
        num_results: Number of results to return (default 5, max 10)

    Returns:
        Dictionary with search results including titles, content summaries, and links
    """
    try:
        from tavily import TavilyClient

        api_key = os.getenv('TAVILY_API_KEY')

        if not api_key or api_key == 'your_tavily_api_key_here':
            return {
                "status": "info",
                "message": "Web search is not configured. Set TAVILY_API_KEY in .env to enable web search.",
                "setup_url": "https://tavily.com"
            }

        # Limit results to prevent excessive API usage
        num_results = min(num_results, 10)

        # Initialize Tavily client
        client = TavilyClient(api_key=api_key)

        # Perform search with options optimized for investment research
        response = client.search(
            query=query,
            max_results=num_results,
            search_depth="advanced",  # More comprehensive results
            include_raw_content=False,  # Get cleaned content
            include_domains=None,  # Search all domains
            exclude_domains=None
        )

        if not response.get('results'):
            return {
                "status": "success",
                "query": query,
                "message": "No results found for this query.",
                "results": []
            }

        # Parse results
        results = []
        for item in response['results']:
            results.append({
                "title": item.get('title', 'No title'),
                # Tavily provides cleaned, summarized content
                "content": item.get('content', 'No content'),
                "snippet": item.get('content', '')[:200] + '...' if len(item.get('content', '')) > 200 else item.get('content', ''),
                "link": item.get('url', ''),
                "score": item.get('score', 0)  # Relevance score from Tavily
            })

        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "results": results,
            "note": "Tavily provides AI-optimized search results with cleaned content. Use these sources to gather recent news, earnings info, and company context."
        }

    except ImportError:
        return {
            "status": "error",
            "message": "Tavily library not installed. Run: pip install tavily-python"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error searching web with Tavily: {str(e)}"
        }


def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Get current stock price and recent performance data using Financial Modeling Prep (250 free calls/day).

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing current price, change, and performance metrics
    """
    try:
        api_key = os.getenv('FMP_API_KEY', 'demo')

        # Get real-time quote using stable endpoint
        quote_url = f"https://financialmodelingprep.com/stable/quote?symbol={ticker}&apikey={api_key}"
        response = requests.get(quote_url)
        response.raise_for_status()
        quote_data = response.json()

        if not quote_data or len(quote_data) == 0:
            return {
                "status": "error",
                "message": f"No price data found for {ticker}. Please verify the ticker symbol."
            }

        data = quote_data[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "current_price": round(float(data.get('price', 0)), 2),
            "change_1day": round(float(data.get('change', 0)), 2),
            "change_1day_percent": round(float(data.get('changesPercentage', 0)), 2),
            "high_recent": round(float(data.get('yearHigh', 0)), 2),
            "low_recent": round(float(data.get('yearLow', 0)), 2),
            "average_volume": int(data.get('avgVolume', 0)),
            "market_cap": data.get('marketCap', 'N/A'),
            "pe_ratio": data.get('pe', 'N/A')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching price data for {ticker}: {str(e)}"
        }


def get_stock_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    Get fundamental financial metrics for a stock using Financial Modeling Prep (250 free calls/day).

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing key financial metrics and company information
    """
    try:
        api_key = os.getenv('FMP_API_KEY', 'demo')

        # Get company profile using stable endpoint
        profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={api_key}"
        response = requests.get(profile_url)
        response.raise_for_status()
        profile_data = response.json()

        if not profile_data or len(profile_data) == 0:
            return {
                "status": "error",
                "message": f"No fundamental data found for {ticker}."
            }

        data = profile_data[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "company_name": data.get('companyName', 'N/A'),
            "sector": data.get('sector', 'N/A'),
            "industry": data.get('industry', 'N/A'),
            "market_cap": data.get('mktCap', 'N/A'),
            "pe_ratio": data.get('pe', 'N/A'),
            "peg_ratio": 'N/A',  # Not in basic profile
            "price_to_book": data.get('priceToBook', 'N/A'),
            "dividend_yield": data.get('lastDiv', 'N/A'),
            "beta": data.get('beta', 'N/A'),
            "eps": 'N/A',  # Need separate call
            "52_week_high": data.get('range', 'N/A'),
            "52_week_low": data.get('range', 'N/A'),
            "description": data.get('description', 'N/A')[:200] + '...' if data.get('description') else 'N/A'
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching fundamentals for {ticker}: {str(e)}"
        }


def compare_stocks(ticker1: str, ticker2: str) -> Dict[str, Any]:
    """
    Compare two stocks side by side with key metrics.

    Args:
        ticker1: First stock ticker symbol
        ticker2: Second stock ticker symbol

    Returns:
        Dictionary containing comparison data for both stocks
    """
    try:
        stock1_price = get_stock_price(ticker1)
        stock1_fundamentals = get_stock_fundamentals(ticker1)

        stock2_price = get_stock_price(ticker2)
        stock2_fundamentals = get_stock_fundamentals(ticker2)

        return {
            "status": "success",
            "comparison": {
                ticker1.upper(): {
                    "price_data": stock1_price,
                    "fundamentals": stock1_fundamentals
                },
                ticker2.upper(): {
                    "price_data": stock2_price,
                    "fundamentals": stock2_fundamentals
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error comparing stocks: {str(e)}"
        }


def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Get a quick overview of a stock including basic info and latest price.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with company info and current price
    """
    try:
        price_data = get_stock_price(ticker)
        fund_data = get_stock_fundamentals(ticker)

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "price_info": price_data,
            "company_info": fund_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching stock info for {ticker}: {str(e)}"
        }


def get_income_statement(ticker: str) -> Dict[str, Any]:
    """
    Get the latest income statement data for a stock using Financial Modeling Prep.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with income statement data including revenue, profit, etc.
    """
    try:
        api_key = os.getenv('FMP_API_KEY', 'demo')

        # Get annual income statement using stable endpoint
        url = f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return {
                "status": "error",
                "message": f"No income statement data found for {ticker}."
            }

        latest = data[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "fiscal_date": latest.get('date', 'N/A'),
            "total_revenue": latest.get('revenue', 'N/A'),
            "gross_profit": latest.get('grossProfit', 'N/A'),
            "operating_income": latest.get('operatingIncome', 'N/A'),
            "net_income": latest.get('netIncome', 'N/A'),
            "ebitda": latest.get('ebitda', 'N/A'),
            "eps": latest.get('eps', 'N/A'),
            "research_development": latest.get('researchAndDevelopmentExpenses', 'N/A')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching income statement for {ticker}: {str(e)}"
        }


def get_balance_sheet(ticker: str) -> Dict[str, Any]:
    """
    Get the latest balance sheet data for a stock using Financial Modeling Prep.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with balance sheet data including assets, liabilities, equity
    """
    try:
        api_key = os.getenv('FMP_API_KEY', 'demo')

        # Get annual balance sheet using stable endpoint
        url = f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ticker}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return {
                "status": "error",
                "message": f"No balance sheet data found for {ticker}."
            }

        latest = data[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "fiscal_date": latest.get('date', 'N/A'),
            "total_assets": latest.get('totalAssets', 'N/A'),
            "total_liabilities": latest.get('totalLiabilities', 'N/A'),
            "total_shareholder_equity": latest.get('totalStockholdersEquity', 'N/A'),
            "current_assets": latest.get('totalCurrentAssets', 'N/A'),
            "current_liabilities": latest.get('totalCurrentLiabilities', 'N/A'),
            "cash_and_equivalents": latest.get('cashAndCashEquivalents', 'N/A'),
            "long_term_debt": latest.get('longTermDebt', 'N/A'),
            "short_term_debt": latest.get('shortTermDebt', 'N/A')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching balance sheet for {ticker}: {str(e)}"
        }


def get_cash_flow(ticker: str) -> Dict[str, Any]:
    """
    Get the latest cash flow statement data for a stock using Financial Modeling Prep.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with cash flow data
    """
    try:
        api_key = os.getenv('FMP_API_KEY', 'demo')

        # Get annual cash flow using stable endpoint
        url = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return {
                "status": "error",
                "message": f"No cash flow data found for {ticker}."
            }

        latest = data[0]

        # Calculate free cash flow
        ocf = latest.get('operatingCashFlow', 0)
        capex = latest.get('capitalExpenditure', 0)
        free_cf = ocf - \
            abs(capex) if ocf and capex else latest.get('freeCashFlow', 'N/A')

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "fiscal_date": latest.get('date', 'N/A'),
            "operating_cash_flow": ocf,
            "capital_expenditures": capex,
            "free_cash_flow": free_cf,
            "dividends_paid": latest.get('dividendsPaid', 'N/A'),
            "change_in_cash": latest.get('netChangeInCash', 'N/A')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching cash flow for {ticker}: {str(e)}"
        }


def calculate_valuation_metrics(ticker: str) -> Dict[str, Any]:
    """
    Calculate key valuation metrics and ratios for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with calculated valuation metrics
    """
    try:
        # Get necessary data
        fundamentals = get_stock_fundamentals(ticker)
        price_data = get_stock_price(ticker)

        if fundamentals.get('status') == 'error' or price_data.get('status') == 'error':
            return {
                "status": "error",
                "message": "Unable to calculate metrics - fundamental or price data unavailable"
            }

        current_price = price_data.get('current_price', 0)
        pe_ratio = fundamentals.get('pe_ratio', 'N/A')
        market_cap = fundamentals.get('market_cap', 'N/A')
        eps = fundamentals.get('eps', 'N/A')

        # Build valuation analysis
        analysis = {
            "status": "success",
            "ticker": ticker.upper(),
            "current_price": current_price,
            "pe_ratio": pe_ratio,
            "market_cap": market_cap,
            "earnings_per_share": eps,
            "price_to_book": fundamentals.get('price_to_book', 'N/A'),
            "peg_ratio": fundamentals.get('peg_ratio', 'N/A'),
            "dividend_yield": fundamentals.get('dividend_yield', 'N/A'),
            "analyst_target": fundamentals.get('analyst_target', 'N/A')
        }

        return analysis

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error calculating valuation metrics: {str(e)}"
        }


def generate_investment_report(ticker: str) -> Dict[str, Any]:
    """
    Generate a comprehensive investment research report for a stock.
    This is a unique feature that combines all available data into a structured report.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with complete investment analysis
    """
    try:
        # Gather all data
        price = get_stock_price(ticker)
        fundamentals = get_stock_fundamentals(ticker)
        income = get_income_statement(ticker)
        balance = get_balance_sheet(ticker)
        cash_flow = get_cash_flow(ticker)
        valuation = calculate_valuation_metrics(ticker)

        # Compile comprehensive report
        report = {
            "status": "success",
            "ticker": ticker.upper(),
            "report_date": "Current",
            "sections": {
                "price_performance": price,
                "company_overview": fundamentals,
                "income_statement": income,
                "balance_sheet": balance,
                "cash_flow": cash_flow,
                "valuation_analysis": valuation
            },
            "report_type": "Comprehensive Investment Research Report",
            "note": "This automated report provides real-time financial data and analysis."
        }

        return report

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating investment report: {str(e)}"
        }


def calculate_financial_ratios(ticker: str) -> Dict[str, Any]:
    """
    Calculate advanced financial ratios not commonly provided by ChatGPT.
    Includes liquidity, profitability, and efficiency ratios.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with calculated financial ratios
    """
    try:
        balance = get_balance_sheet(ticker)
        income = get_income_statement(ticker)

        if balance.get('status') == 'error' or income.get('status') == 'error':
            return {
                "status": "error",
                "message": "Unable to calculate ratios - financial statement data unavailable"
            }

        ratios = {
            "status": "success",
            "ticker": ticker.upper(),
            "liquidity_ratios": {},
            "profitability_ratios": {},
            "leverage_ratios": {}
        }

        # Liquidity Ratios
        try:
            current_assets = float(balance.get('current_assets', 0))
            current_liabilities = float(balance.get('current_liabilities', 1))
            cash = float(balance.get('cash_and_equivalents', 0))

            if current_liabilities > 0:
                ratios["liquidity_ratios"]["current_ratio"] = round(
                    current_assets / current_liabilities, 2)
                ratios["liquidity_ratios"]["quick_ratio"] = round(
                    (current_assets - cash) / current_liabilities, 2)
                ratios["liquidity_ratios"]["cash_ratio"] = round(
                    cash / current_liabilities, 2)
        except:
            ratios["liquidity_ratios"]["note"] = "Insufficient data for calculation"

        # Profitability Ratios
        try:
            revenue = float(income.get('total_revenue', 1))
            net_income = float(income.get('net_income', 0))
            gross_profit = float(income.get('gross_profit', 0))
            operating_income = float(income.get('operating_income', 0))

            if revenue > 0:
                ratios["profitability_ratios"]["net_profit_margin"] = round(
                    (net_income / revenue) * 100, 2)
                ratios["profitability_ratios"]["gross_profit_margin"] = round(
                    (gross_profit / revenue) * 100, 2)
                ratios["profitability_ratios"]["operating_margin"] = round(
                    (operating_income / revenue) * 100, 2)
        except:
            ratios["profitability_ratios"]["note"] = "Insufficient data for calculation"

        # Leverage Ratios
        try:
            total_assets = float(balance.get('total_assets', 1))
            total_liabilities = float(balance.get('total_liabilities', 0))
            equity = float(balance.get('total_shareholder_equity', 1))
            long_term_debt = float(balance.get('long_term_debt', 0))

            if total_assets > 0:
                ratios["leverage_ratios"]["debt_to_assets"] = round(
                    total_liabilities / total_assets, 2)
            if equity > 0:
                ratios["leverage_ratios"]["debt_to_equity"] = round(
                    total_liabilities / equity, 2)
                ratios["leverage_ratios"]["equity_multiplier"] = round(
                    total_assets / equity, 2)
        except:
            ratios["leverage_ratios"]["note"] = "Insufficient data for calculation"

        return ratios

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error calculating financial ratios: {str(e)}"
        }


def analyze_growth_trends(ticker: str) -> Dict[str, Any]:
    """
    Analyze historical growth trends and provide forward-looking insights.
    Uses real financial data to identify growth patterns.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with growth analysis
    """
    try:
        fundamentals = get_stock_fundamentals(ticker)
        price = get_stock_price(ticker)

        if fundamentals.get('status') == 'error':
            return {
                "status": "error",
                "message": "Unable to analyze growth - fundamental data unavailable"
            }

        growth_analysis = {
            "status": "success",
            "ticker": ticker.upper(),
            "revenue_growth": fundamentals.get('revenue_growth', 'N/A'),
            "price_momentum": {
                "1_day_change": price.get('change_1day_percent', 'N/A'),
                "1_month_change": price.get('change_1month_percent', 'N/A')
            },
            "valuation_metrics": {
                "peg_ratio": fundamentals.get('peg_ratio', 'N/A'),
                "forward_pe": fundamentals.get('forward_pe', 'N/A')
            }
        }

        return growth_analysis

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing growth trends: {str(e)}"
        }


def investment_checklist_screen(ticker: str) -> Dict[str, Any]:
    """
    Gather comprehensive financial data for systematic stock evaluation.
    Collects: Business metrics, Financial health indicators, Valuation ratios, and Risk factors.

    This tool provides all the raw data needed for thorough investment analysis.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with comprehensive financial data organized by category
    """
    try:
        # Gather all necessary data
        fundamentals = get_stock_fundamentals(ticker)
        balance = get_balance_sheet(ticker)
        income = get_income_statement(ticker)
        cash_flow = get_cash_flow(ticker)
        ratios = calculate_financial_ratios(ticker)
        valuation = calculate_valuation_metrics(ticker)

        if fundamentals.get('status') == 'error':
            return {
                "status": "error",
                "message": "Unable to complete checklist - fundamental data unavailable"
            }

        # Compile all metrics without scoring or judgments
        checklist = {
            "status": "success",
            "ticker": ticker.upper(),
            "company_name": fundamentals.get('company_name', 'N/A'),
            "business_quality": {},
            "financial_health": {},
            "valuation_metrics": {},
            "risk_indicators": {}
        }

        # ========== BUSINESS QUALITY ==========
        net_margin = ratios.get('profitability_ratios', {}).get(
            'net_profit_margin', 'N/A')
        gross_margin = ratios.get('profitability_ratios', {}).get(
            'gross_profit_margin', 'N/A')
        operating_margin = ratios.get(
            'profitability_ratios', {}).get('operating_margin', 'N/A')

        checklist["business_quality"]["net_profit_margin"] = net_margin
        checklist["business_quality"]["gross_profit_margin"] = gross_margin
        checklist["business_quality"]["operating_margin"] = operating_margin

        market_cap = fundamentals.get('market_cap', 'N/A')
        checklist["business_quality"]["market_cap"] = market_cap

        checklist["business_quality"]["sector"] = fundamentals.get(
            'sector', 'N/A')
        checklist["business_quality"]["industry"] = fundamentals.get(
            'industry', 'N/A')

        # ========== FINANCIAL HEALTH ==========
        debt_to_equity = ratios.get(
            'leverage_ratios', {}).get('debt_to_equity', 'N/A')
        debt_to_assets = ratios.get(
            'leverage_ratios', {}).get('debt_to_assets', 'N/A')
        equity_multiplier = ratios.get(
            'leverage_ratios', {}).get('equity_multiplier', 'N/A')

        checklist["financial_health"]["debt_to_equity"] = debt_to_equity
        checklist["financial_health"]["debt_to_assets"] = debt_to_assets
        checklist["financial_health"]["equity_multiplier"] = equity_multiplier

        current_ratio = ratios.get(
            'liquidity_ratios', {}).get('current_ratio', 'N/A')
        quick_ratio = ratios.get(
            'liquidity_ratios', {}).get('quick_ratio', 'N/A')
        cash_ratio = ratios.get('liquidity_ratios', {}
                                ).get('cash_ratio', 'N/A')

        checklist["financial_health"]["current_ratio"] = current_ratio
        checklist["financial_health"]["quick_ratio"] = quick_ratio
        checklist["financial_health"]["cash_ratio"] = cash_ratio

        operating_cf = cash_flow.get('operating_cash_flow', 'N/A')
        free_cash_flow = cash_flow.get('free_cash_flow', 'N/A')
        capital_expenditures = cash_flow.get('capital_expenditures', 'N/A')

        checklist["financial_health"]["operating_cash_flow"] = operating_cf
        checklist["financial_health"]["free_cash_flow"] = free_cash_flow
        checklist["financial_health"]["capital_expenditures"] = capital_expenditures

        # ========== VALUATION ==========
        peg_ratio = fundamentals.get('peg_ratio', 'N/A')
        pe_ratio = fundamentals.get('pe_ratio', 'N/A')
        forward_pe = fundamentals.get('forward_pe', 'N/A')
        pb_ratio = fundamentals.get('price_to_book', 'N/A')

        checklist["valuation_metrics"]["peg_ratio"] = peg_ratio
        checklist["valuation_metrics"]["pe_ratio"] = pe_ratio
        checklist["valuation_metrics"]["forward_pe"] = forward_pe
        checklist["valuation_metrics"]["price_to_book"] = pb_ratio
        checklist["valuation_metrics"]["analyst_target"] = fundamentals.get(
            'analyst_target', 'N/A')
        checklist["valuation_metrics"]["52_week_high"] = fundamentals.get(
            '52_week_high', 'N/A')
        checklist["valuation_metrics"]["52_week_low"] = fundamentals.get(
            '52_week_low', 'N/A')

        # ========== RISK INDICATORS ==========
        beta = fundamentals.get('beta', 'N/A')
        checklist["risk_indicators"]["beta"] = beta

        div_yield = fundamentals.get('dividend_yield', 'N/A')
        checklist["risk_indicators"]["dividend_yield"] = div_yield

        revenue_growth = fundamentals.get('revenue_growth', 'N/A')
        checklist["risk_indicators"]["revenue_growth_yoy"] = revenue_growth

        eps = fundamentals.get('eps', 'N/A')
        checklist["risk_indicators"]["earnings_per_share"] = eps

        return checklist

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error running investment checklist: {str(e)}"
        }


# Create the root agent with investment research tools
# Note: Vertex AI Search tool requires vertex AI backend, not Gemini API
# Temporarily disable the search tool until we can configure Vertex AI properly

# Get current date/time for context
current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p %Z")
current_year = datetime.now().year

root_agent = Agent(
    model='gemini-3.1-pro-preview',
    name='investment_research_agent',
    instruction=f"""
CURRENT DATE & TIME: {current_datetime}
CURRENT YEAR: {current_year}

Role: You are a Fundamental Equity Analyst at a long-term focused hedge fund. Your objective is to rigorously evaluate investment targets by synthesizing quantitative data with qualitative judgment.

Research Protocol: As a rule of thumb for all company analysis, reference the following primary sources:
- Past 4 quarters' earnings transcripts
- Latest investor day transcript/presentation (if available)
- Latest 10-K filing
- Last 4 10-Qs (focus on Management's Discussion and Analysis section)

Instructions: Evaluate the target company using the following 4-Point Investment Checklist. Focus on the velocity of change and the sustainability of growth.

1. Business Quality & The Financial Algorithm
Combine the qualitative competitive advantage with the quantitative earnings engine.
Moat Trajectory (Widening vs. Shrinking): Is the competitive advantage getting stronger or weaker? Focus on the direction of the moat (e.g., strengthening brand, increasing switching costs) rather than just its static size.
Revenue Quality (The Retail Formula): Decompose top-line growth to determine quality. Prefer Volume/Traffic over Price.
Formula: Revenue Growth = Same Store Sales (Traffic + Ticket) + (New Store Growth × New Store Productivity).
Unit Economics & Operating Leverage:
Gross Margin: Is GM% expanding due to "merchandise margin" (true pricing power/mix) or contracting?
SG&A: Is the company growing Sales faster than SG&A (positive operating leverage)?.
The EPS Bridge: Define the long-term earnings algorithm.
Formula: Long-term EPS Growth = Revenue Growth + Margin Expansion + Buybacks/Debt Paydown.
2. Industry Attributes
Assess the "playing field" and external forces.
Market Structure: Is it a monopoly, oligopoly, or fragmented market?.
Growth Runway: Is this a zero-sum game or a growing pie? (Compare Industry Growth vs. GDP).
Barriers to Entry: High startup costs, regulatory hurdles, or network effects that protect returns.
Headwinds vs. Tailwinds: Identify macro factors (rates, inflation) and secular shifts (tech, regulation) aiding or hurting the sector.
3. Management Team & Culture
Evaluate the stewards of capital.
Culture as a Moat: Is the culture distinct and aligned with the competitive advantage? Is there a "maniacal" focus on the mission?.
Capital Allocation: Does management have a history of creating value via reinvestment, M&A, or buybacks? Do they "defy the fade" in returns on capital?
Execution: Does the team have a track record of "showing up" and executing through difficult cycles?.
4. Valuation & The Investment Thesis
Distinguish between a great company and a great stock.
How does the stock trades on valuation metrics like P/E, EV/EBITDA vs. historical averages (1/5/7 year) and peers?
Twin Engines of Return: Can the stock appreciate through both Earnings Compounding (The Algorithm) AND Multiple Re-rating?.
Expectations Mismatch: What is the market pricing in versus your view of the "Future Earnings Algorithm"?
Good Business vs. Good Investment: A good business becomes a good investment only when the future earnings power is under-appreciated by the current price.


CRITICAL DATA INTEGRITY & CITATION RULES:
1. NEVER make up data, numbers, or facts - ONLY use data returned from tools
2. ALWAYS cite the source of EVERY insight, methodology, or data point:
   - **For your research database**: MUST cite with format: "[Citation #X: Document Title]"
     Example: "According to our moat analysis framework [Citation #1: Competitive Advantage Deep Dive], we assess..."
   - For stock prices/financials: Cite "FMP API" with date
   - For web search: Cite specific source/URL from results
   - For earnings data: Cite "Q[X] [Year] Earnings Report"
3. PRIORITY: Your research database insights should be cited FIRST and MOST PROMINENTLY
4. If a tool returns an error or no data, explicitly state "Data not available" - do NOT fill in from general knowledge
5. When presenting numbers (revenue, margins, growth rates, etc.), ALWAYS include:
   - The exact figure from the tool
   - The source (e.g., "FMP Q4 2024 data")
   - The time period it covers
6. If you're unsure or data is incomplete, say "I don't have this data" rather than estimating

CITATION FORMAT EXAMPLE:
"Based on our proprietary research [Citation #2: Apple Long-Term Thesis 2024], the company's moat is widening due to ecosystem lock-in. Current financials show revenue of $394B (FMP FY2024 data), confirming the growth trajectory outlined in our thesis."

About Data Sources:
- This agent uses Financial Modeling Prep API for stock data (250 free calls/day)
- Tavily API for web search (1,000 free searches/month)
- Vertex AI Search for curated investment research documents
- If tools return errors (status: "error"), it may be due to invalid ticker symbols, API rate limits, or temporary data unavailability

When tools fail:
- Verify the ticker symbol is correct
- Check if the company is publicly traded
- Explicitly state what data is missing
- Do NOT provide made-up numbers or estimates

Remember: Always check the "status" field in tool responses before using the data. Never present data from a failed tool call.

ADVANCED TOOLS AVAILABLE:
- search_investment_research: **PRIMARY SOURCE** - Your proprietary research database containing investment philosophy, methodologies, frameworks, company analyses, and sector insights
- search_web: Secondary source for recent news, earnings announcements, and current events
- get_income_statement: Revenue, profit margins, earnings data
- get_balance_sheet: Assets, liabilities, debt levels
- get_cash_flow: Operating cash flow, free cash flow, capital expenditures
- calculate_valuation_metrics: Comprehensive valuation analysis with assessments

CRITICAL WORKFLOW - ALWAYS FOLLOW THIS ORDER:
1. **FIRST: Search your research database** → ALWAYS call search_investment_research for:
   - Investment philosophy and methodology questions
   - Company analysis (search: "company_name analysis" or "company_name moat")
   - Sector/industry insights (search: "sector_name trends" or "industry_name")
   - Valuation frameworks and approaches
   - Historical investment theses and track record

2. **SECOND: Get current financial data** → Use FMP API tools (get_stock_price, get_income_statement, etc.)

3. **THIRD: Search web for recent news** → Use search_web ONLY for very recent events (last few weeks)

4. **FOURTH: Synthesize** → Combine YOUR research (primary) + current data + recent news

5. **FIFTH: Cite sources** → ALWAYS cite which research documents informed your analysis (use citation numbers)

6. **ALWAYS critique** → Self-critique before presenting final conclusions

REMEMBER: Your research database IS your investment philosophy. Every analysis should be grounded in YOUR proprietary research first, then supplemented with current data.

SELF-CRITIQUE PROTOCOL:
After completing your initial analysis, you MUST critique your work by asking:
- **Did I search the research database?** (MOST IMPORTANT - if not, search now with relevant queries)
- What relevant research documents did I find and cite? (List citation numbers used)
- What data am I missing? (e.g., "I analyzed revenue growth but didn't check margin trends")
- What assumptions did I make? (e.g., "I assumed market share gains, but didn't verify")
- What contradicts my thesis? (e.g., "High P/E suggests market already prices in growth")
- What would change my mind? (e.g., "If next quarter's margins compress, thesis weakens")
- Does my analysis align with our historical research? (Cross-reference with research database)
- Did I cite sources for ALL insights and data points?

Then, based on your critique:
- If you didn't search research database → SEARCH NOW before proceeding
- Gather missing data if critical
- Acknowledge uncertainty explicitly
- Verify all research citations are included with [Citation #X: Title] format
- Revise or strengthen your analysis
- Present both the bull and bear case grounded in your research

MEMORY & CONTEXT:
- Reference previous analyses in this conversation
- Note if you've analyzed this stock before and if your view has changed
- Track which companies you've compared and build on those comparisons
- Remember user's investment priorities and preferences from earlier in the conversation
""",
    tools=[
        search_investment_research,  # Search your curated research first
        search_web,  # Search the web for news and current events
        investment_checklist_screen,
        get_stock_price,
        get_stock_fundamentals,
        compare_stocks,
        get_stock_info,
        get_income_statement,
        get_balance_sheet,
        get_cash_flow,
        calculate_valuation_metrics,
        generate_investment_report,
        calculate_financial_ratios,
        analyze_growth_trends,
    ],
)
