from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class ContentOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("content_optimizer")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting comprehensive content optimization analysis")
        
        # Gather all available data sources
        summary = state.get("query_fanout_summary", "")
        ai_overview = state.get("ai_overview", "")
        title = state.get("title", "")
        main_query = state.get("main_query", "")
        
        # New data sources
        keyword_data = state.get("keyword_data", {})
        intent_analysis = state.get("intent_analysis", {})
        competitive_analysis = state.get("competitive_analysis", {})
        content_topics = state.get("content_topics", {})
        client_analysis = state.get("client_content_analysis", {})
        content_additions = state.get("content_additions", {})
        page_structure = state.get("page_structure", {})
        
        # We need at least the summary or some analysis data to proceed
        if not any([summary, competitive_analysis, content_topics, client_analysis]):
            return {
                **state,
                "errors": state.get("errors", []) + ["Insufficient data for optimization analysis"],
                "current_step": "optimization_failed"
            }
        
        try:
            # Generate comprehensive optimization report using all available data
            optimization_report = self._generate_comprehensive_optimization_report(
                summary=summary,
                ai_overview=ai_overview,
                title=title,
                main_query=main_query,
                keyword_data=keyword_data,
                intent_analysis=intent_analysis,
                competitive_analysis=competitive_analysis,
                content_topics=content_topics,
                client_analysis=client_analysis,
                content_additions=content_additions,
                page_structure=page_structure
            )
            
            self.log("Comprehensive optimization analysis completed")
            
            # Save to output files
            output_files = state.get("output_files", {})
            output_files["comprehensive_optimization_report.md"] = optimization_report
            
            return {
                **state,
                "comparison_report": optimization_report,
                "comprehensive_optimization_report": optimization_report,
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
    
    def _generate_comprehensive_optimization_report(self, **kwargs) -> str:
        """Generate comprehensive optimization report using all available data"""
        
        # Extract all the parameters
        summary = kwargs.get('summary', '')
        ai_overview = kwargs.get('ai_overview', '')
        title = kwargs.get('title', '')
        main_query = kwargs.get('main_query', '')
        keyword_data = kwargs.get('keyword_data', {})
        intent_analysis = kwargs.get('intent_analysis', {})
        competitive_analysis = kwargs.get('competitive_analysis', {})
        content_topics = kwargs.get('content_topics', {})
        client_analysis = kwargs.get('client_analysis', {})
        content_additions = kwargs.get('content_additions', {})
        page_structure = kwargs.get('page_structure', {})
        
        # Prepare comprehensive data summary for analysis
        analysis_data = {
            "current_content": {
                "title": title,
                "main_query": main_query,
                "page_structure": page_structure,
                "client_score": client_analysis.get("content_score", "N/A") if client_analysis else "N/A"
            },
            "keyword_insights": {
                "search_volume": keyword_data.get("search_volume", "N/A") if isinstance(keyword_data, dict) else "N/A",
                "difficulty": keyword_data.get("keyword_difficulty", "N/A") if isinstance(keyword_data, dict) else "N/A",
                "cpc": keyword_data.get("cpc", "N/A") if isinstance(keyword_data, dict) else "N/A"
            },
            "user_intent": {
                "primary": intent_analysis.get("primary_intent", "Unknown") if intent_analysis else "Unknown",
                "confidence": intent_analysis.get("confidence", 0) if intent_analysis else 0
            },
            "competitive_landscape": {
                "common_themes": competitive_analysis.get("common_themes", []) if competitive_analysis else [],
                "content_gaps": competitive_analysis.get("content_gaps", []) if competitive_analysis else [],
                "avg_length": competitive_analysis.get("content_patterns", {}).get("avg_length", "N/A") if competitive_analysis else "N/A"
            },
            "content_analysis": {
                "main_topics": content_topics.get("main_topics", []) if content_topics else [],
                "opportunities": content_topics.get("content_opportunities", []) if content_topics else [],
                "user_questions": content_topics.get("user_questions", []) if content_topics else []
            },
            "client_weaknesses": client_analysis.get("content_weaknesses", []) if client_analysis else [],
            "recommended_additions": len(content_additions.get("new_sections", [])) if content_additions else 0
        }
        
        system_message = SystemMessage(content="""
        You are an advanced SEO and content optimization expert. Create a comprehensive optimization report
        using ALL the provided data sources. This is a complete analysis that includes:
        
        1. Executive summary with key findings
        2. Current content audit and scoring
        3. Keyword and search intent analysis
        4. Competitive landscape insights
        5. Content gap analysis
        6. Specific optimization recommendations
        7. Prioritized action plan
        8. Expected impact and ROI
        
        Make the report actionable, specific, and data-driven. Include metrics where available.
        """)
        
        data_summary = json.dumps(analysis_data, indent=2)
        human_message = HumanMessage(content=f"""
        Create a comprehensive SEO content optimization report using this complete analysis:
        
        ## Analysis Data Summary:
        {data_summary}
        
        ## Additional Context:
        
        **Query Fan-out Summary:**
        {summary[:1000] if summary else "Not available"}
        
        **AI Overview:**
        {ai_overview[:1000] if ai_overview else "Not available"}
        
        **Content Additions Generated:**
        {content_additions.get('new_sections', [])[:3] if content_additions else "None"}
        
        ## Required Report Sections:
        
        1. **🎯 Executive Summary**
           - Current content performance score
           - Top 3 optimization priorities
           - Expected impact assessment
        
        2. **📊 Current Content Audit**
           - Strengths and weaknesses analysis
           - Technical SEO status
           - Content structure evaluation
        
        3. **🔍 Keyword & Intent Analysis**
           - Search volume and competition data
           - User intent alignment
           - Keyword optimization opportunities
        
        4. **🏆 Competitive Intelligence**
           - Market positioning analysis
           - Content gap identification
           - Competitive advantage opportunities
        
        5. **💡 Optimization Recommendations**
           - Content improvements (specific)
           - Technical SEO fixes
           - User experience enhancements
        
        6. **📝 Content Strategy**
           - New content sections to add
           - Content format recommendations
           - Internal linking strategy
        
        7. **🚀 Implementation Roadmap**
           - Phase 1: Quick wins (1-2 weeks)
           - Phase 2: Content improvements (1 month)
           - Phase 3: Advanced optimizations (ongoing)
        
        8. **📈 Success Metrics**
           - KPIs to track
           - Expected timeline for results
           - ROI projections
        
        Format in clean Markdown with headers, bullet points, and tables where appropriate.
        Be specific, actionable, and data-driven in all recommendations.
        """)
        
        messages = [system_message, human_message]
        return self.invoke_llm(messages)
    
    def _generate_comparison_analysis(self, summary: str, ai_overview: str, title: str, main_query: str) -> str:
        """Legacy method - kept for compatibility"""
        return self._generate_comprehensive_optimization_report(
            summary=summary,
            ai_overview=ai_overview,
            title=title,
            main_query=main_query
        )
    
    def _generate_summary_only_analysis(self, summary: str, title: str, main_query: str) -> str:
        """Legacy method - kept for compatibility"""
        return self._generate_comprehensive_optimization_report(
            summary=summary,
            title=title,
            main_query=main_query
        )

def optimizer_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ContentOptimizerAgent()
    return agent.execute(state)