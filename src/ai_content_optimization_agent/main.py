import warnings
import os
from typing import List
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
    """Interactive mode with optional keyword input"""
    url = input("Please enter the URL to process: ").strip()
    if not url:
        raise ValueError("No URL provided. Exiting.")
    
    # NEW OPTIONAL KEYWORD INPUT
    focus_keyword = input("Focus keyword (optional, press Enter to skip): ").strip() or None
    
    secondary_keywords = []
    if input("Add secondary keywords? (y/n): ").strip().lower() == 'y':
        print("Enter secondary keywords (one per line, empty line to finish):")
        while True:
            keyword = input("  - ").strip()
            if not keyword:
                break
            secondary_keywords.append(keyword)
    
    tone_of_voice = input("Tone of voice (ING/casual/professional, default: ING): ").strip() or "ING"
    language = input("Language (nl/en, default: nl): ").strip() or "nl"
    
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
        
        # Enhanced SEO fields
        "intent_analysis": None,
        "keyword_data": None,
        "competitor_urls": None,
        "competitor_content": None,
        "competitive_analysis": None,
        "content_topics": None,
        "content_gaps": None,
        
        # NEW ING BRIEFING FIELDS
        "focus_keyword": focus_keyword,
        "secondary_keywords": secondary_keywords if secondary_keywords else None,
        "page_type": None,
        "funnel_stage": None,
        "tone_of_voice": tone_of_voice,
        "language": language,
        "page_title_suggestion": None,
        "meta_description_suggestion": None,
        "header_suggestions": None,
        "body_copy_outline": None,
        "notable_observations": None,
    }
    
    try:
        print(f"🚀 Analyzing '{url}' for content briefing...")
        print(f"📊 Focus keyword: {focus_keyword or 'Auto-detect'}")
        print(f"📊 Language: {language}")
        
        app = create_workflow()
        final_state = app.invoke(initial_state)
        
        if final_state["current_step"] == "briefing_completed":
            print("✅ Analysis completed successfully!")
            save_output_files(final_state)
            
            # NEW SAVE ING BRIEFING FORMAT
            from briefing_formatter import generate_ing_briefing
            briefing_docx = generate_ing_briefing(final_state)
            print(f"✅ Saved ING Content Briefing: {briefing_docx}")
            
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

def run_with_custom_input(url: str, focus_keyword: str = None, 
                          secondary_keywords: List[str] = None,
                          tone_of_voice: str = "ING",
                          language: str = "nl", **kwargs):
    """Programmatic interface with keyword support"""
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
        "intent_analysis": None,
        "keyword_data": None,
        "competitor_urls": None,
        "competitor_content": None,
        "competitive_analysis": None,
        "content_topics": None,
        "content_gaps": None,
        "focus_keyword": focus_keyword,
        "secondary_keywords": secondary_keywords,
        "page_type": None,
        "funnel_stage": None,
        "tone_of_voice": tone_of_voice,
        "language": language,
        "page_title_suggestion": None,
        "meta_description_suggestion": None,
        "header_suggestions": None,
        "body_copy_outline": None,
        "notable_observations": None,
        **kwargs
    }
    
    app = create_workflow()
    return app.invoke(initial_state)

if __name__ == "__main__":
    run()
