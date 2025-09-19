from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging
from state import ContentOptimizationState

class BaseAgent(ABC):
    """Base class for all agents - replaces CrewAI Agent"""
    def __init__(self, name: str, model: Optional[str] = None, verbose: bool = True):
        self.name = name
        self.verbose = verbose
        self.model = model or os.getenv("MODEL", "gemini/gemini-2.5-flash")
        self.llm = ChatGoogleGenerativeAI(model=self.model)
        self.logger = logging.getLogger(f"agent.{name}")
    def log(self, message: str, level: str = "info"):
        if self.verbose:
            getattr(self.logger, level)(f"[{self.name}] {message}")
    @abstractmethod
    def execute(self, state: ContentOptimizationState) -> ContentOptimizationState:
        pass
    def invoke_llm(self, messages: List[Any], tools: Optional[List] = None) -> str:
        try:
            if tools:
                response = self.llm.invoke(messages, tools=tools)
            else:
                response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            self.log(f"LLM invocation failed: {str(e)}", "error")
            raise
