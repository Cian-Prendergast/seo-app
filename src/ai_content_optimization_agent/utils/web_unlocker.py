import os
import requests
from typing import Dict, Optional

class BrightDataWebUnlocker:
    """Bright Data Web Unlocker API Client"""
    
    def __init__(self):
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.zone = os.getenv("BRIGHT_DATA_ZONE")
        
        if not self.api_key or not self.zone:
            raise ValueError("BRIGHT_DATA_API_KEY and BRIGHT_DATA_ZONE required")
        
        self.endpoint = "https://api.brightdata.com/request"
    
    def scrape_url(self, url: str, format: str = "markdown") -> Dict:
        """
        Scrape URL using Bright Data Web Unlocker
        
        Args:
            url: Target URL
            format: "markdown", "html", or "raw"
        
        Returns:
            Dict with 'content', 'title', 'meta', etc.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "zone": self.zone,
            "url": url,
            "format": format,  # markdown gives clean content
            "country": "us",
            "render": "html"  # Execute JavaScript
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse the markdown/html response
            if format == "markdown":
                return {
                    "content": data.get("body", ""),
                    "full_text": data.get("body", ""),
                    "status": "success"
                }
            else:
                # HTML format - parse with BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(data.get("body", ""), 'html.parser')
                
                return {
                    "title": soup.find('title').get_text() if soup.find('title') else "",
                    "h1": soup.find('h1').get_text(strip=True) if soup.find('h1') else "",
                    "h2s": [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
                    "paragraphs": [p.get_text(strip=True) for p in soup.find_all('p')],
                    "full_text": soup.get_text(),
                    "content": data.get("body", ""),
                    "status": "success"
                }
                
        except Exception as e:
            return {
                "content": "",
                "full_text": "",
                "status": "error",
                "error": str(e)
            }