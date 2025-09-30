from langgraph.graph import StateGraph, START, END
from state import ContentOptimizationState
from agents.title_scraper import title_scraper_node
from agents.query_researcher import query_researcher_node
from agents.query_extractor import query_extractor_node
from agents.ai_overview_retriever import ai_overview_node
from agents.summarizer import summarizer_node
from agents.optimizer import optimizer_node
from agents.briefing_generator import briefing_generator_node
# New agents
from agents.semrush_keyword_agent import semrush_keyword_node
from agents.intent_categorization_agent import intent_categorization_node
from agents.competitive_scraper_agent import competitive_scraper_node
from agents.competitive_summary_agent import competitive_summary_node
from agents.content_topics_extractor_agent import content_topics_extractor_node
from agents.client_content_analyzer_agent import client_content_analyzer_node
from agents.content_additions_agent import content_additions_node
import logging

# Wrapper functions to add progress indicators
def title_scraper_wrapper(state):
    print("🏃‍♂️ Step 1/13: Extracting page title and content...")
    result = title_scraper_node(state)
    print(f"   ✅ Title: {result.get('title', 'Unknown')}")
    print()
    return result

def query_researcher_wrapper(state):
    print("🏃‍♂️ Step 2/13: Researching search landscape...")
    result = query_researcher_node(state)
    return result

def query_extractor_wrapper(state):
    print("🏃‍♂️ Step 3/13: Extracting main search query...")
    result = query_extractor_node(state)
    return result

def competitive_scraper_wrapper(state):
    print("🏃‍♂️ Step 4/13: Scraping competitor content...")
    result = competitive_scraper_node(state)
    return result

def semrush_keyword_wrapper(state):
    print("🏃‍♂️ Step 5/13: Fetching keyword data...")
    result = semrush_keyword_node(state)
    return result

def intent_categorization_wrapper(state):
    print("🏃‍♂️ Step 6/13: Analyzing user intent...")
    result = intent_categorization_node(state)
    return result

def competitive_summary_wrapper(state):
    print("🏃‍♂️ Step 7/13: Analyzing competitive landscape...")
    result = competitive_summary_node(state)
    return result

def content_topics_extractor_wrapper(state):
    print("🏃‍♂️ Step 8/13: Extracting content topics...")
    result = content_topics_extractor_node(state)
    return result

def client_content_analyzer_wrapper(state):
    print("🏃‍♂️ Step 9/13: Analyzing current client content...")
    result = client_content_analyzer_node(state)
    return result

def ai_overview_wrapper(state):
    print("🏃‍♂️ Step 10/13: Retrieving AI overview...")
    result = ai_overview_node(state)
    return result

def summarizer_wrapper(state):
    print("🏃‍♂️ Step 11/13: Summarizing all analysis...")
    result = summarizer_node(state)
    print(f"   ✅ Summary generated")
    print()
    return result

def content_additions_wrapper(state):
    print("🏃‍♂️ Step 12/13: Generating content additions...")
    result = content_additions_node(state)
    return result

def optimizer_wrapper(state):
    print("🏃‍♂️ Step 13/13: Generating optimization report...")
    result = optimizer_node(state)
    print(f"   ✅ Report completed")
    print()
    return result

def briefing_generator_wrapper(state):
    print("🏃‍♂️ Final Step: Generating ING content briefing...")
    result = briefing_generator_node(state)
    return result

def create_workflow():
    logging.basicConfig(level=logging.INFO)
    workflow = StateGraph(ContentOptimizationState)
    
    # Phase 1: Data Collection
    workflow.add_node("title_scraper", title_scraper_wrapper)
    workflow.add_node("query_researcher", query_researcher_wrapper)
    workflow.add_node("query_extractor", query_extractor_wrapper)
    workflow.add_node("competitive_scraper", competitive_scraper_wrapper)
    workflow.add_node("semrush_keyword", semrush_keyword_wrapper)
    
    # Phase 2: Analysis
    workflow.add_node("intent_categorization", intent_categorization_wrapper)
    workflow.add_node("competitive_summary", competitive_summary_wrapper)
    workflow.add_node("content_topics_extractor", content_topics_extractor_wrapper)
    workflow.add_node("client_content_analyzer", client_content_analyzer_wrapper)
    workflow.add_node("ai_overview_retriever", ai_overview_wrapper)
    
    # Phase 3: Content Generation & Optimization
    workflow.add_node("summarizer", summarizer_wrapper)
    workflow.add_node("content_additions", content_additions_wrapper)
    workflow.add_node("content_optimizer", optimizer_wrapper)
    workflow.add_node("briefing_generator", briefing_generator_wrapper)
    
    # Sequential flow - comprehensive SEO analysis pipeline
    workflow.add_edge(START, "title_scraper")
    workflow.add_edge("title_scraper", "query_researcher")
    workflow.add_edge("query_researcher", "query_extractor")
    workflow.add_edge("query_extractor", "competitive_scraper")
    workflow.add_edge("competitive_scraper", "semrush_keyword")
    workflow.add_edge("semrush_keyword", "intent_categorization")
    workflow.add_edge("intent_categorization", "competitive_summary")
    workflow.add_edge("competitive_summary", "content_topics_extractor")
    workflow.add_edge("content_topics_extractor", "client_content_analyzer")
    workflow.add_edge("client_content_analyzer", "ai_overview_retriever")
    workflow.add_edge("ai_overview_retriever", "summarizer")
    workflow.add_edge("summarizer", "content_additions")
    workflow.add_edge("content_additions", "content_optimizer")
    workflow.add_edge("content_optimizer", "briefing_generator")
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