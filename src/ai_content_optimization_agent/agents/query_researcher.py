from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState

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
            system_message = SystemMessage(content="""
            You are an AI research assistant, powered by the Google Search tool.
            Your goal is: Given a title, perform a comprehensive web search to get the query fan-out.
            You have access to Google Search. Use it to research the topic thoroughly.
            """)
            human_message = HumanMessage(content=f"""
            Research this title comprehensively: "{title}"
            Perform web searches to understand:
            - What users are searching for related to this topic
            - Key questions and subtopics
            - Related keywords and phrases
            - Market context and trends
            Provide comprehensive search results and insights.
            """)
            messages = [system_message, human_message]
            # Don't pass tools - the LLM integration adds googleSearch automatically
            search_results = self.invoke_llm(messages)
            self.log("Research completed successfully")
            
            # Print search results summary
            print(f"🔍 Search Results Summary:")
            print(f"   📊 Length: {len(search_results)} characters")
            if search_results and len(search_results) > 500:
                print(f"   📝 Preview: {search_results[:500]}...")
            else:
                print(f"   📝 Content: {search_results}")
            print()
            
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
