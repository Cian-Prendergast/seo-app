import warnings
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Check required environment variables before importing modules that use them
required_env_vars = ["MODEL", "GEMINI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

from workflow import create_workflow, save_output_files
from state import ContentOptimizationState

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    url = input("Please enter the URL to process: ").strip()
    if not url:
        raise ValueError("No URL provided. Exiting.")
    initial_state: ContentOptimizationState = {
        "url": url,
        "title": None,
        "page_content": None,
        "search_results": None,
        "main_query": None,
        "ai_overview": None,
        "query_fanout_summary": None,
        "comparison_report": None,
        "current_step": "initialized",
        "errors": [],
        "retry_count": 0,
        "output_files": {}
    }
    try:
        print(f"🚀 Analyzing '{url}' for AI content optimization...")
        print("📊 Using LangGraph workflow (CrewAI-free)")
        app = create_workflow()
        final_state = app.invoke(initial_state)
        if final_state["current_step"] == "optimization_completed":
            print("✅ Analysis completed successfully!")
            save_output_files(final_state)
            if final_state.get("comparison_report"):
                print("\n" + "="*60)
                print("📋 FINAL REPORT")
                print("="*60)
                print(final_state["comparison_report"][:1000] + "..." if len(final_state["comparison_report"]) > 1000 else final_state["comparison_report"])
        else:
            print(f"❌ Workflow ended at step: {final_state['current_step']}")
            if final_state.get("errors"):
                print("Errors encountered:")
                for error in final_state["errors"]:
                    print(f"  - {error}")
        return final_state
    except Exception as e:
        print(f"💥 An error occurred while running the workflow: {e}")
        raise

def run_with_custom_input(url: str, **kwargs):
    initial_state: ContentOptimizationState = {
        "url": url,
        "title": None,
        "page_content": None,
        "search_results": None,
        "main_query": None,
        "ai_overview": None,
        "query_fanout_summary": None,
        "comparison_report": None,
        "current_step": "initialized",
        "errors": [],
        "retry_count": 0,
        "output_files": {},
        **kwargs
    }
    app = create_workflow()
    return app.invoke(initial_state)

if __name__ == "__main__":
    run()
