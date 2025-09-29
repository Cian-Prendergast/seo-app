from typing import TypedDict, Optional, List, Dict, Any, Annotated
from pydantic import BaseModel

class ContentOptimizationState(TypedDict):
    # EXISTING FIELDS
    url: Annotated[str, "single"]  # Only one value allowed per step
    title: Optional[str]
    page_content: Optional[str]
    search_results: Optional[str]
    main_query: Optional[str]
    ai_overview: Optional[str]
    query_fanout_summary: Optional[str]
    comparison_report: Optional[str]
    current_step: str
    errors: List[str]
    retry_count: int
    output_files: Dict[str, str]
    intent_analysis: Optional[Dict[str, Any]]
    keyword_data: Optional[Dict[str, Any]]
    competitor_urls: Optional[List[str]]
    competitor_content: Optional[Dict[str, str]]
    competitive_analysis: Optional[Dict[str, Any]]
    content_topics: Optional[List[str]]
    content_gaps: Optional[List[Dict[str, str]]]
    
    # NEW FIELDS FOR ING BRIEFING FORMAT
    focus_keyword: Optional[str]  # User-provided or auto-extracted
    secondary_keywords: Optional[List[str]]  # User-provided or auto-extracted
    page_type: Optional[str]  # "Blog", "Product", "Landing Page", etc.
    funnel_stage: Optional[str]  # "Awareness", "Consideration", "Decision"
    tone_of_voice: Optional[str]  # "ING", "casual", "professional", etc.
    language: Optional[str]  # "nl", "en", etc.
    
    # Briefing-specific outputs
    page_title_suggestion: Optional[str]
    meta_description_suggestion: Optional[str]
    header_suggestions: Optional[Dict[str, List[str]]]  # H1, H2, H3
    body_copy_outline: Optional[str]
    notable_observations: Optional[str]

class AgentConfig(BaseModel):
    """Configuration for each agent/node"""
    max_retries: int = 3
    timeout: int = 30
    model: str = "gemini/gemini-2.5-flash"
    verbose: bool = True
