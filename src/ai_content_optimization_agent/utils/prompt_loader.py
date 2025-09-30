import os
from pathlib import Path
from typing import Dict

class PromptLoader:
    """Utility class to load prompts from text files"""
    
    def __init__(self, prompts_dir: str = None):
        """
        Initialize the PromptLoader
        
        Args:
            prompts_dir: Path to prompts directory. If None, uses default location.
        """
        if prompts_dir is None:
            # Default to prompts/ directory relative to this file
            base_dir = Path(__file__).parent.parent
            self.prompts_dir = base_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # Cache loaded prompts to avoid repeated file I/O
        self._cache: Dict[str, str] = {}
    
    def load(self, prompt_name: str) -> str:
        """
        Load a prompt from a text file
        
        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            
        Returns:
            The prompt text as a string
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        # Check cache first
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        # Load from file
        file_path = self.prompts_dir / f"{prompt_name}.txt"
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {file_path}\n"
                f"Expected location: {file_path.absolute()}"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read().strip()
        
        # Cache the result
        self._cache[prompt_name] = prompt_text
        
        return prompt_text
    
    def format(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format a prompt with variables
        
        Args:
            prompt_name: Name of the prompt file
            **kwargs: Variables to format into the prompt using .format()
            
        Returns:
            The formatted prompt text
        """
        prompt_text = self.load(prompt_name)
        return prompt_text.format(**kwargs)
    
    def clear_cache(self):
        """Clear the prompt cache (useful for development/testing)"""
        self._cache.clear()


# Global instance for convenience
_default_loader = None

def get_loader() -> PromptLoader:
    """Get the default PromptLoader instance"""
    global _default_loader
    if _default_loader is None:
        _default_loader = PromptLoader()
    return _default_loader


def load_prompt(prompt_name: str) -> str:
    """Convenience function to load a prompt using the default loader"""
    return get_loader().load(prompt_name)


def format_prompt(prompt_name: str, **kwargs) -> str:
    """Convenience function to load and format a prompt"""
    return get_loader().format(prompt_name, **kwargs)