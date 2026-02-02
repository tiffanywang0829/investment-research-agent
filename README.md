# Investment Research Agent

An AI-powered investment research agent built with Google Agent Development Kit (ADK) that analyzes stocks using real-time market data and a custom investment framework.

## Features

- **4-Point Investment Checklist Framework** - Analyzes companies based on velocity of change and sustainability
- **Real-time Stock Data** - Integrates with Alpha Vantage API for current market data
- **Investment Research Context** - Uses Vertex AI Search to query research frameworks and analysis from cloud storage
- **Comprehensive Financial Analysis** - Evaluates valuation metrics, growth trends, and investment criteria

## Tools Available

The agent has access to 13 specialized tools:
1. Financial data retrieval (stock prices, company overviews, income statements, balance sheets, cash flow)
2. Financial calculations (valuation metrics, growth trends, investment screening)
3. Investment research search (Vertex AI Search integration)

## Quick Start - Local Development

### Prerequisites
- Python 3.10+
- Google Cloud account with Vertex AI Search configured
- Alpha Vantage API key
- Google AI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tiffanywang0829/investment-research-agent.git
   cd investment-research-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   GCP_PROJECT_ID=your_gcp_project_id
   VERTEX_LOCATION=us
   VERTEX_DATA_STORE_ID=your_data_store_id
   ```

5. **Run the agent locally**
   ```bash
   adk web investment_agent
   ```

   Access the UI at http://localhost:8080

## Running Evaluations

Test the agent with evaluation sets:

```bash
# Start the ADK web UI
adk web

# Navigate to http://localhost:8080
# Go to Evaluations tab
# Run Eval1 evaluation set
```

Evaluation results are saved in `investment_agent/.adk/eval_history/`

## Deployment

See [README_RENDER.md](README_RENDER.md) for deployment instructions to Render.com.

## Project Structure

```
investment-research-agent/
├── investment_agent/
│   ├── agent.py              # Main agent code with tools and logic
│   ├── __init__.py           # Package initialization
│   └── Eval1.evalset.json    # Evaluation test cases
├── tests/
│   ├── check_search_results.py
│   ├── test_search.py
│   └── test_search_debug.py
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
└── README.md                 # This file
```

## Agent Architecture

The agent uses:
- **Model**: Gemini 2.0 Flash (experimental)
- **Backend**: Google Generative AI
- **Memory**: Conversation history tracking
- **Tools**: 13 specialized financial and research tools

## Environment Variables

Required:
- `GOOGLE_API_KEY` - Google AI API key for Gemini models
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API for stock data
- `GCP_PROJECT_ID` - Google Cloud project ID
- `VERTEX_LOCATION` - Vertex AI region (e.g., "us")
- `VERTEX_DATA_STORE_ID` - Vertex AI Search data store ID

## License

Private research project
