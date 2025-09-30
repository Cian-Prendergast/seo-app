from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
from utils.prompt_loader import load_prompt, format_prompt

class QueryResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("query_researcher")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting query research")
        
        title = state.get("title", "")
        if not title:
            return {
                **state,
                "errors": state.get("errors", []) + ["No title available for research"],
                "current_step": "research_failed"
            }
        
        try:
            # Load prompts from files
            system_prompt = load_prompt("query_researcher_system")
            human_prompt = format_prompt("query_researcher_human", title=title)
            
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=human_prompt)
            
            messages = [system_message, human_message]
            tools = [{"google_search": {}}]
            
            search_results = self.invoke_llm(messages, tools=tools)
            
            self.log("Research completed successfully")
            
            output_files = state.get("output_files", {})
            output_files["query_fanout.md"] = search_results
            
            return {
                **state,
                "search_results": search_results,
                "output_files": output_files,
                "current_step": "research_completed"
            }
            
        except Exception as e:
            error_msg = f"Research failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "research_failed"
            }

def query_researcher_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = QueryResearcherAgent()
    return agent.execute(state)