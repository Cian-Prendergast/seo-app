from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class IntentCategorizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("intent_categorization")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Analyzing user intent from search results")
        
        search_results = state.get("search_results", "")
        if not search_results:
            return {
                **state,
                "intent_analysis": {"status": "skipped"},
                "current_step": "intent_skipped"
            }
        
        try:
            system_message = SystemMessage(content="""
            You are an intent classification expert. Analyze search results and classify intent.
            
            Intent types:
            - Informational: User wants to learn/understand
            - Navigational: User wants specific website/brand
            - Transactional: User wants to buy/sign up
            - Commercial: User is comparing/researching before purchase
            
            Return JSON:
            {
                "primary_intent": "informational",
                "secondary_intent": "commercial",
                "confidence": 0.85,
                "reasoning": "..."
            }
            """)
            
            human_message = HumanMessage(content=f"""
            Analyze these search results and classify user intent:
            
            {search_results[:2000]}
            
            Return JSON with intent classification.
            """)
            
            response = self.invoke_llm([system_message, human_message])
            
            # Parse JSON
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group(1))
            else:
                try:
                    intent_data = json.loads(response)
                except:
                    # Fallback if parsing fails
                    intent_data = {
                        "primary_intent": "informational",
                        "secondary_intent": None,
                        "confidence": 0.5,
                        "reasoning": "Could not parse LLM response, defaulting to informational"
                    }
            
            self.log(f"Intent: {intent_data.get('primary_intent')}")
            print(f"🎯 Intent Analysis:")
            print(f"   Primary: {intent_data.get('primary_intent')}")
            print(f"   Secondary: {intent_data.get('secondary_intent')}")
            print(f"   Confidence: {intent_data.get('confidence', 0):.0%}")
            print()
            
            return {
                **state,
                "intent_analysis": intent_data,
                "current_step": "intent_completed"
            }
            
        except Exception as e:
            self.log(f"Intent analysis failed: {str(e)}", "error")
            return {
                **state,
                "intent_analysis": {"status": "error", "error": str(e)},
                "current_step": "intent_failed"
            }

def intent_categorization_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = IntentCategorizationAgent()
    return agent.execute(state)