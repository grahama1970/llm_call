"""
Configuration settings models for llm_call package.

This module defines Pydantic models for type-safe configuration management.
Settings are loaded from environment variables and configuration files.

Links:
- Pydantic documentation: https://docs.pydantic.dev/

Sample usage:
    from llm_call.core.config.settings import LLMSettings, ClaudeProxySettings
    settings = LLMSettings(model="gpt-4", temperature=0.7)

Expected output:
    Validated configuration objects
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pathlib import Path


class RetrySettings(BaseModel):
    """Retry configuration settings."""
    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_factor: float = Field(default=2.0, ge=1.0, le=5.0)
    initial_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    max_delay: float = Field(default=60.0, ge=1.0, le=300.0)
    debug_mode: bool = Field(default=False)
    enable_cache: bool = Field(default=True)
    
    model_config = ConfigDict(extra="forbid")


class ClaudeProxySettings(BaseModel):
    """Claude CLI proxy server settings."""
    # From POC: CLAUDE_CLI_PATH, POC_TARGET_DIR, POC_SERVER_HOST, POC_SERVER_PORT
    cli_path: str = Field(default="/home/graham/.nvm/versions/node/v22.15.0/bin/claude")
    workspace_dir: Path = Field(default_factory=lambda: Path.home() / ".claude_workspace")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=3010)  # Match the running POC server
    proxy_url: str = Field(default="http://127.0.0.1:3010/v1/chat/completions")
    default_model_label: str = Field(default="max/poc-claude-default")
    
    @property
    def base_url(self) -> str:
        """Get base URL for proxy server."""
        return f"http://{self.host}:{self.port}"
    
    @field_validator("cli_path")
    def validate_cli_path(cls, v):
        """Validate Claude CLI path exists."""
        if not Path(v).exists():
            # Log warning but don't fail - server will check at runtime
            import warnings
            warnings.warn(f"Claude CLI not found at {v}")
        return v
    
    @field_validator("workspace_dir")
    def ensure_workspace_exists(cls, v):
        """Ensure workspace directory exists."""
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    model_config = ConfigDict(extra="forbid")


class VertexAISettings(BaseModel):
    """Vertex AI configuration settings."""
    project: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    credentials_path: Optional[str] = Field(default=None)
    
    @field_validator("project", mode="before")
    def get_project(cls, v):
        """Get project from various env vars."""
        if v:
            return v
        return os.getenv("LITELLM_VERTEX_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
    
    @field_validator("location", mode="before")
    def get_location(cls, v):
        """Get location from various env vars."""
        if v:
            return v
        return os.getenv("LITELLM_VERTEX_LOCATION") or os.getenv("GOOGLE_CLOUD_REGION") or "us-central1"
    
    model_config = ConfigDict(extra="forbid")


class OpenAISettings(BaseModel):
    """OpenAI configuration settings."""
    api_key: Optional[str] = Field(default=None)
    api_base: Optional[str] = Field(default=None)
    organization: Optional[str] = Field(default=None)
    
    model_config = ConfigDict(extra="forbid")


class LLMSettings(BaseModel):
    """General LLM configuration settings."""
    default_model: str = Field(default="gpt-3.5-turbo")
    default_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=250, ge=1, le=8192)
    timeout: float = Field(default=120.0, ge=10.0, le=600.0)
    
    # Multimodal settings from POC
    default_image_directory: Optional[Path] = Field(default=None)
    max_image_size_kb: int = Field(default=500, ge=100, le=5000)
    
    # JSON mode settings
    json_mode_instruction: str = Field(
        default="You MUST respond with a valid JSON object. Do not include any text outside of the JSON structure."
    )
    
    model_config = ConfigDict(extra="forbid")


class APISettings(BaseModel):
    """API server configuration settings."""
    title: str = Field(default="LLM Call API")
    version: str = Field(default="1.0.0")
    description: str = Field(default="Unified LLM API with Claude CLI proxy support")
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    
    model_config = ConfigDict(extra="forbid")


class Settings(BaseModel):
    """Main settings container."""
    llm: LLMSettings = Field(default_factory=LLMSettings)
    retry: RetrySettings = Field(default_factory=RetrySettings)
    claude_proxy: ClaudeProxySettings = Field(default_factory=ClaudeProxySettings)
    vertex_ai: VertexAISettings = Field(default_factory=VertexAISettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    api: APISettings = Field(default_factory=APISettings)
    
    # Logging settings
    log_level: str = Field(default="INFO")
    log_file: Optional[str] = Field(default=None)
    
    model_config = ConfigDict(extra="forbid")


# Test function
if __name__ == "__main__":
    from loguru import logger
    import sys
    
    logger.info("Testing settings models...")
    
    try:
        # Test basic settings creation
        settings = Settings()
        logger.success(f"✅ Created default settings")
        
        # Test Claude proxy settings
        assert settings.claude_proxy.port == 8001
        assert settings.claude_proxy.host == "127.0.0.1"
        logger.success(f"✅ Claude proxy settings: {settings.claude_proxy.host}:{settings.claude_proxy.port}")
        
        # Test retry settings
        assert settings.retry.max_attempts == 3
        assert settings.retry.backoff_factor == 2.0
        logger.success(f"✅ Retry settings: max_attempts={settings.retry.max_attempts}")
        
        # Test LLM settings
        assert settings.llm.default_temperature == 0.1
        assert settings.llm.default_max_tokens == 250
        logger.success(f"✅ LLM settings: temp={settings.llm.default_temperature}, max_tokens={settings.llm.default_max_tokens}")
        
        # Test custom settings
        custom_settings = Settings(
            claude_proxy=ClaudeProxySettings(port=8002),
            log_level="DEBUG"
        )
        assert custom_settings.claude_proxy.port == 8002
        assert custom_settings.log_level == "DEBUG"
        logger.success(f"✅ Custom settings work")
        
        logger.success("✅ All settings tests passed")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Settings test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)