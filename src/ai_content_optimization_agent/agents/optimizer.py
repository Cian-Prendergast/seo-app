from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState

class ContentOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("content_optimizer")
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting content optimization analysis")
        summary = state.get("query_fanout_summary", "")
        ai_overview = state.get("ai_overview", "")
        if not summary or not ai_overview:
            return {
                **state,
                "errors": state.get("errors", []) + ["Missing summary or AI overview for comparison"],
                "current_step": "optimization_failed"
            }
        try:
            system_message = SystemMessage(content="""
            You are an AI assistant that analyzes content summaries and AI overviews to find 
            recurring themes, patterns, and actionable insights to optimize content strategies.
            Your goal is to compare a summary generated from a query fan-out with the Google AI Overview,
            identify patterns and similarities, and generate a list of action items based on common topics.
            """)
            human_message = HumanMessage(content=f"""
            Compare these two sources and generate a comprehensive analysis:
            ## Query Fan-Out Summary:
            {summary}
            ## Google AI Overview:
            {ai_overview}
            Please provide:
            1. A comparison table with columns: Aspect, Query Fan-Out Summary, Google AI Overview, Similarities/Patterns, Differences
            2. Detailed analysis of patterns and similarities
            3. List of actionable recommendations based on the comparison
            4. Content optimization strategies
            Format everything in clean Markdown with proper headers and structure.
            """)
            messages = [system_message, human_message]
            comparison_report = self.invoke_llm(messages)
            self.log("Optimization analysis completed")
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
def optimizer_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ContentOptimizerAgent()
    return agent.execute(state)
