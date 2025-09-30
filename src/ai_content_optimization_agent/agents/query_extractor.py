from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
from utils.prompt_loader import load_prompt, format_prompt  # ✅ ADD THIS LINE

class MainQueryExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__("query_extractor")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Extracting main query")
        
        search_results = state.get("search_results", "")
        if not search_results:
            return {
                **state,
                "errors": state.get("errors", []) + ["No search results available"],
                "current_step": "query_extraction_failed"
            }
        
        try:
            # ✅ REPLACE the hardcoded prompts with these 2 lines:
            system_prompt = load_prompt("query_extractor_system")
            human_prompt = format_prompt("query_extractor_human", search_results=search_results)
            
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=human_prompt)
            
            messages = [system_message, human_message]
            
            main_query = self.invoke_llm(messages)
            
            self.log(f"Extracted main query: {main_query}")
            
            return {
                **state,
                "main_query": main_query.strip(),
                "current_step": "query_extracted"
            }
            
        except Exception as e:
            error_msg = f"Query extraction failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "query_extraction_failed"
            }

def query_extractor_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = MainQueryExtractorAgent()
    return agent.execute(state)