from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState

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
            system_message = SystemMessage(content="""
            You are an AI summarization expert focused on condensing query fan-outs 
            into clear, actionable summaries in Markdown format.
            Your goal is to generate a concise and structured summary from the provided query fan-out.
            """)
            human_message = HumanMessage(content=f"""
            Generate a comprehensive summary from this query fan-out:
            {search_results}
            Create a structured Markdown summary that includes:
            - Main themes and topics
            - Key insights and patterns
            - Important keywords and phrases
            - User intent analysis
            Format the output as clean, well-structured Markdown.
            """)
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
