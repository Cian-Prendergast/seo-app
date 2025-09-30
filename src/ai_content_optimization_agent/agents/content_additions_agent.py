from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class ContentAdditionsAgent(BaseAgent):
    def __init__(self):
        super().__init__("content_additions")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Generating specific content additions and improvements")
        
        # Gather all analysis data
        client_analysis = state.get("client_content_analysis", {})
        competitive_analysis = state.get("competitive_analysis", {})
        content_topics = state.get("content_topics", {})
        intent_analysis = state.get("intent_analysis", {})
        keyword_data = state.get("keyword_data", {})
        
        if not any([client_analysis, content_topics, competitive_analysis]):
            return {
                **state,
                "content_additions": {"status": "skipped", "reason": "Insufficient analysis data"},
                "current_step": "content_additions_skipped"
            }
        
        try:
            # Prepare analysis summary for content generation
            analysis_summary = {
                "client_strengths": client_analysis.get("content_strengths", []),
                "client_weaknesses": client_analysis.get("content_weaknesses", []),
                "seo_opportunities": client_analysis.get("seo_opportunities", {}),
                "competitor_themes": competitive_analysis.get("common_themes", []),
                "content_gaps": competitive_analysis.get("content_gaps", []),
                "main_topics": content_topics.get("main_topics", []),
                "user_questions": content_topics.get("user_questions", []),
                "recommended_headings": content_topics.get("recommended_headings", []),
                "primary_intent": intent_analysis.get("primary_intent", "informational"),
                "keyword": keyword_data.get("keyword", "") if isinstance(keyword_data, dict) else ""
            }
            
            system_message = SystemMessage(content="""
            You are a content creation expert. Based on the comprehensive analysis provided, generate specific content additions and improvements.
            
            Create:
            1. New content sections with actual text
            2. Improved headings and subheadings
            3. FAQ content based on user questions
            4. Call-to-action improvements
            5. SEO-optimized content blocks
            
            Return JSON:
            {
                "new_sections": [
                    {
                        "heading": "H2: Section Title",
                        "content": "Actual paragraph content...",
                        "purpose": "addresses user question X"
                    }
                ],
                "improved_headings": [
                    {
                        "current": "Current heading",
                        "improved": "SEO-optimized heading",
                        "reason": "includes target keyword"
                    }
                ],
                "faq_content": [
                    {
                        "question": "Common user question?",
                        "answer": "Detailed answer content..."
                    }
                ],
                "cta_improvements": [
                    {
                        "type": "primary",
                        "text": "Optimized CTA text",
                        "placement": "after section X"
                    }
                ],
                "seo_content_blocks": [
                    {
                        "purpose": "keyword optimization",
                        "content": "SEO-focused paragraph...",
                        "placement": "introduction"
                    }
                ]
            }
            """)
            
            analysis_data = json.dumps(analysis_summary, indent=2)
            human_message = HumanMessage(content=f"""
            Based on this comprehensive analysis, generate specific content additions and improvements:
            
            {analysis_data}
            
            Create actual content text, not just suggestions. Focus on:
            - Addressing identified content gaps
            - Optimizing for the primary intent: {analysis_summary.get('primary_intent')}
            - Including target keyword: {analysis_summary.get('keyword')}
            - Answering user questions
            - Improving SEO performance
            
            Return JSON with detailed content additions.
            """)
            
            response = self.invoke_llm([system_message, human_message])
            
            # Parse JSON
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if json_match:
                additions_data = json.loads(json_match.group(1))
            else:
                try:
                    additions_data = json.loads(response)
                except:
                    # Fallback content additions
                    additions_data = {
                        "new_sections": [
                            {
                                "heading": "H2: How It Works",
                                "content": "Understanding the process is essential for making informed decisions. Here's a step-by-step breakdown of how our solution works...",
                                "purpose": "addresses user question about process"
                            }
                        ],
                        "improved_headings": [
                            {
                                "current": "Services",
                                "improved": "Complete Business Solutions & Services",
                                "reason": "includes target keywords and is more descriptive"
                            }
                        ],
                        "faq_content": [
                            {
                                "question": "What are the requirements?",
                                "answer": "The basic requirements include valid business registration, financial statements, and proof of business operations..."
                            }
                        ],
                        "cta_improvements": [
                            {
                                "type": "primary",
                                "text": "Get Started Today - Free Consultation",
                                "placement": "after main content sections"
                            }
                        ],
                        "seo_content_blocks": [
                            {
                                "purpose": "keyword optimization",
                                "content": "Our comprehensive business solutions are designed to help companies of all sizes achieve their goals through innovative approaches and proven strategies.",
                                "placement": "introduction"
                            }
                        ]
                    }
            
            total_additions = (
                len(additions_data.get("new_sections", [])) +
                len(additions_data.get("improved_headings", [])) +
                len(additions_data.get("faq_content", [])) +
                len(additions_data.get("cta_improvements", [])) +
                len(additions_data.get("seo_content_blocks", []))
            )
            
            self.log(f"Generated {total_additions} content additions")
            
            print(f"✨ Content Additions Generated:")
            print(f"   📄 New sections: {len(additions_data.get('new_sections', []))}")
            print(f"   📝 Improved headings: {len(additions_data.get('improved_headings', []))}")
            print(f"   ❓ FAQ items: {len(additions_data.get('faq_content', []))}")
            print(f"   🎯 CTA improvements: {len(additions_data.get('cta_improvements', []))}")
            print(f"   🔍 SEO blocks: {len(additions_data.get('seo_content_blocks', []))}")
            print()
            
            return {
                **state,
                "content_additions": additions_data,
                "current_step": "content_additions_completed"
            }
            
        except Exception as e:
            self.log(f"Content additions generation failed: {str(e)}", "error")
            return {
                **state,
                "content_additions": {"status": "error", "error": str(e)},
                "current_step": "content_additions_failed"
            }

def content_additions_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = ContentAdditionsAgent()
    return agent.execute(state)