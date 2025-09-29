from utils.prompt_loader import PromptLoader
from config import Config
from langchain_core.messages import HumanMessage
import os
import requests
from bs4 import BeautifulSoup


def get_user_inputs():
    """Get inputs from user - NO hardcoded values"""
    print("\n" + "="*60)
    print("📝 CONTENT BRIEF GENERATOR")
    print("="*60 + "\n")
    
    # Required inputs
    target_url = input("🔗 Target URL (required): ").strip()
    if not target_url:
        raise ValueError("❌ Error: URL is required")
    
    focus_keyword = input("🎯 Focus keyword (required): ").strip()
    if not focus_keyword:
        raise ValueError("❌ Error: Focus keyword is required")
    
    # Optional input
    secondary_input = input("📋 Secondary keywords, comma-separated (optional): ").strip()
    secondary_keywords = [k.strip() for k in secondary_input.split(",")] if secondary_input else []
    
    # Confirmation
    print("\n" + "-"*60)
    print("📊 INPUT SUMMARY:")
    print(f"   URL: {target_url}")
    print(f"   Focus Keyword: {focus_keyword}")
    print(f"   Secondary Keywords: {secondary_keywords if secondary_keywords else '(none)'}")
    print("-"*60 + "\n")
    
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        raise InterruptedError("❌ Cancelled by user")
    
    return {
        "target_url": target_url,
        "focus_keyword": focus_keyword,
        "secondary_keywords": secondary_keywords
    }


def fetch_page_content(url):
    """Fetch page content using web scraping"""
    print(f"   Fetching: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "No title found"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '') if meta_desc else ""
        
        # Extract H1
        h1_tag = soup.find('h1')
        h1 = h1_tag.get_text(strip=True) if h1_tag else ""
        
        # Extract H2s
        h2_tags = soup.find_all('h2')
        h2s = [tag.get_text(strip=True) for tag in h2_tags[:5]]  # Limit to first 5
        
        # Extract body text (first 1000 chars)
        body_text = soup.get_text()[:1000]
        
        return {
            "title": title,
            "meta_description": meta_description,
            "h1": h1,
            "h2s": h2s,
            "body": body_text
        }
        
    except Exception as e:
        print(f"   ⚠️  Error fetching page: {e}")
        # Return fallback data
        return {
            "title": "Could not fetch title",
            "meta_description": "Could not fetch meta description",
            "h1": "Could not fetch H1",
            "h2s": ["Could not fetch H2s"],
            "body": "Could not fetch content"
        }


def get_serp_results(keyword, num_results=3):
    """Fetch SERP results using Bright Data SERP API"""
    print(f"   Fetching SERP for: {keyword}")
    
    try:
        import urllib.parse
        import json
        
        # Bright Data SERP API endpoint
        url = "https://api.brightdata.com/request"
        headers = {
            "Authorization": f"Bearer {Config.BRIGHT_DATA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # URL encode the query properly
        encoded_query = urllib.parse.quote(keyword)
        search_url = f"https://www.google.com/search?q={encoded_query}&hl=en&gl=us&brd_json=1"
        
        # Bright Data payload
        payload = {
            "zone": Config.BRIGHT_DATA_ZONE,
            "url": search_url,
            "format": "raw"
        }
        
        print(f"   Calling Bright Data API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract organic results
        organic_results = []
        if "organic_results" in data:
            results = data["organic_results"]
        elif "organic" in data:
            results = data["organic"]
        elif "results" in data:
            results = data["results"]
        else:
            print(f"   ⚠️  No organic results found. Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return []
        
        # Format results for our system
        for i, result in enumerate(results[:num_results]):
            organic_results.append({
                "url": result.get("url", f"https://example{i+1}.com"),
                "title": result.get("title", f"Result {i+1}"),
                "description": result.get("snippet", "") or result.get("description", f"Meta {i+1}")
            })
        
        print(f"   ✅ Found {len(organic_results)} SERP results")
        return organic_results
        
    except Exception as e:
        print(f"   ⚠️  SERP API error: {e}")
        print(f"   Using fallback dummy data...")
        # Fallback to dummy data if API fails
        return [
            {"url": "https://example1.com", "title": "Result 1", "description": "Meta 1"},
            {"url": "https://example2.com", "title": "Result 2", "description": "Meta 2"},
            {"url": "https://example3.com", "title": "Result 3", "description": "Meta 3"},
        ]


def main():
    """Main orchestration - simple 3-agent flow"""
    
    # ============================================
    # STEP 1: GET INPUTS
    # ============================================
    try:
        inputs = get_user_inputs()
    except (ValueError, InterruptedError) as e:
        print(f"\n{e}\n")
        return
    
    target_url = inputs["target_url"]
    focus_keyword = inputs["focus_keyword"]
    secondary_keywords = inputs["secondary_keywords"]
    
    # Initialize
    loader = PromptLoader(Config.PROMPTS_DIR)
    llm = Config.get_llm()
    
    # Load brand guidelines
    with open(Config.BRAND_GUIDELINES_FILE, 'r', encoding='utf-8') as f:
        tone_of_voice = f.read()
    
    # ============================================
    # STEP 2: FETCH DATA (NOT from LLM)
    # ============================================
    print("\n🌐 Fetching data...\n")
    
    # Fetch target page
    page_content = fetch_page_content(target_url)
    
    # Fetch SERP results
    serp_results = get_serp_results(focus_keyword, num_results=3)
    
    # Prepare SERP data for prompts
    serp_data = {}
    for i, serp in enumerate(serp_results, 1):
        serp_data[f"serp_{i}_url"] = serp["url"]
        serp_data[f"serp_{i}_title"] = serp["title"]
        serp_data[f"serp_{i}_meta"] = serp["description"]
    
    print("✅ Data fetched\n")
    
    # ============================================
    # STEP 3: AGENT 1 - SERP ANALYZER
    # ============================================
    print("🔍 Running SERP Analyzer...")
    
    serp_prompt = loader.load(
        "serp_analyzer.txt",
        focus_keyword=focus_keyword,
        **serp_data
    )
    
    serp_analysis = llm.invoke([HumanMessage(content=serp_prompt)]).content
    print("✅ SERP analysis complete\n")
    
    # ============================================
    # STEP 4: AGENT 2 - PAGE ANALYZER
    # ============================================
    print("📄 Running Page Analyzer...")
    
    page_prompt = loader.load(
        "page_analyzer.txt",
        industry="Banking",  # Could make this an input too
        target_url=target_url,
        current_title=page_content["title"],
        current_meta=page_content["meta_description"],
        current_h1=page_content["h1"],
        current_h2s=", ".join(page_content["h2s"]),
        focus_keyword=focus_keyword,
        secondary_keywords=", ".join(secondary_keywords) if secondary_keywords else "None provided",
        tone_of_voice=tone_of_voice
    )
    
    page_analysis = llm.invoke([HumanMessage(content=page_prompt)]).content
    print("✅ Page analysis complete\n")
    
    # ============================================
    # STEP 5: AGENT 3 - BRIEF GENERATOR
    # ============================================
    print("📝 Generating content brief...")
    
    brief_prompt = loader.load(
        "brief_generator.txt",
        serp_analysis=serp_analysis,
        page_analysis=page_analysis,
        target_url=target_url,
        focus_keyword=focus_keyword,
        secondary_keywords=", ".join(secondary_keywords) if secondary_keywords else "Geen",
        tone_of_voice=tone_of_voice,
        **serp_data  # Include SERP URLs in brief
    )
    
    completed_brief = llm.invoke([HumanMessage(content=brief_prompt)]).content
    print("✅ Brief generated\n")
    
    # ============================================
    # STEP 6: SAVE OUTPUT
    # ============================================
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    # Create safe filename
    safe_keyword = focus_keyword.replace(" ", "_").replace("/", "-")
    output_file = os.path.join(Config.OUTPUT_DIR, f"brief_{safe_keyword}.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(completed_brief)
    
    print("="*60)
    print(f"✅ SUCCESS! Brief saved to: {output_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()