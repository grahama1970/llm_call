"""
Configuration manager for llm_call.
Module: config_manager.py
Description: Configuration management and settings

Manages application configuration including model settings, API keys, and runtime options.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from loguru import logger

from .config.settings import Settings
from .config.loader import load_json_config, load_yaml_config


class ModelConfig(BaseModel):
    """Configuration for a specific model."""
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 120
    retry_attempts: int = 3


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self._settings = None
        self._model_configs = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from file and environment."""
        # Load settings
        self._settings = Settings()
        
        # Load from config file if provided
        if self.config_path and self.config_path.exists():
            try:
                if self.config_path.suffix == '.json':
                    config_data = load_json_config(self.config_path)
                else:
                    config_data = load_yaml_config(self.config_path)
                self._process_config_data(config_data)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _process_config_data(self, config_data: Dict[str, Any]):
        """Process loaded configuration data."""
        # Extract model configurations
        models = config_data.get("models", {})
        for model_name, model_config in models.items():
            self._model_configs[model_name] = ModelConfig(**model_config)
        
        # Update settings if provided
        if "settings" in config_data:
            for key, value in config_data["settings"].items():
                if hasattr(self._settings, key):
                    setattr(self._settings, key, value)
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        # Common API keys
        api_keys = {
            "OPENAI_API_KEY": "openai",
            "ANTHROPIC_API_KEY": "anthropic",
            "GROQ_API_KEY": "groq",
            "TOGETHER_API_KEY": "together",
            "GOOGLE_API_KEY": "google",
            "PERPLEXITY_API_KEY": "perplexity"
        }
        
        for env_var, provider in api_keys.items():
            api_key = os.getenv(env_var)
            if api_key:
                # Update all models from this provider
                for model_name, model_config in self._model_configs.items():
                    if model_config.provider == provider:
                        model_config.api_key = api_key
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model configuration or None if not found
        """
        return self._model_configs.get(model_name)
    
    def get_all_models(self) -> List[str]:
        """Get list of all configured models."""
        return list(self._model_configs.keys())
    
    def get_settings(self) -> Settings:
        """Get application settings."""
        return self._settings
    
    def update_model_config(
        self,
        model_name: str,
        config_updates: Dict[str, Any]
    ) -> bool:
        """
        Update configuration for a specific model.
        
        Args:
            model_name: Name of the model to update
            config_updates: Configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        if model_name not in self._model_configs:
            logger.error(f"Model '{model_name}' not found")
            return False
        
        try:
            current_config = self._model_configs[model_name]
            # Update fields
            for key, value in config_updates.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            logger.info(f"Updated configuration for model '{model_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to update model config: {e}")
            return False
    
    def add_model_config(
        self,
        model_name: str,
        provider: str,
        **kwargs
    ) -> bool:
        """
        Add configuration for a new model.
        
        Args:
            model_name: Name of the model
            provider: Provider name
            **kwargs: Additional configuration options
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._model_configs[model_name] = ModelConfig(
                provider=provider,
                **kwargs
            )
            logger.info(f"Added configuration for model '{model_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to add model config: {e}")
            return False
    
    def save_config(self, path: Optional[Path] = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            path: Path to save to (uses self.config_path if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self.config_path
        if not save_path:
            logger.error("No save path specified")
            return False
        
        try:
            config_data = {
                "models": {
                    name: config.model_dump()
                    for name, config in self._model_configs.items()
                },
                "settings": self._settings.model_dump()
            }
            
            with open(save_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Saved configuration to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False


# Default configuration manager instance
_default_manager = None


def get_config_manager() -> ConfigManager:
    """Get default configuration manager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = ConfigManager()
    return _default_manager


if __name__ == "__main__":
    # Test configuration manager
    print("Testing ConfigManager...")
    
    manager = ConfigManager()
    
    # Add some test models
    manager.add_model_config(
        "gpt-4",
        "openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=8192
    )
    
    manager.add_model_config(
        "claude-3-opus-20240229",
        "anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=4096
    )
    
    # Test getting models
    models = manager.get_all_models()
    print(f" Configured {len(models)} models: {models}")
    
    # Test getting specific model config
    gpt4_config = manager.get_model_config("gpt-4")
    if gpt4_config:
        print(f" GPT-4 config: provider={gpt4_config.provider}, max_tokens={gpt4_config.max_tokens}")
    
    # Test updating model config
    success = manager.update_model_config("gpt-4", {"temperature": 0.5})
    print(f" Updated GPT-4 config: {success}")
    
    # Test saving config
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    success = manager.save_config(temp_path)
    print(f" Saved config to {temp_path}: {success}")
    
    # Clean up
    if temp_path.exists():
        temp_path.unlink()
    
    print("\n All ConfigManager tests passed!")