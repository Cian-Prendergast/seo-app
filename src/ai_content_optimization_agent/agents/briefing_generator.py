from langchain_core.messages import HumanMessage, SystemMessage
from base_agent import BaseAgent
from state import ContentOptimizationState
import json

class BriefingGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("briefing_generator")
    
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        self.log("Generating ING-format content briefing")
        
        # Gather all available data
        url = state.get("url")
        title = state.get("title")
        search_results = state.get("search_results") or ""
        focus_keyword = state.get("focus_keyword") or state.get("main_query")
        secondary_keywords = state.get("secondary_keywords") or []
        tone_of_voice = state.get("tone_of_voice", "ING")
        language = state.get("language", "nl")
        
        # Extract competitor URLs from search results if available
        competitor_urls = self._extract_competitor_urls(search_results)
        
        # Print competitor analysis
        print(f"🏆 Competitor Analysis:")
        if competitor_urls:
            for i, url in enumerate(competitor_urls, 1):
                print(f"   {i}. {url}")
        else:
            print(f"   No competitor URLs found in search results")
        print()
        
        # Generate mock data for missing analysis fields (for initial implementation)
        keyword_data = {"keyword_variations": []}
        competitive_analysis = {"summary": {"common_patterns": []}}
        content_gaps = {"topics_missing": []}
        intent_analysis = {"summary": {"informational_percentage": 70, "transactional_percentage": 20}}
        
        try:
            # Generate each briefing component
            print(f"📋 Generating ING Content Briefing Components...")
            
            page_type = self._determine_page_type(state)
            print(f"   📄 Page Type: {page_type}")
            
            funnel_stage = self._determine_funnel_stage(state)
            print(f"   🎯 Funnel Stage: {funnel_stage}")
            
            notable_observations = self._generate_notable_observations(state)
            print(f"   👀 Notable Observations: {notable_observations[:100]}...")
            
            page_title = self._generate_page_title(focus_keyword, language)
            print(f"   📝 Page Title: {page_title}")
            
            meta_description = self._generate_meta_description(focus_keyword, secondary_keywords, language)
            print(f"   📋 Meta Description: {meta_description}")
            
            header_suggestions = self._generate_header_suggestions(state)
            print(f"   📑 H1 Suggestion: {header_suggestions.get('h1', 'None')}")
            print(f"   📑 H2 Count: {len(header_suggestions.get('h2', []))}")
            
            body_copy_outline = self._generate_body_copy_outline(state)
            print(f"   📖 Body Copy Outline: {len(body_copy_outline)} characters")
            print()
            
            self.log("Briefing generation completed")
            
            # Save to output files
            output_files = state.get("output_files", {})
            
            # Generate structured briefing data
            briefing_data = {
                "url": url,
                "serp_competitors": {
                    "1": competitor_urls[0] if len(competitor_urls) > 0 else "",
                    "2": competitor_urls[1] if len(competitor_urls) > 1 else "",
                    "3": competitor_urls[2] if len(competitor_urls) > 2 else ""
                },
                "notable_observations": notable_observations,
                "page_type": page_type,
                "funnel_stage": funnel_stage,
                "focus_keyword": focus_keyword,
                "secondary_keywords": secondary_keywords or [],
                "page_title_suggestion": page_title,
                "meta_description_suggestion": meta_description,
                "header_suggestions": header_suggestions,
                "body_copy_outline": body_copy_outline,
                "tone_of_voice": tone_of_voice,
                "language": language
            }
            
            output_files["briefing_data.json"] = json.dumps(briefing_data, indent=2, ensure_ascii=False)
            
            return {
                **state,
                "competitor_urls": competitor_urls,
                "page_type": page_type,
                "funnel_stage": funnel_stage,
                "notable_observations": notable_observations,
                "page_title_suggestion": page_title,
                "meta_description_suggestion": meta_description,
                "header_suggestions": header_suggestions,
                "body_copy_outline": body_copy_outline,
                "output_files": output_files,
                "current_step": "briefing_completed"
            }
            
        except Exception as e:
            error_msg = f"Briefing generation failed: {str(e)}"
            self.log(error_msg, "error")
            raise RuntimeError(error_msg) from e
    
    def _extract_competitor_urls(self, search_results: str) -> list:
        """Extract competitor URLs from search results"""
        import re
        
        if not search_results:
            return []
        
        # Extract URLs from search results using regex
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|[^\s<>"]+\.[a-z]{2,}'
        urls = re.findall(url_pattern, search_results, re.IGNORECASE)
        
        # Clean and filter URLs
        cleaned_urls = []
        for url in urls[:10]:  # Take first 10 potential URLs
            # Clean URL
            url = url.strip('.,;()')
            if not url.startswith('http'):
                url = 'https://' + url
            
            # Skip Google and other non-competitor URLs
            if any(domain in url.lower() for domain in ['google.', 'youtube.', 'facebook.', 'twitter.', 'linkedin.']):
                continue
                
            cleaned_urls.append(url)
            
            if len(cleaned_urls) >= 3:
                break
        
        return cleaned_urls
    
    def _determine_page_type(self, state: ContentOptimizationState) -> str:
        """Determine page type based on content and URL"""
        url = state.get("url", "")
        title = state.get("title", "")
        
        # Simple heuristics
        if "/blog/" in url or "/artikel/" in url:
            return "Blog artikel"
        elif "/product/" in url:
            return "Product pagina"
        elif any(word in title.lower() for word in ["gids", "guide", "how to", "hoe"]):
            return "Gids/Tutorial"
        elif any(word in url for word in ["/landing", "/lp/"]):
            return "Landing page"
        else:
            return "Informatie pagina"
    
    def _determine_funnel_stage(self, state: ContentOptimizationState) -> str:
        """Determine funnel stage based on available content analysis"""
        main_query = state.get("main_query") or ""
        title = state.get("title") or ""
        search_results = state.get("search_results") or ""
        
        # Combine all text for analysis
        content_text = f"{main_query} {title} {search_results}".lower()
        
        # Count intent indicators
        info_indicators = ["how", "what", "why", "guide", "hoe", "wat", "waarom", "gids", "uitleg"]
        trans_indicators = ["buy", "price", "cost", "kopen", "prijs", "kosten", "bestellen", "aanvragen"]
        commercial_indicators = ["best", "review", "compare", "beste", "vergelijk", "test"]
        
        info_count = sum(1 for word in info_indicators if word in content_text)
        trans_count = sum(1 for word in trans_indicators if word in content_text)
        commercial_count = sum(1 for word in commercial_indicators if word in content_text)
        
        if trans_count > info_count and trans_count > commercial_count:
            return "Beslissing (Decision)"
        elif commercial_count > info_count:
            return "Overweging (Consideration)"
        else:
            return "Bewustwording (Awareness)"
    
    def _generate_notable_observations(self, state: ContentOptimizationState) -> str:
        """Generate notable observations from available analysis"""
        search_results = state.get("search_results") or ""
        query_fanout_summary = state.get("query_fanout_summary") or ""
        ai_overview = state.get("ai_overview") or ""
        
        observations = []
        
        # Analyze search results patterns
        if search_results:
            # Basic pattern detection from search results
            if "how to" in search_results.lower():
                observations.append("Zoekresultaten tonen veel 'how-to' content - instructionele intent")
            if "best" in search_results.lower() or "top" in search_results.lower():
                observations.append("Competitie bevat veel vergelijkende content")
            if "review" in search_results.lower():
                observations.append("Reviews en evaluaties zijn belangrijk in dit landschap")
        
        # Analyze query fanout summary
        if query_fanout_summary:
            if len(query_fanout_summary) > 2000:
                observations.append("Uitgebreide competitieve analyse beschikbaar")
            if "seo" in query_fanout_summary.lower():
                observations.append("SEO optimalisatie is relevant voor concurrenten")
        
        # Analyze AI overview
        if ai_overview:
            if "step" in ai_overview.lower() or "stap" in ai_overview.lower():
                observations.append("Content vraagt om stapsgewijze uitleg")
            if "important" in ai_overview.lower() or "belangrijk" in ai_overview.lower():
                observations.append("AI overview benadrukt belangrijke aandachtspunten")
        
        return "\n".join(observations) if observations else "Gebaseerd op beschikbare zoekresultaten en competitieve analyse"
    
    def _generate_page_title(self, focus_keyword: str, language: str) -> str:
        """Generate optimized page title (max 60 chars)"""
        if not focus_keyword:
            return ""
        
        system_message = SystemMessage(content=f"""
        You are an SEO expert. Generate a compelling page title in {language}.
        
        Requirements:
        - Maximum 60 characters including spaces
        - Include the focus keyword naturally
        - Compelling and click-worthy
        - Follow SEO best practices
        
        Return ONLY the page title, nothing else.
        """)
        
        human_message = HumanMessage(content=f"""
        Focus keyword: {focus_keyword}
        Language: {language}
        
        Generate an optimized page title (max 60 chars).
        """)
        
        response = self.invoke_llm([system_message, human_message])
        return response.strip()[:60]
    
    def _generate_meta_description(self, focus_keyword: str, 
                                   secondary_keywords: list, 
                                   language: str) -> str:
        """Generate optimized meta description (max 155 chars)"""
        if not focus_keyword:
            return ""
        
        system_message = SystemMessage(content=f"""
        You are an SEO expert. Generate a compelling meta description in {language}.
        
        Requirements:
        - Maximum 155 characters including spaces
        - Include focus keyword
        - Include 1-2 secondary keywords if possible
        - Include a call-to-action (Ontdek, Bekijk, Lees meer, etc.)
        - Compelling and encourages clicks
        
        Return ONLY the meta description, nothing else.
        """)
        
        human_message = HumanMessage(content=f"""
        Focus keyword: {focus_keyword}
        Secondary keywords: {', '.join(secondary_keywords) if secondary_keywords else "None"}
        Language: {language}
        
        Generate an optimized meta description (max 155 chars).
        """)
        
        response = self.invoke_llm([system_message, human_message])
        return response.strip()[:155]
    
    def _generate_header_suggestions(self, state: ContentOptimizationState) -> dict:
        """Generate H1, H2, H3 suggestions"""
        focus_keyword = state.get("focus_keyword") or state.get("main_query")
        search_results = state.get("search_results") or ""
        query_fanout_summary = state.get("query_fanout_summary") or ""
        language = state.get("language", "nl")
        
        system_message = SystemMessage(content=f"""
        You are a content strategist. Generate header structure in {language}.
        
        Create:
        - 1 H1 heading (includes focus keyword naturally)
        - 5-8 H2 headings (main sections)
        - 2-3 H3 headings for each H2 (subsections)
        
        Base suggestions on search results and competitive analysis.
        
        Return as JSON:
        {{
            "h1": "Main heading",
            "h2": ["Section 1", "Section 2", ...],
            "h3": {{
                "Section 1": ["Subsection 1.1", "Subsection 1.2"],
                "Section 2": ["Subsection 2.1", "Subsection 2.2"]
            }}
        }}
        """)
        
        context = f"""
        Focus keyword: {focus_keyword}
        Language: {language}
        
        Search results analysis:
        {search_results[:1000] if search_results else "No search results available"}
        
        Query fanout summary:
        {query_fanout_summary[:1000] if query_fanout_summary else "No summary available"}
        
        Generate header structure.
        """
        
        response = self.invoke_llm([system_message, HumanMessage(content=context)])
        
        try:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(response)
        except:
            return {
                "h1": focus_keyword or "Header suggestion failed",
                "h2": ["Inleiding", "Hoofdpunten", "Voordelen", "Implementatie", "Conclusie"],
                "h3": {
                    "Hoofdpunten": ["Punt 1", "Punt 2", "Punt 3"],
                    "Voordelen": ["Voordeel 1", "Voordeel 2"]
                }
            }
    
    def _generate_body_copy_outline(self, state: ContentOptimizationState) -> str:
        """Generate body copy outline with keyword integration instructions"""
        focus_keyword = state.get("focus_keyword") or state.get("main_query")
        secondary_keywords = state.get("secondary_keywords", [])
        search_results = state.get("search_results") or ""
        query_fanout_summary = state.get("query_fanout_summary") or ""
        language = state.get("language", "nl")
        
        system_message = SystemMessage(content=f"""
        You are a content strategist. Create a body copy outline in {language}.
        
        The outline should:
        - Specify where to naturally integrate focus keyword (3+ times)
        - Specify where to integrate secondary keywords
        - Reference key topics from competitive analysis
        - Provide writing guidance for each major section
        - Be specific and actionable
        
        Write in {language}.
        """)
        
        context = f"""
        Focus keyword: {focus_keyword}
        Secondary keywords: {', '.join(secondary_keywords) if secondary_keywords else "None"}
        
        Search results insights:
        {search_results[:1000] if search_results else "No search results available"}
        
        Query fanout summary:
        {query_fanout_summary[:1000] if query_fanout_summary else "No summary available"}
        
        Create a body copy outline with specific keyword integration instructions.
        """
        
        response = self.invoke_llm([system_message, HumanMessage(content=context)])
        return response.strip()

def briefing_generator_node(state: ContentOptimizationState) -> ContentOptimizationState:
    agent = BriefingGeneratorAgent()
    return agent.execute(state)