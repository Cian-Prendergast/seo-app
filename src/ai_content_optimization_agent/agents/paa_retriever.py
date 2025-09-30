import os
import requests
import json
import urllib.parse
from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState

class PAARetrieverAgent(BaseAgent):
    def __init__(self):
        super().__init__("paa_retriever")
        self.bright_data_api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.bright_data_zone = os.getenv("BRIGHT_DATA_ZONE")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Retrieving People Also Ask (PAA)")
        main_query = state.get("main_query", "")
        
        if not main_query:
            return {
                **state,
                "errors": state.get("errors", []) + ["No main query for PAA"],
                "current_step": "paa_failed"
            }
        
        try:
            paa_data = self._search_paa_api(main_query)
            
            if paa_data:
                self.log(f"PAA retrieved successfully - found {len(paa_data.split('##')) - 1} questions")
            else:
                self.log("No PAA data found", "info")
                paa_data = "No People Also Ask questions found for this query."
            
            # Save to output files
            output_files = state.get("output_files", {})
            output_files["paa_data.md"] = paa_data
            
            return {
                **state,
                "paa_data": paa_data,
                "output_files": output_files,
                "current_step": "paa_retrieved"
            }
            
        except Exception as e:
            error_msg = f"PAA retrieval failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "paa_data": "PAA retrieval failed",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "paa_failed"
            }
    
    def _search_paa_api(self, query: str) -> str:
        """Get PAA from Bright Data SERP API"""
        if not self.bright_data_api_key or not self.bright_data_zone:
            raise ValueError("BRIGHT_DATA_API_KEY and BRIGHT_DATA_ZONE not configured")
        
        self.log(f"Searching PAA for query: {query}")
        
        url = "https://api.brightdata.com/request"
        headers = {
            "Authorization": f"Bearer {self.bright_data_api_key}",
            "Content-Type": "application/json"
        }
        
        encoded_query = urllib.parse.quote(query)
        # Add brd_json=1 to get structured data with PAA
        search_url = f"https://www.google.com/search?q={encoded_query}&hl=en&gl=us&brd_json=1"
        
        payload = {
            "zone": self.bright_data_zone,
            "url": search_url,
            "format": "raw"
        }
        
        self.log(f"Request URL: {search_url}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return self._extract_paa(data, query)
            
        except requests.exceptions.HTTPError as e:
            self.log(f"HTTP Error: {e.response.status_code}", "error")
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text[:500]}")
        except Exception as e:
            raise Exception(f"PAA request failed: {str(e)}")
    
    def _extract_paa(self, data: dict, query: str) -> str:
        """Extract People Also Ask from SERP response"""
        
        # Look for PAA in different possible locations
        paa_questions = []
        
        # Check for 'related_questions' or 'people_also_ask'
        if "related_questions" in data:
            paa_questions = data["related_questions"]
            self.log(f"Found {len(paa_questions)} related questions")
        elif "people_also_ask" in data:
            paa_questions = data["people_also_ask"]
            self.log(f"Found {len(paa_questions)} PAA questions")
        else:
            self.log(f"No PAA found. Available keys: {list(data.keys())}")
            return ""
        
        # Format PAA as Markdown
        if not paa_questions:
            return ""
        
        markdown = f"# People Also Ask: {query}\n\n"
        
        for i, item in enumerate(paa_questions, 1):
            if isinstance(item, dict):
                question = item.get("question", "")
                answer = item.get("answer", "") or item.get("snippet", "")
                source = item.get("source", "") or item.get("link", "")
                
                markdown += f"## {i}. {question}\n\n"
                if answer:
                    markdown += f"{answer}\n\n"
                if source:
                    markdown += f"*Source: {source}*\n\n"
            else:
                markdown += f"## {i}. {item}\n\n"
        
        return markdown

def paa_retriever_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = PAARetrieverAgent()
    return agent.execute(state)