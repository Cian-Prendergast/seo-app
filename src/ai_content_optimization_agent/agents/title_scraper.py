import os
import requests
import json
from bs4 import BeautifulSoup
from base_agent import BaseAgent
from state import ContentOptimizationState

class TitleScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("title_scraper")
        self.bright_data_api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.bright_data_unlocker_zone = os.getenv("BRIGHT_DATA_UNLOCKER_ZONE")  # ✅ Use Unlocker zone
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting full page scraping with Bright Data Web Unlocker")
        url = state["url"]
        
        if not self.bright_data_api_key or not self.bright_data_unlocker_zone:
            error_msg = "BRIGHT_DATA_API_KEY and BRIGHT_DATA_UNLOCKER_ZONE not configured"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Configuration Error",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "title_extraction_failed"
            }
        
        try:
            # Scrape full page content using Bright Data Web Unlocker
            page_html = self._scrape_with_unblocker(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(page_html, 'html.parser')
            
            # Extract title from H1 or title tag
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            else:
                title_tag = soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else "No title found"
            
            # Get full text content
            full_text = soup.get_text(separator='\n', strip=True)
            
            self.log(f"✅ Extracted title: {title}")
            self.log(f"✅ Full page content length: {len(full_text)} characters")
            
            # Log the page content to console
            self.log("=" * 80)
            self.log("SCRAPED PAGE CONTENT (first 3000 chars):")
            self.log("=" * 80)
            self.log(full_text[:3000])
            self.log("=" * 80)
            
            # Save scraped content to output files ✅ NEW
            output_files = state.get("output_files", {})
            output_files["scraped_page.md"] = f"# Scraped Content from {url}\n\n{full_text}"
            
            return {
                **state,
                "title": title,
                "page_content": full_text,
                "raw_html": page_html,
                "output_files": output_files,  # ✅ Include output_files
                "current_step": "title_extracted"
            }
            
        except Exception as e:
            error_msg = f"Failed to scrape page: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Error extracting title",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "title_extraction_failed"
            }
    
    def _scrape_with_unblocker(self, target_url: str) -> str:
        """Scrape page content using Bright Data Web Unlocker API"""
        
        print(f"[DEBUG TITLE_SCRAPER] 🌐 Scraping URL: {target_url}")
        print(f"[DEBUG TITLE_SCRAPER] 🔑 Using API Key: {self.bright_data_api_key[:10]}...")
        print(f"[DEBUG TITLE_SCRAPER] 🏷️  Using Unlocker Zone: {self.bright_data_unlocker_zone}")
        
        api_url = "https://api.brightdata.com/request"
        
        headers = {
            "Authorization": f"Bearer {self.bright_data_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use markdown format to get rendered content
        payload = {
            "zone": self.bright_data_unlocker_zone,
            "url": target_url,
            "format": "raw",  # Changed from "json" 
            "data_format": "markdown"  # This converts HTML to markdown after rendering
        }
        
        print(f"[DEBUG TITLE_SCRAPER] 📤 Sending request with markdown format...")
        print(f"[DEBUG TITLE_SCRAPER] 📦 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                api_url, 
                headers=headers, 
                json=payload, 
                timeout=120
            )
            
            print(f"[DEBUG TITLE_SCRAPER] 📥 Response status: {response.status_code}")
            response.raise_for_status()
            
            # With format="raw" and data_format="markdown", response.text is the markdown content
            markdown_content = response.text
            
            print(f"[DEBUG TITLE_SCRAPER] ✅ Extracted content - Length: {len(markdown_content)} bytes")
            print(f"[DEBUG TITLE_SCRAPER] First 2000 chars of markdown content:")
            print(markdown_content[:2000])
            
            return markdown_content
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[DEBUG TITLE_SCRAPER] ❌ ERROR: {error_msg}")
            raise Exception(error_msg)

def title_scraper_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = TitleScraperAgent()
    return agent.execute(state)