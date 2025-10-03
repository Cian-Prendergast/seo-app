import os
import requests
import json
import urllib.parse
from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState

class AIOverviewRetrieverAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai_overview_retriever")
        self.bright_data_api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.bright_data_zone = os.getenv("BRIGHT_DATA_ZONE")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Retrieving AI Overview")
        main_query = state.get("main_query", "")
        if not main_query:
            return {
                **state,
                "errors": state.get("errors", []) + ["No main query available"],
                "current_step": "ai_overview_failed"
            }
        
        try:
            ai_overview = self._search_serp_api(main_query)
            
            if ai_overview:
                self.log("AI Overview retrieved successfully from SERP API")
            else:
                error_msg = "No AI overview found in SERP results (this might be normal - not all searches have AI overviews)"
                self.log(error_msg, "info")
                return {
                    **state,
                    "errors": state.get("errors", []) + [error_msg],
                    "current_step": "ai_overview_failed"
                }
            
            # Save to output files
            output_files = state.get("output_files", {})
            output_files["ai_overview.md"] = ai_overview
            
            return {
                **state,
                "ai_overview": ai_overview,
                "output_files": output_files,
                "current_step": "ai_overview_retrieved"
            }
            
        except Exception as e:
            error_msg = f"AI Overview retrieval failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "ai_overview_failed"
            }
    
    def _search_serp_api(self, query: str) -> str:
        """Get AI overview from Bright Data SERP API with detailed debugging"""
        if not self.bright_data_api_key or not self.bright_data_zone:
            raise ValueError("BRIGHT_DATA_API_KEY and BRIGHT_DATA_ZONE not configured")
        
        # Debug: Log configuration (first 10 chars of API key for security)
        self.log(f"API Key (first 10 chars): {self.bright_data_api_key[:10]}...")
        self.log(f"Zone: {self.bright_data_zone}")
        self.log(f"Query: {query}")
        
        # Correct Bright Data endpoint
        url = "https://api.brightdata.com/request"
        headers = {
            "Authorization": f"Bearer {self.bright_data_api_key}",
            "Content-Type": "application/json"
        }
        
        # URL encode the query properly
        encoded_query = urllib.parse.quote(query)
        # Use simpler URL format for SERP API
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        # Debug: Log request details
        self.log(f"Search URL: {search_url}")
        
        # Correct payload format for structured JSON data
        payload = {
            "zone": self.bright_data_zone,
            "url": search_url,
            "format": "json"  # Changed from "raw" to "json" to get structured data
        }
        
        # Debug: Log the exact request
        print(f"[DEBUG AI_OVERVIEW] Request URL: {url}")
        print(f"[DEBUG AI_OVERVIEW] Request Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'})}")
        print(f"[DEBUG AI_OVERVIEW] Request Payload: {json.dumps(payload)}")
        print(f"[DEBUG AI_OVERVIEW] Authorization header present: {'Authorization' in headers}")
        
        try:
            print("[DEBUG AI_OVERVIEW] Sending request to Bright Data API...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Debug: Log response details
            self.log(f"Response Status Code: {response.status_code}")
            self.log(f"Response Headers: {dict(response.headers)}")
            
            # If it's an error, log the response body
            if response.status_code != 200:
                self.log(f"Response Body: {response.text}")
                response.raise_for_status()
            
            # Check if response has content before parsing
            response_text = response.text.strip()
            print(f"[DEBUG AI_OVERVIEW] Response status: {response.status_code}")
            print(f"[DEBUG AI_OVERVIEW] Response headers: {dict(response.headers)}")
            print(f"[DEBUG AI_OVERVIEW] Response content length: {len(response_text)}")
            print(f"[DEBUG AI_OVERVIEW] Response content (first 500 chars): {response_text[:500]}")
            
            if not response_text:
                raise Exception("Empty response received from Bright Data API")
            
            # Parse response
            try:
                data = response.json()
                print(f"[DEBUG AI_OVERVIEW] JSON parsed successfully. Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            except json.JSONDecodeError as e:
                print(f"[DEBUG AI_OVERVIEW] Failed to parse JSON response. Full response text: {response_text}")
                raise Exception(f"Invalid JSON response: {str(e)}")
            
            # Debug: Log response structure (first 500 chars)
            response_preview = json.dumps(data, indent=2)[:500]
            self.log(f"Response Preview: {response_preview}...")
            
            # Extract AI overview from response
            ai_overview = self._extract_ai_overview(data, query)
            
            if ai_overview:
                self.log(f"AI Overview found (length: {len(ai_overview)} chars)")
            else:
                self.log("No AI overview found in response - checking available keys")
                self.log(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            return ai_overview
            
        except requests.exceptions.HTTPError as e:
            # Enhanced error logging
            error_details = f"HTTP {e.response.status_code}: {e.response.reason}"
            if e.response.text:
                error_details += f"\nResponse body: {e.response.text[:500]}"
            # Check for common authentication issues
            if e.response.status_code == 401:
                error_details += "\nThis appears to be an authentication error. Please check your BRIGHT_DATA_API_KEY."
            elif e.response.status_code == 403:
                error_details += "\nThis appears to be an authorization error. Please check your zone permissions and API key."
            raise Exception(error_details)
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _extract_ai_overview(self, data: dict, query: str) -> str:
        """Extract AI overview from response with detailed logging"""
        
        # Try different possible locations for AI overview
        if "ai_overview" in data:
            self.log("Found 'ai_overview' key in response")
            if isinstance(data["ai_overview"], dict):
                return data["ai_overview"].get("text", "")
            else:
                return str(data["ai_overview"])
                
        elif "answer_box" in data:
            self.log("Found 'answer_box' key in response")
            return data.get("answer_box", {}).get("snippet", "")
            
        elif "organic_results" in data:
            self.log("Found 'organic_results' key - synthesizing overview")
            results = data.get("organic_results", [])[:3]
            if results:
                return self._synthesize_ai_overview(query, results)
                
        elif "results" in data:
            self.log("Found 'results' key - synthesizing overview")
            results = data.get("results", [])[:3]
            if results:
                return self._synthesize_ai_overview(query, results)
        
        # If we have any data, try to create something useful
        elif data:
            self.log(f"No standard AI overview found. Available keys: {list(data.keys())}")
            return f"# Search Results for '{query}'\n\nRaw data available but no AI overview found.\n\n*Response keys: {list(data.keys())}*"
        
        return ""
    
    def _synthesize_ai_overview(self, query: str, results: list) -> str:
        """Create an AI overview-style summary from SERP results"""
        overview = f"# Synthesized Overview for '{query}'\n\n"
        
        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "")
            snippet = result.get("snippet", "") or result.get("description", "")
            if title and snippet:
                overview += f"**{i}. {title}**\n{snippet}\n\n"
        
        overview += "*Generated from top search results (no native AI overview found).*"
        return overview

def ai_overview_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = AIOverviewRetrieverAgent()
    return agent.execute(state)