from langgraph.graph import END, MessageGraph
from state import ContentOptimizationState
from agents.title_scraper import title_scraper_node
from agents.query_researcher import query_researcher_node
from agents.query_extractor import query_extractor_node
from agents.ai_overview_retriever import ai_overview_node
from agents.summarizer import summarizer_node
from agents.optimizer import optimizer_node
import logging

def create_workflow():
    logging.basicConfig(level=logging.INFO)
    workflow = StateGraph(ContentOptimizationState)
    workflow.add_node("title_scraper", title_scraper_node)
    workflow.add_node("query_researcher", query_researcher_node)
    workflow.add_node("query_extractor", query_extractor_node)
    workflow.add_node("ai_overview_retriever", ai_overview_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("content_optimizer", optimizer_node)
    workflow.add_edge(START, "title_scraper")
    workflow.add_edge("title_scraper", "query_researcher")
    workflow.add_edge("query_researcher", "query_extractor")
    workflow.add_edge("query_extractor", "ai_overview_retriever")
    workflow.add_edge("query_researcher", "summarizer")
    workflow.add_edge(["ai_overview_retriever", "summarizer"], "content_optimizer")
    workflow.add_edge("content_optimizer", END)
    return workflow.compile()

def save_output_files(state: ContentOptimizationState, output_dir: str = "output"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    output_files = state.get("output_files", {})
    for filename, content in output_files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Saved {filepath}")
