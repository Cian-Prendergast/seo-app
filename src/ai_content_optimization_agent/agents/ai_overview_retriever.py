import os
import requests
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
            if not ai_overview:
                ai_overview = self._generate_ai_overview_fallback(main_query, state.get("search_results", ""))
                ai_overview += "\n\n*Note: This AI Overview was generated as none was found in SERP results.*"
            self.log("AI Overview retrieved successfully")
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
        if not self.bright_data_api_key:
            raise ValueError("BRIGHT_DATA_API_KEY not configured")
        url = "https://api.brightdata.com/serp/v1/search"
        headers = {
            "Authorization": f"Bearer {self.bright_data_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "brd_ai_overview": 2,
            "gl": "us",
            "hl": "en"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        ai_overview = data.get("ai_overview", {}).get("text", "")
        return ai_overview
    def _generate_ai_overview_fallback(self, query: str, search_results: str) -> str:
        system_message = SystemMessage(content="""
        You are an AI assistant that generates AI Overviews based on search results.
        Create a comprehensive, well-structured overview that would typically appear 
        in Google's AI Overview section.
        """)
        human_message = HumanMessage(content=f"""
        Based on these search results for query "{query}", generate an AI Overview:
        {search_results[:3000]}
        Format as a clear, informative overview that answers the user's likely intent.
        """)
        messages = [system_message, human_message]
        return self.invoke_llm(messages)
def ai_overview_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = AIOverviewRetrieverAgent()
    return agent.execute(state)
