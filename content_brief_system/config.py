import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration - NO hardcoded values"""
    
    # API Keys - Support both OpenAI and Gemini
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Bright Data SERP API
    BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
    BRIGHT_DATA_ZONE = os.getenv("BRIGHT_DATA_ZONE")
    
    # Model settings
    MODEL = os.getenv("MODEL", "gemini-2.0-flash-exp")  # Default to Gemini
    
    # Paths
    PROMPTS_DIR = "prompts"
    BRAND_GUIDELINES_FILE = "brand_guidelines/ing_tone_of_voice.txt"
    OUTPUT_DIR = "output"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        # Need Gemini for LLM
        if not cls.GEMINI_API_KEY:
            raise EnvironmentError("❌ GEMINI_API_KEY must be set in .env file")
        
        # Need Bright Data for SERP
        if not cls.BRIGHT_DATA_API_KEY:
            raise EnvironmentError("❌ BRIGHT_DATA_API_KEY not set in .env file")
        if not cls.BRIGHT_DATA_ZONE:
            raise EnvironmentError("❌ BRIGHT_DATA_ZONE not set in .env file")
    
    @classmethod
    def get_llm(cls):
        """Get Gemini LLM"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=cls.MODEL,
            google_api_key=cls.GEMINI_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )