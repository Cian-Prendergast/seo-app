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
        
        print(f"[DEBUG BROWSER_SCRAPER] 🔌 Connecting to Browser API...")
        
        with sync_playwright() as p:
            print("[DEBUG BROWSER_SCRAPER] 📡 Establishing browser connection...")
            browser = p.chromium.connect_over_cdp(ws_endpoint)
            
            try:
                print("[DEBUG BROWSER_SCRAPER] 📄 Creating new page...")
                page = browser.new_page()
                
                print(f"[DEBUG BROWSER_SCRAPER] 🚀 Navigating to {target_url}...")
                page.goto(target_url, wait_until="domcontentloaded", timeout=90000)
                
                print("[DEBUG BROWSER_SCRAPER] ⏳ Waiting for JavaScript to render content...")
                # Wait longer for JavaScript to execute
                page.wait_for_timeout(10000)  # 10 seconds
                
                # Try multiple selectors to wait for content
                print("[DEBUG BROWSER_SCRAPER] 🔍 Waiting for main content...")
                try:
                    # Wait for common content containers
                    page.wait_for_selector("main, article, [role='main'], .content, #content", timeout=15000)
                except:
                    print("[DEBUG BROWSER_SCRAPER] ⚠️ No main content selector found, continuing...")
                
                # Extract title
                title = page.title() or "No title found"
                print(f"[DEBUG BROWSER_SCRAPER] 📝 Title: {title}")
                
                # Try multiple methods to get content
                print("[DEBUG BROWSER_SCRAPER] 📖 Extracting page content...")
                
                # Method 1: Try innerText on body
                page_content = page.evaluate("() => document.body.innerText || ''")
                print(f"[DEBUG BROWSER_SCRAPER] Method 1 (innerText): {len(page_content)} chars")
                
                # Method 2: If that's empty, try textContent
                if not page_content or len(page_content) < 100:
                    page_content = page.evaluate("() => document.body.textContent || ''")
                    print(f"[DEBUG BROWSER_SCRAPER] Method 2 (textContent): {len(page_content)} chars")
                
                # Method 3: If still empty, get all text from all elements
                if not page_content or len(page_content) < 100:
                    page_content = page.evaluate("""() => {
                        const elements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, span, div, a');
                        return Array.from(elements)
                            .map(el => el.innerText || el.textContent)
                            .filter(text => text && text.trim().length > 0)
                            .join('\\n');
                    }""")
                    print(f"[DEBUG BROWSER_SCRAPER] Method 3 (all elements): {len(page_content)} chars")
                
                # Debug: Check raw HTML to see if content exists
                html_length = page.evaluate("() => document.documentElement.outerHTML.length")
                print(f"[DEBUG BROWSER_SCRAPER] 🔍 Raw HTML length: {html_length} chars")
                
                if not page_content or len(page_content) < 50:
                    print("[DEBUG BROWSER_SCRAPER] ⚠️ Very little content extracted!")
                    # Get a sample of the HTML for debugging
                    html_sample = page.evaluate("() => document.documentElement.outerHTML.substring(0, 2000)")
                    print(f"[DEBUG BROWSER_SCRAPER] HTML sample:\n{html_sample}")
                
                print(f"[DEBUG BROWSER_SCRAPER] ✅ Successfully scraped!")
                print(f"[DEBUG BROWSER_SCRAPER] Final content length: {len(page_content)} chars")
                print(f"[DEBUG BROWSER_SCRAPER] First 2000 chars:")
                print(page_content[:2000])
                
                return page_content, title
                
            except Exception as e:
                print(f"[DEBUG BROWSER_SCRAPER] ❌ Error: {str(e)}")
                raise e
                
            finally:
                print("[DEBUG BROWSER_SCRAPER] 🔒 Closing browser connection...")
                browser.close()

def browser_scraper_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = BrowserScraperAgent()
    return agent.execute(state)