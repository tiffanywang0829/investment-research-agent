#!/usr/bin/env python3
"""Startup script for Render deployment."""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from investment_agent.agent import root_agent

if __name__ == "__main__":
    import uvicorn
    from google.adk.cli.fast_api import create_app

    # Get port from environment (Render provides this)
    port = int(os.environ.get("PORT", 8080))

    # Create FastAPI app with the agent
    app = create_app(root_agent)

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)
