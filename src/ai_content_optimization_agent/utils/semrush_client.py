import os
import requests
from typing import Dict, List, Optional

class SEMrushClient:
    """SEMrush API Client"""
    
    def __init__(self):
        self.api_key = os.getenv("SEMRUSH_API_KEY")  # Optional
        self.base_url = "https://api.semrush.com"
    
    def is_available(self) -> bool:
        """Check if SEMrush API is configured"""
        return bool(self.api_key)
    
    def get_keyword_data(self, keyword: str, database: str = "us") -> Optional[Dict]:
        """
        Get keyword volume, difficulty, CPC, etc.
        
        Returns:
            {
                "keyword": "business loans",
                "search_volume": 12000,
                "keyword_difficulty": 75,
                "cpc": 15.50,
                "competition": "high"
            }
        """
        if not self.is_available():
            return None
        
        try:
            params = {
                "type": "phrase_this",
                "key": self.api_key,
                "phrase": keyword,
                "database": database,
                "export_columns": "Ph,Nq,Cp,Co,Kd"
            }
            
            response = requests.get(
                f"{self.base_url}/",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse CSV response
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            headers = lines[0].split(';')
            values = lines[1].split(';')
            
            return {
                "keyword": keyword,
                "search_volume": int(values[1]) if len(values) > 1 else 0,
                "cpc": float(values[2]) if len(values) > 2 else 0.0,
                "competition": float(values[3]) if len(values) > 3 else 0.0,
                "keyword_difficulty": int(values[4]) if len(values) > 4 else 0
            }
            
        except Exception as e:
            print(f"SEMrush API error: {e}")
            return None
    
    def get_domain_ranking(self, domain: str, keyword: str) -> Optional[Dict]:
        """Get domain's ranking for specific keyword"""
        if not self.is_available():
            return None
        
        try:
            params = {
                "type": "domain_ranks",
                "key": self.api_key,
                "display_limit": 10,
                "export_columns": "Dn,Rk,Or,Ot,Oc,Ad",
                "domain": domain,
                "display_filter": f"+|Ph|Co|{keyword}"
            }
            
            response = requests.get(f"{self.base_url}/", params=params, timeout=30)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            values = lines[1].split(';')
            
            return {
                "domain": domain,
                "keyword": keyword,
                "rank": int(values[1]) if len(values) > 1 else None,
                "organic_traffic": int(values[2]) if len(values) > 2 else 0
            }
            
        except Exception as e:
            print(f"SEMrush ranking error: {e}")
            return None