"""
Debug script to see raw response structure from Vertex AI Search
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import discoveryengine_v1beta as discoveryengine
from dotenv import load_dotenv

load_dotenv()

# Configuration
project_id = os.getenv('GCP_PROJECT_ID')
location = os.getenv('VERTEX_LOCATION', 'us')
data_store_id = os.getenv('VERTEX_DATA_STORE_ID')

print(f"Testing search for data store: {data_store_id}")
print("=" * 60)

# Create client
client_options = {"api_endpoint": f"{location}-discoveryengine.googleapis.com"}
client = discoveryengine.SearchServiceClient(client_options=client_options)

# Build serving config path
serving_config = client.serving_config_path(
    project=project_id,
    location=location,
    data_store=data_store_id,
    serving_config="default_search",
)

print(f"Serving config: {serving_config}\n")

# Create search request
request = discoveryengine.SearchRequest(
    serving_config=serving_config,
    query="investment framework",
    page_size=3,
)

# Execute search
response = client.search(request)

print(f"Response type: {type(response)}")
print(f"Has results: {hasattr(response, 'results')}")

if hasattr(response, 'results'):
    results_list = list(response.results)
    print(f"Number of results: {len(results_list)}")

    if results_list:
        print("\nFirst result structure:")
        first_result = results_list[0]
        print(f"Result type: {type(first_result)}")
        print(f"Has document: {hasattr(first_result, 'document')}")

        if hasattr(first_result, 'document'):
            doc = first_result.document
            print(f"Document type: {type(doc)}")
            print(f"Document fields: {dir(doc)}")

            if hasattr(doc, 'derived_struct_data'):
                print(f"\nDerived struct data: {doc.derived_struct_data}")
    else:
        print("\n⚠ No results returned - data store may be empty or still indexing")
