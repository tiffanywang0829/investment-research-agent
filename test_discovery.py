#!/usr/bin/env python3
"""Test script to verify ADK can discover the agent."""
import os
import sys

print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")
print()

# Test 1: Check if investment_agent folder exists
agent_dir = "investment_agent"
if os.path.exists(agent_dir):
    print(f"✅ Found {agent_dir}/ directory")
    files = os.listdir(agent_dir)
    print(f"   Files: {files}")
else:
    print(f"❌ {agent_dir}/ directory not found")

print()

# Test 2: Try importing the agent
try:
    from investment_agent import root_agent
    print(f"✅ Successfully imported root_agent")
    print(f"   Agent name: {root_agent.name}")
except Exception as e:
    print(f"❌ Failed to import root_agent: {e}")

print()

# Test 3: Check environment variables
required_vars = ["GOOGLE_API_KEY", "ALPHA_VANTAGE_API_KEY", "GCP_PROJECT_ID"]
print("Environment variables:")
for var in required_vars:
    value = os.environ.get(var)
    if value:
        print(f"  ✅ {var}: {value[:10]}...")
    else:
        print(f"  ❌ {var}: NOT SET")
