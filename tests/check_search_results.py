"""
Test script to check if Vertex AI Search is returning results
Run this after your documents are indexed to verify the integration works
"""
import sys
import os

# Add parent directory to path so we can import investment_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from investment_agent.agent import search_investment_research


def test_search(query):
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print('='*70)

    result = search_investment_research(query)

    print(f"Status: {result.get('status')}")

    if result.get('status') == 'error':
        print(f"❌ Error: {result.get('message')}")
        return False

    results_count = result.get('results_count', 0)
    print(f"Results found: {results_count}")

    if results_count > 0:
        print(f"\n✅ SUCCESS - Found {results_count} results!\n")
        for i, res in enumerate(result.get('results', []), 1):
            print(f"{i}. Title: {res.get('title')}")
            snippet = res.get('snippet', '')
            if snippet:
                # Show first 200 characters of snippet
                print(
                    f"   Snippet: {snippet[:200]}{'...' if len(snippet) > 200 else ''}")
            if res.get('link'):
                print(f"   Link: {res.get('link')}")
            print()
        return True
    else:
        print("\n⚠️  No results found")
        print("   This means either:")
        print("   - Documents are still being indexed (wait 5-30 minutes)")
        print("   - Data store is empty (upload documents in GCP console)")
        print("   - Query doesn't match indexed content (try different keywords)")
        return False


# Run multiple test queries
print("\nTesting Vertex AI Search Integration")
print("="*70)

test_queries = [
    "investment framework",
    "valuation",
    "moat",
    "retail",
    "Philippe Laffont"
]

print("\nRunning test queries...")
results_found = False

for query in test_queries:
    if test_search(query):
        results_found = True

print("\n" + "="*70)
if results_found:
    print("✅ VERTEX AI SEARCH IS WORKING!")
    print("   Your agent can now search your investment research!")
else:
    print("⚠️  NO RESULTS YET")
    print("   Check document indexing status in GCP Console:")
    print("   https://console.cloud.google.com/gen-app-builder/data-stores")
print("="*70)
