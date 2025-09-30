from base_agent import BaseAgent
from state import ContentOptimizationState
from utils.web_unlocker import BrightDataWebUnlocker
import re

class CompetitiveScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("competitive_scraper")
        try:
            self.web_unlocker = BrightDataWebUnlocker()
        except ValueError as e:
            self.log(f"Web Unlocker not configured: {e}", "warning")
            self.web_unlocker = None
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Scraping top competitor pages")
        
        # Extract URLs from search results
        search_results = state.get("search_results", "")
        competitor_urls = self._extract_urls(search_results)[:3]  # Top 3
        
        if not competitor_urls:
            self.log("No competitor URLs found", "warning")
            return {
                **state,
                "competitor_urls": [],
                "competitor_content": {},
                "current_step": "competitor_scraping_failed"
            }
        
        competitor_content = {}
        
        if not self.web_unlocker:
            self.log("Web Unlocker not available - skipping competitor scraping", "warning")
            return {
                **state,
                "competitor_urls": competitor_urls,
                "competitor_content": {"status": "skipped", "reason": "Web Unlocker not configured"},
                "current_step": "competitor_scraping_skipped"
            }
        
        for i, url in enumerate(competitor_urls, 1):
            try:
                self.log(f"Scraping competitor {i}: {url}")
                print(f"🔍 Scraping competitor {i}/3: {url[:50]}...")
                
                result = self.web_unlocker.scrape_url(url, format="html")
                
                if result["status"] == "success":
                    competitor_content[url] = result
                    print(f"   ✅ Content extracted ({len(result['full_text'])} chars)")
                else:
                    print(f"   ⚠️ Failed: {result.get('error')}")
                    
            except Exception as e:
                self.log(f"Failed to scrape {url}: {str(e)}", "warning")
                print(f"   ⚠️ Error: {str(e)}")
        
        print()
        
        return {
            **state,
            "competitor_urls": competitor_urls,
            "competitor_content": competitor_content,
            "current_step": "competitor_scraped"
        }
    
    def _extract_urls(self, text: str) -> list:
        """Extract URLs from search results"""
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|[^\s<>"]+\.[com|org|net|io|nl]+'
        urls = re.findall(url_pattern, text)
        # Clean and deduplicate
        cleaned = list(set([url.rstrip('.,;:)]}') for url in urls if len(url) > 10]))
        return cleaned

def competitive_scraper_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = CompetitiveScraperAgent()
    return agent.execute(state)