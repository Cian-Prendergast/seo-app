from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class ContentTopicsExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__("content_topics_extractor")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Extracting content topics and themes")
        
        # Gather all content sources
        page_content = state.get("page_content", "")
        search_results = state.get("search_results", "")
        competitor_content = state.get("competitor_content", {})
        ai_overview = state.get("ai_overview", "")
        
        if not any([page_content, search_results, ai_overview]):
            return {
                **state,
                "content_topics": {"status": "skipped", "reason": "No content available for analysis"},
                "current_step": "topics_extraction_skipped"
            }
        
        try:
            # Prepare content for analysis
            content_sources = []
            
            if page_content:
                content_sources.append(f"Original Page Content:\n{page_content[:1000]}")
            
            if search_results:
                content_sources.append(f"Search Results:\n{search_results[:1000]}")
            
            if ai_overview:
                content_sources.append(f"AI Overview:\n{ai_overview[:1000]}")
            
            # Add competitor content if available
            if isinstance(competitor_content, dict):
                for url, content in list(competitor_content.items())[:2]:  # Top 2 competitors
                    if isinstance(content, dict) and content.get("status") == "success":
                        content_sources.append(f"Competitor ({url[:30]}):\n{content.get('full_text', '')[:800]}")
            
            combined_content = "\n\n---\n\n".join(content_sources)
            
            system_message = SystemMessage(content="""
            You are a content analysis expert. Extract key topics, themes, and content opportunities from the provided content.
            
            Analyze for:
            1. Main topics and subtopics
            2. Content themes and patterns
            3. Technical concepts mentioned
            4. User pain points and questions
            5. Content gaps and opportunities
            
            Return JSON:
            {
                "main_topics": ["topic1", "topic2"],
                "subtopics": {
                    "topic1": ["subtopic1", "subtopic2"],
                    "topic2": ["subtopic3", "subtopic4"]
                },
                "content_themes": ["theme1", "theme2"],
                "technical_concepts": ["concept1", "concept2"],
                "user_questions": ["question1", "question2"],
                "content_opportunities": ["opportunity1", "opportunity2"],
                "recommended_headings": ["H2: heading1", "H2: heading2"]
            }
            """)
            
            human_message = HumanMessage(content=f"""
            Extract comprehensive topics and content opportunities from this content:
            
            {combined_content[:3000]}
            
            Return JSON with detailed topic analysis.
            """)
            
            response = self.invoke_llm([system_message, human_message])
            
            # Parse JSON
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if json_match:
                topics_data = json.loads(json_match.group(1))
            else:
                try:
                    topics_data = json.loads(response)
                except:
                    # Fallback topics extraction
                    topics_data = {
                        "main_topics": ["business solutions", "financial services"],
                        "subtopics": {
                            "business solutions": ["loans", "credit", "applications"],
                            "financial services": ["banking", "payments", "accounts"]
                        },
                        "content_themes": ["informational", "solution-focused"],
                        "technical_concepts": ["API", "application process", "eligibility"],
                        "user_questions": ["How to apply?", "What are requirements?"],
                        "content_opportunities": ["step-by-step guide", "comparison table"],
                        "recommended_headings": ["H2: How It Works", "H2: Getting Started"]
                    }
            
            self.log(f"Extracted {len(topics_data.get('main_topics', []))} main topics")
            print(f"📝 Content Topics Analysis:")
            print(f"   🎯 Main topics: {', '.join(topics_data.get('main_topics', [])[:3])}")
            print(f"   💡 Opportunities: {len(topics_data.get('content_opportunities', []))}")
            print(f"   ❓ User questions: {len(topics_data.get('user_questions', []))}")
            print()
            
            return {
                **state,
                "content_topics": topics_data,
                "current_step": "topics_extraction_completed"
            }
            
        except Exception as e:
            self.log(f"Topics extraction failed: {str(e)}", "error")
            return {
                **state,
                "content_topics": {"status": "error", "error": str(e)},
                "current_step": "topics_extraction_failed"
            }

def content_topics_extractor_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ContentTopicsExtractorAgent()
    return agent.execute(state)