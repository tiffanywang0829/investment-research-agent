# Test Scripts

This folder contains test scripts to verify your Vertex AI Search integration.

## Quick Test (Recommended)

**`check_search_results.py`** - Run this to verify if search is working
```bash
# From the project root directory:
source venv/bin/activate
python tests/check_search_results.py
```

This script:
- Tests multiple search queries
- Shows clear ✅ or ⚠️ status
- Displays result snippets when documents are indexed
- Tells you what to do if no results are found

## Other Test Scripts

**`test_search.py`** - Simple single-query test
- Tests one query: "What is the investing framework?"
- Shows basic result structure

**`test_search_debug.py`** - Debug/development script
- Shows raw API response structure
- Useful for troubleshooting API issues
- Displays internal response format

## Expected Output (When Working)

```
✅ SUCCESS - Found 3 results!

1. Title: Investment Analysis Framework
   Snippet: The 4-point investment checklist...
```

## Expected Output (While Indexing)

```
⚠️  NO RESULTS YET
   Check document indexing status in GCP Console
```
