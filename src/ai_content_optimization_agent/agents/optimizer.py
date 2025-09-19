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
        
        system_message = SystemMessage(content="""
        You are an AI content optimization specialist. Analyze the provided content and generate 
        actionable SEO and content optimization recommendations. Focus on identifying opportunities
        and providing specific, implementable suggestions.
        """)
        
        human_message = HumanMessage(content=f"""
        Analyze this content for optimization opportunities:
        
        **Page Title:** {title}
        **Main Query:** {main_query}
        
        ## Query Fan-Out Summary:
        {summary}
        
        ## {overview_type}:
        {ai_overview}
        
        Please provide a comprehensive analysis with:
        
        1. **Executive Summary** - Key optimization opportunities and priorities
        2. **Content Analysis** - What themes and topics are most important for this query
        3. **SEO Recommendations** - Specific improvements for search visibility
        4. **Content Strategy** - How to align content with search intent
        5. **Competitive Insights** - What the analysis reveals about the competitive landscape
        6. **Action Items** - Concrete next steps to implement
        
        {"Note: The AI overview was synthesized from search results since no native Google AI overview was available for this query." if is_synthesized else ""}
        
        Format everything in clean Markdown with proper headers and structure. Be specific and actionable.
        """)
        
        messages = [system_message, human_message]
        return self.invoke_llm(messages)
    
    def _generate_summary_only_analysis(self, summary: str, title: str, main_query: str) -> str:
        """Generate analysis when we only have the summary"""
        system_message = SystemMessage(content="""
        You are an AI content optimization specialist. Analyze the provided query fanout summary
        to generate actionable SEO and content optimization recommendations.
        """)
        
        human_message = HumanMessage(content=f"""
        Analyze this content for optimization opportunities:
        
        **Page Title:** {title}
        **Main Query:** {main_query}
        
        ## Query Fan-Out Summary:
        {summary}
        
        **Note:** No AI overview data was available for this analysis.
        
        Please provide:
        1. **Executive Summary** - Key optimization opportunities
        2. **Query Pattern Analysis** - Insights from search behavior
        3. **Content Optimization Recommendations** - Specific improvements
        4. **SEO Strategy** - How to target the identified search patterns
        5. **Content Gaps** - What might be missing from current content
        6. **Next Steps** - Prioritized action items
        
        Base your analysis entirely on the query fanout patterns and search intent signals.
        """)
        
        messages = [system_message, human_message]
        return self.invoke_llm(messages)

def optimizer_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ContentOptimizerAgent()
    return agent.execute(state)