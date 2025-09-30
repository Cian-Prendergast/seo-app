from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class CompetitiveSummaryAgent(BaseAgent):
    def __init__(self):
        super().__init__("competitive_summary")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Analyzing competitor content and strategies")
        
        competitor_content = state.get("competitor_content", {})
        if not competitor_content or competitor_content.get("status") == "skipped":
            return {
                **state,
                "competitive_analysis": {"status": "skipped", "reason": "No competitor content available"},
                "current_step": "competitive_analysis_skipped"
            }
        
        try:
            # Prepare competitor content for analysis
            competitor_summaries = []
            for url, content in competitor_content.items():
                if isinstance(content, dict) and content.get("status") == "success":
                    summary = {
                        "url": url,
                        "title": content.get("h1") or content.get("title", ""),
                        "h2s": content.get("h2s", [])[:5],  # Top 5 H2s
                        "content_length": len(content.get("full_text", "")),
                        "preview": content.get("full_text", "")[:500]  # First 500 chars
                    }
                    competitor_summaries.append(summary)
            
            if not competitor_summaries:
                return {
                    **state,
                    "competitive_analysis": {"status": "no_data"},
                    "current_step": "competitive_analysis_failed"
                }
            
            system_message = SystemMessage(content="""
            You are a competitive analysis expert. Analyze competitor content and identify:
            1. Common content themes and topics
            2. Content structure patterns (H2 headings, length, etc.)
            3. Content gaps and opportunities
            4. Competitive advantages/weaknesses
            
            Return JSON:
            {
                "common_themes": ["theme1", "theme2"],
                "content_patterns": {
                    "avg_length": 2500,
                    "common_h2_topics": ["topic1", "topic2"],
                    "structure_insights": "..."
                },
                "content_gaps": ["gap1", "gap2"],
                "recommendations": ["rec1", "rec2"]
            }
            """)
            
            competitor_data = json.dumps(competitor_summaries, indent=2)
            human_message = HumanMessage(content=f"""
            Analyze these competitor pages and provide competitive insights:
            
            {competitor_data}
            
            Return JSON with competitive analysis.
            """)
            
            response = self.invoke_llm([system_message, human_message])
            
            # Parse JSON
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group(1))
            else:
                try:
                    analysis_data = json.loads(response)
                except:
                    # Fallback analysis
                    analysis_data = {
                        "common_themes": ["informational content", "product features"],
                        "content_patterns": {
                            "avg_length": sum(s["content_length"] for s in competitor_summaries) // len(competitor_summaries),
                            "common_h2_topics": [],
                            "structure_insights": "Analysis failed, using fallback data"
                        },
                        "content_gaps": ["detailed analysis", "user examples"],
                        "recommendations": ["Add more depth", "Include practical examples"]
                    }
            
            self.log(f"Analyzed {len(competitor_summaries)} competitor pages")
            print(f"🔍 Competitive Analysis:")
            print(f"   📊 Pages analyzed: {len(competitor_summaries)}")
            print(f"   🎯 Common themes: {', '.join(analysis_data.get('common_themes', [])[:3])}")
            print(f"   📝 Avg content length: {analysis_data.get('content_patterns', {}).get('avg_length', 'N/A')}")
            print()
            
            return {
                **state,
                "competitive_analysis": analysis_data,
                "competitor_summaries": competitor_summaries,
                "current_step": "competitive_analysis_completed"
            }
            
        except Exception as e:
            self.log(f"Competitive analysis failed: {str(e)}", "error")
            return {
                **state,
                "competitive_analysis": {"status": "error", "error": str(e)},
                "current_step": "competitive_analysis_failed"
            }

def competitive_summary_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = CompetitiveSummaryAgent()
    return agent.execute(state)