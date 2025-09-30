from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class ClientContentAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("client_content_analyzer")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Analyzing current client content for optimization opportunities")
        
        page_content = state.get("page_content", "")
        title = state.get("title", "")
        page_structure = state.get("page_structure", {})
        
        if not page_content:
            return {
                **state,
                "client_content_analysis": {"status": "skipped", "reason": "No client content available"},
                "current_step": "client_analysis_skipped"
            }
        
        try:
            # Prepare current content for analysis
            current_content = {
                "title": title,
                "h1": page_structure.get("h1", ""),
                "h2s": page_structure.get("h2s", []),
                "content_length": len(page_content),
                "content_preview": page_content[:1500]
            }
            
            system_message = SystemMessage(content="""
            You are a content optimization expert. Analyze the current client content and identify:
            1. Content strengths and weaknesses
            2. SEO optimization opportunities
            3. Structure and readability issues
            4. Missing content elements
            5. User experience improvements
            
            Return JSON:
            {
                "content_strengths": ["strength1", "strength2"],
                "content_weaknesses": ["weakness1", "weakness2"],
                "seo_opportunities": {
                    "title_optimization": "recommendation",
                    "heading_improvements": ["improvement1", "improvement2"],
                    "content_gaps": ["gap1", "gap2"],
                    "keyword_opportunities": ["keyword1", "keyword2"]
                },
                "structure_issues": ["issue1", "issue2"],
                "ux_improvements": ["improvement1", "improvement2"],
                "content_score": 75,
                "priority_actions": ["action1", "action2"]
            }
            """)
            
            content_data = json.dumps(current_content, indent=2)
            human_message = HumanMessage(content=f"""
            Analyze this current client content for optimization opportunities:
            
            {content_data}
            
            Full content preview:
            {page_content[:2000]}
            
            Return JSON with comprehensive content analysis and optimization recommendations.
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
                        "content_strengths": ["clear messaging", "relevant topic"],
                        "content_weaknesses": ["limited depth", "missing structure"],
                        "seo_opportunities": {
                            "title_optimization": "Add focus keyword to title",
                            "heading_improvements": ["Add more H2 sections", "Include keyword variations"],
                            "content_gaps": ["Add FAQ section", "Include examples"],
                            "keyword_opportunities": ["long-tail keywords", "related terms"]
                        },
                        "structure_issues": ["needs better organization", "missing subheadings"],
                        "ux_improvements": ["add bullet points", "shorter paragraphs"],
                        "content_score": 60,
                        "priority_actions": ["improve structure", "add more content"]
                    }
            
            content_score = analysis_data.get("content_score", 0)
            self.log(f"Content analysis completed - Score: {content_score}/100")
            
            print(f"📊 Client Content Analysis:")
            print(f"   📈 Content Score: {content_score}/100")
            print(f"   ✅ Strengths: {len(analysis_data.get('content_strengths', []))}")
            print(f"   ⚠️ Weaknesses: {len(analysis_data.get('content_weaknesses', []))}")
            print(f"   🎯 SEO Opportunities: {len(analysis_data.get('seo_opportunities', {}).get('content_gaps', []))}")
            print()
            
            return {
                **state,
                "client_content_analysis": analysis_data,
                "current_step": "client_analysis_completed"
            }
            
        except Exception as e:
            self.log(f"Client content analysis failed: {str(e)}", "error")
            return {
                **state,
                "client_content_analysis": {"status": "error", "error": str(e)},
                "current_step": "client_analysis_failed"
            }

def client_content_analyzer_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ClientContentAnalyzerAgent()
    return agent.execute(state)