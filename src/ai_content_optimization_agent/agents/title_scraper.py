import requests
from bs4 import BeautifulSoup
from base_agent import BaseAgent
from state import ContentOptimizationState

class TitleScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("title_scraper")
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting title extraction")
        url = state["url"]
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            else:
                title_tag = soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else "No title found"
            self.log(f"Extracted title: {title}")
            return {
                **state,
                "title": title,
                "page_content": soup.get_text()[:2000],
                "current_step": "title_extracted"
            }
        except Exception as e:
            error_msg = f"Failed to extract title: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Error extracting title",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "title_extraction_failed"
            }
def title_scraper_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = TitleScraperAgent()
    return agent.execute(state)
