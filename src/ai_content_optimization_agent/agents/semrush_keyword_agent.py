from base_agent import BaseAgent
from state import ContentOptimizationState
from utils.semrush_client import SEMrushClient

class SEMrushKeywordAgent(BaseAgent):
    def __init__(self):
        super().__init__("semrush_keyword")
        self.semrush = SEMrushClient()
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Fetching SEMrush keyword data")
        
        # Skip if API not configured
        if not self.semrush.is_available():
            self.log("SEMrush API not configured - skipping")
            return {
                **state,
                "keyword_data": {"status": "skipped", "reason": "API not configured"},
                "current_step": "semrush_skipped"
            }
        
        main_query = state.get("main_query")
        focus_keyword = state.get("focus_keyword")
        keyword = focus_keyword or main_query
        
        if not keyword:
            return {
                **state,
                "keyword_data": {"status": "skipped", "reason": "No keyword available"},
                "current_step": "semrush_skipped"
            }
        
        try:
            # Get keyword metrics
            keyword_data = self.semrush.get_keyword_data(keyword)
            
            if keyword_data:
                self.log(f"Retrieved SEMrush data for '{keyword}'")
                print(f"📊 SEMrush Data:")
                print(f"   🔍 Keyword: {keyword_data['keyword']}")
                print(f"   📈 Search Volume: {keyword_data.get('search_volume', 'N/A')}")
                print(f"   💰 CPC: ${keyword_data.get('cpc', 0):.2f}")
                print(f"   🎯 Difficulty: {keyword_data.get('keyword_difficulty', 'N/A')}")
                print()
            else:
                keyword_data = {"status": "no_data", "keyword": keyword}
            
            return {
                **state,
                "keyword_data": keyword_data,
                "current_step": "semrush_completed"
            }
            
        except Exception as e:
            error_msg = f"SEMrush lookup failed: {str(e)}"
            self.log(error_msg, "warning")
            return {
                **state,
                "keyword_data": {"status": "error", "error": str(e)},
                "current_step": "semrush_failed"
            }

def semrush_keyword_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = SEMrushKeywordAgent()
    return agent.execute(state)