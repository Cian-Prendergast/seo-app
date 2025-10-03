#!/usr/bin/env python3
"""
Test script to verify Bright Data API connectivity
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_bright_data_api():
    api_key = os.getenv("BRIGHT_DATA_API_KEY")
    zone = os.getenv("BRIGHT_DATA_ZONE")
    
    print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}...")
    print(f"Zone: {zone}")
    
    if not api_key or not zone:
        print("❌ Missing BRIGHT_DATA_API_KEY or BRIGHT_DATA_ZONE")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "zone": zone,
        "url": "https://www.google.com/search?q=pizza",
        "format": "json"  # Changed from "raw" to "json"
    }
    
    print(f"\n🔄 Testing Bright Data API...")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Length: {len(response.text)}")
        print(f"Response Content (first 500 chars):")
        print("-" * 50)
        print(response.text[:500])
        print("-" * 50)
        
        if response.status_code == 200:
            print("✅ API request successful!")
            
            # Try to parse as JSON
            try:
                json_data = response.json()
                print(f"✅ JSON parsing successful!")
                print(f"Top-level keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print("This might be normal if the response is HTML content")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_bright_data_api()