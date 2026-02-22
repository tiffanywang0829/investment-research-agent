#!/usr/bin/env python3
"""Test script to verify Vertex AI Search is working with stored investment philosophy."""

from investment_agent.agent import search_investment_research
import json

print("=" * 80)
print("Testing Vertex AI Search Integration")
print("=" * 80)
print()

# Test 1: Search for 4-point checklist
print("Test 1: Searching for '4-point investment checklist'...")
result = search_investment_research("4-point investment checklist")
print(json.dumps(result, indent=2))
print()

# Test 2: Search for velocity of change
print("Test 2: Searching for 'velocity of change'...")
result = search_investment_research("velocity of change")
print(json.dumps(result, indent=2))
print()

# Test 3: Search for sustainability criteria
print("Test 3: Searching for 'sustainability criteria'...")
result = search_investment_research("sustainability criteria")
print(json.dumps(result, indent=2))
print()

# Test 4: Search for earnings transcript analysis
print("Test 4: Searching for 'earnings transcript analysis'...")
result = search_investment_research("earnings transcript analysis")
print(json.dumps(result, indent=2))
print()

print("=" * 80)
print("If you see results with titles, snippets, and links, Vertex AI Search is working!")
print("=" * 80)
