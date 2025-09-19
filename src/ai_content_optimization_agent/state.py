from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel

class ContentOptimizationState(TypedDict):
    url: str
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

class AgentConfig(BaseModel):
    """Configuration for each agent/node"""
    max_retries: int = 3
    timeout: int = 30
    model: str = "gemini/gemini-2.5-flash"
    verbose: bool = True
