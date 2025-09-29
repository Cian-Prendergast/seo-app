from langgraph.graph import StateGraph, START, END
from state import ContentOptimizationState
from agents.title_scraper import title_scraper_node
from agents.query_researcher import query_researcher_node
from agents.query_extractor import query_extractor_node
from agents.ai_overview_retriever import ai_overview_node
from agents.summarizer import summarizer_node
from agents.optimizer import optimizer_node
from agents.briefing_generator import briefing_generator_node
import logging

def create_workflow():
    logging.basicConfig(level=logging.INFO)
    workflow = StateGraph(ContentOptimizationState)
    
    # Add all nodes
    workflow.add_node("title_scraper", title_scraper_node)
    workflow.add_node("query_researcher", query_researcher_node)
    workflow.add_node("query_extractor", query_extractor_node)
    workflow.add_node("ai_overview_retriever", ai_overview_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("content_optimizer", optimizer_node)
    workflow.add_node("briefing_generator", briefing_generator_node)
    
    # Sequential flow - no parallel execution
    workflow.add_edge(START, "title_scraper")
    workflow.add_edge("title_scraper", "query_researcher")
    workflow.add_edge("query_researcher", "query_extractor")
    workflow.add_edge("query_extractor", "ai_overview_retriever")  # Run first
    workflow.add_edge("ai_overview_retriever", "summarizer")       # Then run this
    workflow.add_edge("summarizer", "content_optimizer")           # Then this
    workflow.add_edge("content_optimizer", "briefing_generator")   # Finally briefing generator
    workflow.add_edge("briefing_generator", END)
    
    return workflow.compile()

def save_output_files(state: ContentOptimizationState, output_dir: str = "output"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    output_files = state.get("output_files", {})
    
    for filename, content in output_files.items():
        filepath = os.path.join(output_dir, filename)
        
        # Convert content to string if it's not already
        if isinstance(content, list):
            # Join list items with newlines
            content_str = "\n".join(str(item) for item in content)
        elif isinstance(content, dict):
            # Convert dict to JSON string
            import json
            content_str = json.dumps(content, indent=2)
        elif content is None:
            content_str = "No content available"
        else:
            # Convert to string
            content_str = str(content)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content_str)
            print(f"✅ Saved {filepath}")
        except Exception as e:
            print(f"❌ Failed to save {filepath}: {str(e)}")
            print(f"   Content type: {type(content)}")
            if hasattr(content, '__len__'):
                print(f"   Content length: {len(content)}")