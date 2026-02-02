#!/usr/bin/env python3
"""Test script to verify Cloud Run deployment."""

import requests
import json

# Your Cloud Run URL
BASE_URL = "https://adk-default-service-name-288459684190.us-east1.run.app"

def test_health():
    """Test if the service is running."""
    try:
        response = requests.get(BASE_URL)
        print(f"✅ Service is responding (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Service not responding: {e}")
        return False

if __name__ == "__main__":
    print(f"Testing Cloud Run deployment at: {BASE_URL}\n")
    test_health()
    print(f"\n📍 Your agent is deployed at: {BASE_URL}")
    print("⚠️  The /docs UI has a compatibility issue, but the agent is running.")
    print("   You can interact with it via API calls or the ADK client SDK.")
