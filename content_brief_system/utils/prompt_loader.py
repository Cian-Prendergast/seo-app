import os
from typing import Dict, Any

class PromptLoader:
    """Simple utility to load and format prompt templates from TXT files"""
    
    def __init__(self, prompts_directory: str):
        self.prompts_dir = prompts_directory
    
    def load(self, filename: str, **kwargs) -> str:
        """
        Load a prompt file and substitute variables
        
        Args:
            filename: Name of the prompt file (e.g., 'serp_analyzer.txt')
            **kwargs: Variables to substitute in the prompt template
            
        Returns:
            Formatted prompt string with variables substituted
        """
        file_path = os.path.join(self.prompts_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
        # Read the prompt template
        with open(file_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Substitute variables using string formatting
        try:
            formatted_prompt = template.format(**kwargs)
            return formatted_prompt
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Missing required variable '{missing_var}' for prompt '{filename}'")
    
    def list_prompts(self) -> list:
        """List all available prompt files"""
        if not os.path.exists(self.prompts_dir):
            return []
        
        return [f for f in os.listdir(self.prompts_dir) if f.endswith('.txt')]
    
    def validate_variables(self, filename: str, variables: Dict[str, Any]) -> list:
        """
        Check which variables are required but missing for a prompt
        
        Returns:
            List of missing variable names
        """
        file_path = os.path.join(self.prompts_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Extract variable names from template (basic implementation)
        import re
        # Find all {variable_name} patterns
        pattern = r'\{([^}]+)\}'
        required_vars = set(re.findall(pattern, template))
        provided_vars = set(variables.keys())
        
        missing_vars = required_vars - provided_vars
        return list(missing_vars)