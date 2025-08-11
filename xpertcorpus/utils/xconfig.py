"""
Config for XpertCorpus.

@author: rookielittleblack
@date:   2025-08-11
"""
import os
import yaml

from xpertcorpus.utils.xlogger import xlogger


class XConfigLoader:
    """Config loader for CorpusFlow."""
    
    def __init__(self, config_path="xpertcorpus/config/config.yaml"):
        """
        Initialize the config loader.
        
        Args:
            config_path: config file path, default is xpertcorpus/config/config.yaml
        """
        self.config_path = config_path
        self.config = None
        self.load_config()
    
    def load_config(self):
        """Load the config file."""
        try:
            if not os.path.exists(self.config_path):
                xlogger.error(f"Config file not found: {self.config_path}")
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            #xlogger.info(f"Successfully loaded config file: {self.config_path}")
            return self.config
        except Exception as e:
            xlogger.error(f"Failed to load config file: {str(e)}")
            raise
    
    def get_llm_model_config(self):
        """Get the config of the LLM model."""
        return self.config.get("llm_model", {})
    
    def get_vision_model_config(self):
        """Get the config of the vision model."""
        return self.config.get("vision_model", {})
    
    def get_embedding_model_config(self):
        """Get the config of the embedding model."""
        return self.config.get("embedding_model", {})
    
    def get_rarank_model_config(self):
        """Get the config of the rerank model."""
        return self.config.get("rarank_model", {})


# Run as a script to check the functions: `python -m xpertcorpus.utils.xconfig`
if __name__ == "__main__":
    # Test code
    config_loader = XConfigLoader()
    xlogger.info(config_loader.get_llm_model_config())
    xlogger.info(config_loader.get_vision_model_config())
    xlogger.info(config_loader.get_embedding_model_config())
    xlogger.info(config_loader.get_rarank_model_config())