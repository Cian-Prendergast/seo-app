from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
from utils.prompt_loader import load_prompt, format_prompt  # ✅ ADD THIS LINE

class QueryFanoutSummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("summarizer")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Summarizing query fanout")
        
        search_results = state.get("search_results", "")
        if not search_results:
            return {
                **state,
                "errors": state.get("errors", []) + ["No search results to summarize"],
                "current_step": "summarization_failed"
            }
        
        try:
            # ✅ REPLACE the hardcoded prompts with these 2 lines:
            system_prompt = load_prompt("summarizer_system")
            human_prompt = format_prompt("summarizer_human", search_results=search_results)
            
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=human_prompt)
            
            messages = [system_message, human_message]
            
            summary = self.invoke_llm(messages)
            
            self.log("Summary generated successfully")
            
            output_files = state.get("output_files", {})
            output_files["query_fanout_summary.md"] = summary
            
            return {
                **state,
                "query_fanout_summary": summary,
                "output_files": output_files,
                "current_step": "summarization_completed"
            }
            
        except Exception as e:
            error_msg = f"Summarization failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "summarization_failed"
            }

def summarizer_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = QueryFanoutSummarizerAgent()
    return agent.execute(state)