"""
Investment Research Agent using Google's Agent Development Kit (ADK)
This agent helps analyze stocks and assets for investment decisions.
Uses Alpha Vantage API for reliable stock data.
"""

import os
import tempfile
from typing import Dict, Any
from google.adk.agents.llm_agent import Agent
from google.cloud import discoveryengine_v1beta as discoveryengine
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Handle Google Cloud credentials for production (Render)
# If GOOGLE_APPLICATION_CREDENTIALS_JSON is set, write it to a temp file
credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
if credentials_json:
    try:
        # Create a temporary file to store credentials
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write(credentials_json)
            credentials_path = f.name
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        print(f"✓ Google Cloud credentials loaded from environment variable")
    except Exception as e:
        print(f"⚠ Warning: Could not process GCP credentials: {e}")

# Configure Vertex AI Search to connect to your data store
# Get configuration from environment variables
VERTEX_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
VERTEX_LOCATION = os.getenv('VERTEX_LOCATION', 'us')
VERTEX_DATA_STORE_ID = os.getenv('VERTEX_DATA_STORE_ID')

# Initialize Discovery Engine client for direct API access
vertex_search_available = False

if VERTEX_PROJECT_ID and VERTEX_DATA_STORE_ID:
    try:
        # Test connection by creating client with regional endpoint
        client_options = {
            "api_endpoint": f"{VERTEX_LOCATION}-discoveryengine.googleapis.com"}
        test_client = discoveryengine.SearchServiceClient(
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
        # Create client with regional endpoint for 'us' location
        client_options = {
            "api_endpoint": f"{VERTEX_LOCATION}-discoveryengine.googleapis.com"}
        client = discoveryengine.SearchServiceClient(
            client_options=client_options)

        # Build serving config path
        serving_config = client.serving_config_path(
            project=VERTEX_PROJECT_ID,
            location=VERTEX_LOCATION,
            data_store=VERTEX_DATA_STORE_ID,
            serving_config="default_search",
        )

        # Create search request
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=5,  # Get top 5 results
        )

        # Execute search
        response = client.search(request)

        # Parse results
        results = []
        for result in response.results:
            doc_data = result.document.derived_struct_data
            results.append({
                "title": doc_data.get('title', 'Untitled'),
                "snippet": doc_data.get('snippets', [{}])[0].get('snippet', '') if doc_data.get('snippets') else '',
                "link": doc_data.get('link', ''),
            })

        if not results:
            return {
                "status": "success",
                "query": query,
                "message": "No results found for this query.",
                "results": []
            }

        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "results": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error searching investment research: {str(e)}"
        }


def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Get current stock price and recent performance data using Alpha Vantage.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing current price, change, and performance metrics
    """
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        ts = TimeSeries(key=api_key, output_format='pandas')

        # Get daily data
        data, meta_data = ts.get_daily(symbol=ticker, outputsize='compact')

        if data.empty:
            return {
                "status": "error",
                "message": f"No price data found for {ticker}. Please verify the ticker symbol."
            }

        # Get latest and previous prices
        latest_close = float(data['4. close'].iloc[0])
        previous_close = float(data['4. close'].iloc[1])
        month_ago_close = float(data['4. close'].iloc[-1])

        change_1day = latest_close - previous_close
        change_1day_pct = (change_1day / previous_close) * 100

        change_1month = latest_close - month_ago_close
        change_1month_pct = (change_1month / month_ago_close) * 100

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "current_price": round(latest_close, 2),
            "change_1day": round(change_1day, 2),
            "change_1day_percent": round(change_1day_pct, 2),
            "change_1month": round(change_1month, 2),
            "change_1month_percent": round(change_1month_pct, 2),
            "high_recent": round(float(data['2. high'].max()), 2),
            "low_recent": round(float(data['3. low'].min()), 2),
            "average_volume": int(data['5. volume'].mean())
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching price data for {ticker}: {str(e)}. If using demo API key, note that it has limited tickers."
        }


def get_stock_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    Get fundamental financial metrics for a stock using Alpha Vantage.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing key financial metrics and company information
    """
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        fd = FundamentalData(key=api_key, output_format='pandas')

        # Get company overview
        data, meta_data = fd.get_company_overview(symbol=ticker)

        if data.empty:
            return {
                "status": "error",
                "message": f"No fundamental data found for {ticker}."
            }

        # Extract data (Alpha Vantage returns a single-row DataFrame)
        info = data.iloc[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "company_name": info.get('Name', 'N/A'),
            "sector": info.get('Sector', 'N/A'),
            "industry": info.get('Industry', 'N/A'),
            "market_cap": info.get('MarketCapitalization', 'N/A'),
            "pe_ratio": info.get('PERatio', 'N/A'),
            "forward_pe": info.get('ForwardPE', 'N/A'),
            "peg_ratio": info.get('PEGRatio', 'N/A'),
            "price_to_book": info.get('PriceToBookRatio', 'N/A'),
            "dividend_yield": info.get('DividendYield', 'N/A'),
            "beta": info.get('Beta', 'N/A'),
            "profit_margin": info.get('ProfitMargin', 'N/A'),
            "revenue_growth": info.get('QuarterlyRevenueGrowthYOY', 'N/A'),
            "eps": info.get('EPS', 'N/A'),
            "analyst_target": info.get('AnalystTargetPrice', 'N/A'),
            "52_week_high": info.get('52WeekHigh', 'N/A'),
            "52_week_low": info.get('52WeekLow', 'N/A')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching fundamentals for {ticker}: {str(e)}. If using demo API key, upgrade at alphavantage.co"
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
    Get the latest income statement data for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with income statement data including revenue, profit, etc.
    """
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        fd = FundamentalData(key=api_key, output_format='pandas')

        # Get annual income statement
        data, meta_data = fd.get_income_statement_annual(symbol=ticker)

        if data.empty:
            return {
                "status": "error",
                "message": f"No income statement data found for {ticker}."
            }

        # Get most recent year
        latest = data.iloc[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "fiscal_date": latest.get('fiscalDateEnding', 'N/A'),
            "total_revenue": latest.get('totalRevenue', 'N/A'),
            "gross_profit": latest.get('grossProfit', 'N/A'),
            "operating_income": latest.get('operatingIncome', 'N/A'),
            "net_income": latest.get('netIncome', 'N/A'),
            "ebitda": latest.get('ebitda', 'N/A'),
            "eps": latest.get('eps', 'N/A'),
            "research_development": latest.get('researchAndDevelopment', 'N/A')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching income statement for {ticker}: {str(e)}"
        }


def get_balance_sheet(ticker: str) -> Dict[str, Any]:
    """
    Get the latest balance sheet data for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with balance sheet data including assets, liabilities, equity
    """
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        fd = FundamentalData(key=api_key, output_format='pandas')

        # Get annual balance sheet
        data, meta_data = fd.get_balance_sheet_annual(symbol=ticker)

        if data.empty:
            return {
                "status": "error",
                "message": f"No balance sheet data found for {ticker}."
            }

        # Get most recent year
        latest = data.iloc[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "fiscal_date": latest.get('fiscalDateEnding', 'N/A'),
            "total_assets": latest.get('totalAssets', 'N/A'),
            "total_liabilities": latest.get('totalLiabilities', 'N/A'),
            "total_shareholder_equity": latest.get('totalShareholderEquity', 'N/A'),
            "current_assets": latest.get('totalCurrentAssets', 'N/A'),
            "current_liabilities": latest.get('totalCurrentLiabilities', 'N/A'),
            "cash_and_equivalents": latest.get('cashAndCashEquivalentsAtCarryingValue', 'N/A'),
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
    Get the latest cash flow statement data for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with cash flow data
    """
    try:
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        fd = FundamentalData(key=api_key, output_format='pandas')

        # Get annual cash flow
        data, meta_data = fd.get_cash_flow_annual(symbol=ticker)

        if data.empty:
            return {
                "status": "error",
                "message": f"No cash flow data found for {ticker}."
            }

        # Get most recent year
        latest = data.iloc[0]

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "fiscal_date": latest.get('fiscalDateEnding', 'N/A'),
            "operating_cash_flow": latest.get('operatingCashflow', 'N/A'),
            "capital_expenditures": latest.get('capitalExpenditures', 'N/A'),
            # Can calculate: OCF - CapEx
            "free_cash_flow": latest.get('operatingCashflow', 'N/A'),
            "dividends_paid": latest.get('dividendPayout', 'N/A'),
            "change_in_cash": latest.get('changeInCashAndCashEquivalents', 'N/A')
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
root_agent = Agent(
    model='gemini-3-flash-preview',  # Use stable Gemini 1.5 model
    name='investment_research_agent',
    instruction="""
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


IMPORTANT - About the Data Source:
- This agent uses Alpha Vantage API for stock data
- For full access to all tickers, users need a free API key from alphavantage.co
- If tools return errors (status: "error"), acknowledge this and suggest getting a free API key
- Still provide general investment insights when data isn't available
- Use reputable data source for financials like sales / same store sales / margins / cash flow / etc. Sources I like include earnings releases / transcripts / 10-Ks / 10-Qs etc.

When tools fail:
- Explain the limitation (demo key or API issue)
- Suggest getting a free API key from alphavantage.co
- Provide general analysis based on your knowledge

Remember: Always check the "status" field in tool responses before using the data.

ADVANCED TOOLS AVAILABLE:
- search_investment_research: Search curated investment research, frameworks, and methodologies from your data store
- get_income_statement: Revenue, profit margins, earnings data
- get_balance_sheet: Assets, liabilities, debt levels
- get_cash_flow: Operating cash flow, free cash flow, capital expenditures
- calculate_valuation_metrics: Comprehensive valuation analysis with assessments

WORKFLOW:
1. For methodology/framework questions → Use search_investment_research first to query your research library
2. For stock data → Use financial data tools
3. Combine insights from both sources for comprehensive analysis
""",
    tools=[
        search_investment_research,  # Search your curated research first
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
