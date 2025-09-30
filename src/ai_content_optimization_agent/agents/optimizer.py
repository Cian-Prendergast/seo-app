from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
from utils.prompt_loader import load_prompt, format_prompt  # ✅ ADD THIS LINE

class ContentOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("content_optimizer")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting content optimization analysis")
        
        summary = state.get("query_fanout_summary", "")
        ai_overview = state.get("ai_overview", "")
        title = state.get("title", "")
        main_query = state.get("main_query", "")
        
        # We need at least the summary to do analysis
        if not summary:
            return {
                **state,
                "errors": state.get("errors", []) + ["Missing query fanout summary for analysis"],
                "current_step": "optimization_failed"
            }
        
        try:
            if ai_overview:
                # We have some form of AI overview (native or synthesized)
                comparison_report = self._generate_comparison_analysis(summary, ai_overview, title, main_query)
            else:
                # No AI overview at all, analyze just the summary
                comparison_report = self._generate_summary_only_analysis(summary, title, main_query)
            
            self.log("Optimization analysis completed")
            
            # Save to output files
            output_files = state.get("output_files", {})
            output_files["report.md"] = comparison_report
            
            return {
                **state,
                "comparison_report": comparison_report,
                "output_files": output_files,
                "current_step": "optimization_completed"
            }
            
        except Exception as e:
            error_msg = f"Content optimization failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "optimization_failed"
            }
    
    def _generate_comparison_analysis(self, summary: str, ai_overview: str, title: str, main_query: str) -> str:
        """Generate analysis when we have both summary and some form of AI overview"""
        
        # Check if this is a synthesized overview
        is_synthesized = "Generated from top search results" in ai_overview or "Synthesized Overview" in ai_overview
        overview_type = "Synthesized AI Overview" if is_synthesized else "AI Overview"
        
        # ✅ REPLACE the hardcoded prompts with these lines:
        system_prompt = load_prompt("optimizer_system")
        
        synthesized_note = "Note: The AI overview was synthesized from search results since no native Google AI overview was available for this query." if is_synthesized else ""
        
        human_prompt = format_prompt(
            "optimizer_comparison_human",
            title=title,
            main_query=main_query,
            summary=summary,
            overview_type=overview_type,
            ai_overview=ai_overview,
            synthesized_note=synthesized_note
        )
        
        system_message = SystemMessage(content=system_prompt)
        human_message = HumanMessage(content=human_prompt)
        
        messages = [system_message, human_message]
        return self.invoke_llm(messages)
    
    def _generate_summary_only_analysis(self, summary: str, title: str, main_query: str) -> str:
        """Generate analysis when we only have the summary"""
        
        # ✅ REPLACE the hardcoded prompts with these lines:
        system_prompt = load_prompt("optimizer_system")
        human_prompt = format_prompt(
            "optimizer_summary_only_human",
            title=title,
            main_query=main_query,
            summary=summary
        )
        
        system_message = SystemMessage(content=system_prompt)
        human_message = HumanMessage(content=human_prompt)
        
        messages = [system_message, human_message]
        return self.invoke_llm(messages)

def optimizer_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ContentOptimizerAgent()
    return agent.execute(state)