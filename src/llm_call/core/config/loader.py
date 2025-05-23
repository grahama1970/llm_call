"""
Configuration loader for llm_call package.

This module loads configuration from environment variables and configuration files,
then validates and returns properly typed settings objects.

Links:
- python-dotenv documentation: https://github.com/theskumar/python-dotenv
- PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation

Sample usage:
    from llm_call.core.config.loader import load_configuration
    config = load_configuration()

Expected output:
    Settings object with all configuration loaded and validated
"""

import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from loguru import logger

from llm_call.core.config.settings import Settings


def find_config_file(config_name: str = "config") -> Optional[Path]:
    """
    Find configuration file in standard locations.
    
    Searches for config.yml, config.yaml, or config.json in:
    1. Current directory
    2. Project root
    3. src/llm_call/config/
    
    Args:
        config_name: Base name of config file (without extension)
    
    Returns:
        Path to config file if found, None otherwise
    """
    extensions = [".yml", ".yaml", ".json"]
    search_paths = [
        Path.cwd(),
        Path.cwd().parent,
        Path.cwd().parent.parent,
        Path(__file__).parent.parent.parent.parent,  # Project root
        Path(__file__).parent,  # config directory
    ]
    
    for path in search_paths:
        for ext in extensions:
            config_path = path / f"{config_name}{ext}"
            if config_path.exists():
                logger.debug(f"Found config file: {config_path}")
                return config_path
    
    return None


def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to load YAML config from {file_path}: {e}")
        return {}


def load_json_config(file_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON config from {file_path}: {e}")
        return {}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two configuration dictionaries.
    
    Args:
        base: Base configuration
        override: Configuration to override base values
    
    Returns:
        Merged configuration
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def load_configuration(
    env_file: Optional[str] = None,
    config_file: Optional[str] = None
) -> Settings:
    """
    Load configuration from environment and files.
    
    Loading order (later overrides earlier):
    1. Default values from Settings models
    2. .env file (if exists)
    3. Environment variables
    4. Configuration file (YAML/JSON)
    
    Args:
        env_file: Path to .env file (defaults to finding .env in standard locations)
        config_file: Path to config file (defaults to finding config.yml/yaml/json)
    
    Returns:
        Validated Settings object
    """
    # Load .env file
    if env_file:
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    else:
        # Try to find .env file
        if load_dotenv():
            logger.info("Loaded .env file")
    
    # Start with empty config
    config_dict = {}
    
    # Load configuration file if specified or found
    if config_file:
        config_path = Path(config_file)
    else:
        config_path = find_config_file()
    
    if config_path and config_path.exists():
        if config_path.suffix in ['.yml', '.yaml']:
            file_config = load_yaml_config(config_path)
        elif config_path.suffix == '.json':
            file_config = load_json_config(config_path)
        else:
            logger.warning(f"Unknown config file type: {config_path}")
            file_config = {}
        
        if file_config:
            config_dict = merge_configs(config_dict, file_config)
            logger.info(f"Loaded configuration from {config_path}")
    
    # Apply environment variable overrides for specific settings
    env_overrides = {}
    
    # Claude proxy settings from env
    if os.getenv("CLAUDE_CLI_PATH"):
        env_overrides.setdefault("claude_proxy", {})["cli_path"] = os.getenv("CLAUDE_CLI_PATH")
    if os.getenv("CLAUDE_PROXY_PORT"):
        env_overrides.setdefault("claude_proxy", {})["port"] = int(os.getenv("CLAUDE_PROXY_PORT"))
    if os.getenv("CLAUDE_PROXY_HOST"):
        env_overrides.setdefault("claude_proxy", {})["host"] = os.getenv("CLAUDE_PROXY_HOST")
    
    # Logging settings from env
    if os.getenv("LOG_LEVEL"):
        env_overrides["log_level"] = os.getenv("LOG_LEVEL")
    if os.getenv("LOG_FILE"):
        env_overrides["log_file"] = os.getenv("LOG_FILE")
    
    # Merge env overrides
    if env_overrides:
        config_dict = merge_configs(config_dict, env_overrides)
    
    # Create and validate settings
    try:
        settings = Settings(**config_dict)
        logger.success("Configuration loaded and validated successfully")
        return settings
    except Exception as e:
        logger.error(f"Failed to validate configuration: {e}")
        # Return default settings as fallback
        logger.warning("Using default settings as fallback")
        return Settings()


# Test function
if __name__ == "__main__":
    import sys
    
    logger.info("Testing configuration loader...")
    
    try:
        # Test 1: Load default configuration
        config = load_configuration()
        assert config.claude_proxy.port == 8001
        logger.success("✅ Default configuration loaded")
        
        # Test 2: Test with environment variable
        os.environ["CLAUDE_PROXY_PORT"] = "8002"
        os.environ["LOG_LEVEL"] = "DEBUG"
        config2 = load_configuration()
        assert config2.claude_proxy.port == 8002
        assert config2.log_level == "DEBUG"
        logger.success("✅ Environment variable override works")
        
        # Test 3: Create a test config file
        test_config = {
            "llm": {
                "default_model": "gpt-4",
                "default_temperature": 0.5
            },
            "claude_proxy": {
                "port": 8003
            }
        }
        
        test_config_path = Path("test_config.json")
        with open(test_config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Clear the env var that was set earlier
        os.environ.pop("CLAUDE_PROXY_PORT", None)
        
        config3 = load_configuration(config_file=str(test_config_path))
        assert config3.llm.default_model == "gpt-4"
        assert config3.llm.default_temperature == 0.5
        assert config3.claude_proxy.port == 8003
        logger.success("✅ Config file loading works")
        
        # Clean up
        test_config_path.unlink()
        
        logger.success("✅ All configuration loader tests passed")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Configuration loader test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)