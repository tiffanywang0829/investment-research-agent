"""
Quick test script to verify Vertex AI Search integration
"""
import sys
import os

# Add parent directory to path so we can import investment_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from investment_agent.agent import search_investment_research

# Test search functionality
print("Testing Vertex AI Search integration...")
print("=" * 60)

result = search_investment_research("What is the investing framework?")

print(f"Status: {result.get('status')}")
print(f"Query: {result.get('query', 'N/A')}")

if result.get('status') == 'success':
    print(f"Results found: {result.get('results_count', 0)}")
    print("\nTop results:")
    for i, res in enumerate(result.get('results', []), 1):
        print(f"\n{i}. {res.get('title')}")
        print(f"   Snippet: {res.get('snippet')[:150]}...")
        if res.get('link'):
            print(f"   Link: {res.get('link')}")
else:
    print(f"Error: {result.get('message')}")
