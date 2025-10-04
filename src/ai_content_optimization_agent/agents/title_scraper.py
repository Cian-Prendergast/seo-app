import os
import requests
from base_agent import BaseAgent
from state import ContentOptimizationState

class TitleScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("title_scraper")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting page scraping with Firecrawl")
        url = state["url"]
        
        if not self.firecrawl_api_key:
            error_msg = "FIRECRAWL_API_KEY not configured"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Configuration Error",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "scraping_failed"
            }
        
        try:
            page_content, title = self._scrape_with_firecrawl(url)
            
            self.log(f"Extracted title: {title}")
            self.log(f"Content length: {len(page_content)} characters")
            
            # Save scraped content
            output_files = state.get("output_files", {})
            output_files["scraped_page.md"] = f"# Scraped Content from {url}\n\n{page_content}"
            
            return {
                **state,
                "title": title,
                "page_content": page_content,
                "output_files": output_files,
                "current_step": "title_extracted"
            }
            
        except Exception as e:
            error_msg = f"Failed to scrape: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Error scraping page",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "scraping_failed"
            }
    
    def _scrape_with_firecrawl(self, target_url: str) -> tuple[str, str]:
        """Scrape using Firecrawl API"""
        
        print(f"[title_scraper] Scraping: {target_url}")
        
        api_url = "https://api.firecrawl.dev/v2/scrape"
        
        payload = {
            "url": target_url,
            "onlyMainContent": False,
            "formats": ["markdown"]
        }
        
        headers = {
            "Authorization": f"Bearer {self.firecrawl_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract markdown content and title
        markdown_content = data.get("data", {}).get("markdown", "")
        title = data.get("data", {}).get("metadata", {}).get("title", "No title found")
        
        print(f"[title_scraper] Extracted {len(markdown_content)} chars")
        print(f"[title_scraper] Title: {title}")
        
        return markdown_content, title

def title_scraper_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = TitleScraperAgent()
    return agent.execute(state)