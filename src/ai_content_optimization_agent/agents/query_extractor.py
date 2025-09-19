from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState

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
            system_message = SystemMessage(content="""
            You are an AI assistant specialized in parsing query fan-outs and identifying 
            the main, concise search query suitable for Google searches.
            Your goal is to extract the main Google-like search query from a provided query fan-out.
            """)
            human_message = HumanMessage(content=f"""
            From the following query fan-out, extract the main search query and transform it 
            into a concise, Google-like keyphrase that users would type into Google:
            Query Fan-out:
            {search_results}
            Return only the main search query as a short, clear phrase.
            """)
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
