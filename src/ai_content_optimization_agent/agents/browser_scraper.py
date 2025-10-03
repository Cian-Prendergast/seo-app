import os
from playwright.sync_api import sync_playwright
from base_agent import BaseAgent
from state import ContentOptimizationState

class BrowserScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("browser_scraper")
        self.browser_username = os.getenv("BRIGHT_DATA_BROWSER_USERNAME")
        self.browser_password = os.getenv("BRIGHT_DATA_BROWSER_PASSWORD")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Starting Browser API scraping with JavaScript rendering")
        url = state["url"]
        
        if not self.browser_username or not self.browser_password:
            error_msg = "BRIGHT_DATA_BROWSER_USERNAME and BRIGHT_DATA_BROWSER_PASSWORD not configured"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Configuration Error",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "browser_scraping_failed"
            }
        
        try:
            page_content, title = self._scrape_with_browser(url)
            
            self.log(f"✅ Extracted title: {title}")
            self.log(f"✅ Full page content length: {len(page_content)} characters")
            
            # Save scraped content to output files
            output_files = state.get("output_files", {})
            output_files["scraped_page.md"] = f"# Scraped Content from {url}\n\n{page_content}"
            
            return {
                **state,
                "title": title,
                "page_content": page_content,
                "output_files": output_files,
                "current_step": "browser_scraped"
            }
            
        except Exception as e:
            error_msg = f"Failed to scrape with Browser API: {str(e)}"
            self.log(error_msg, "error")
            return {
                **state,
                "title": "Error scraping with browser",
                "errors": state.get("errors", []) + [error_msg],
                "current_step": "browser_scraping_failed"
            }
    
    def _scrape_with_browser(self, target_url: str) -> tuple[str, str]:
        """Scrape page content using Browser API with Playwright"""
        
        print(f"[DEBUG BROWSER_SCRAPER] 🌐 Scraping URL with Browser API: {target_url}")
        print(f"[DEBUG BROWSER_SCRAPER] 🔑 Using username: {self.browser_username[:30]}...")
        
        ws_endpoint = f"wss://{self.browser_username}:{self.browser_password}@brd.superproxy.io:9222"
        
        with sync_playwright() as p:
            print("[DEBUG BROWSER_SCRAPER] 📡 Establishing browser connection...")
            browser = p.chromium.connect_over_cdp(ws_endpoint)
            
            try:
                print("[DEBUG BROWSER_SCRAPER] 📄 Creating new page...")
                page = browser.new_page()
                
                print(f"[DEBUG BROWSER_SCRAPER] 🚀 Navigating to {target_url}...")
                page.goto(target_url, wait_until="load", timeout=90000)
                
                print("[DEBUG BROWSER_SCRAPER] ⏳ Waiting 15 seconds for content to render...")
                page.wait_for_timeout(15000)  # Wait 15 seconds
                
                # Scroll to trigger any lazy loading
                print("[DEBUG BROWSER_SCRAPER] 📜 Scrolling...")
                for i in range(3):
                    page.evaluate(f"window.scrollTo(0, {i * 1000});")
                    page.wait_for_timeout(1000)
                
                page.evaluate("window.scrollTo(0, 0);")
                page.wait_for_timeout(2000)
                
                # Get title
                title = page.title() or "No title found"
                
                # Save the raw HTML for inspection
                full_html = page.content()
                
                # Save HTML to file for debugging
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(full_html)
                print(f"[DEBUG BROWSER_SCRAPER] 💾 Saved HTML to debug_page.html ({len(full_html)} chars)")
                
                # Extract all visible text
                page_content = page.evaluate("""() => {
                    return document.body.innerText;
                }""")
                
                print(f"[DEBUG BROWSER_SCRAPER] 📖 Extracted: {len(page_content)} chars")
                print(f"[DEBUG BROWSER_SCRAPER] First 500 chars:\n{page_content[:500]}")
                
                # If still minimal, take a screenshot to see what's rendered
                if len(page_content) < 200:
                    print("[DEBUG BROWSER_SCRAPER] 📸 Taking screenshot...")
                    page.screenshot(path="debug_screenshot.png", full_page=True)
                    print("[DEBUG BROWSER_SCRAPER] 💾 Saved screenshot to debug_screenshot.png")
                
                return page_content, title
                
            finally:
                print("[DEBUG BROWSER_SCRAPER] 🔒 Closing browser...")
                browser.close()

def browser_scraper_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = BrowserScraperAgent()
    return agent.execute(state)