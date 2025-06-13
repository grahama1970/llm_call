# Bare Except Clauses Report

Generated: 2025-06-10 08:55:23

Total issues found: 312

## Summary Statistics
- Files with issues: 103
- Bare except clauses: 12
- Generic Exception handlers: 300

## Required Imports
- `import asyncio`
- `import sqlite3`
- `import subprocess`
- `import yaml`

## Issues by File

### src/llm_call/cli/main.py
Issues: 9

#### Line 222
**Current:** `except:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 215

**Context:**
```python
            content = str(response)
        
        if json_mode:
            try:
                parsed = json.loads(content)
                console.print(Panel(
                    Syntax(json.dumps(parsed, indent=2), "json"),
                    title="Response",
                    border_style="green"
                ))
except:
                console.print(Panel(content, title="Response", border_style="green"))
        else:
            console.print(Panel(content, title="Response", border_style="green"))
```

#### Line 227
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 174

**Context:**
```python
                console.print(Panel(
                    Syntax(json.dumps(parsed, indent=2), "json"),
                    title="Response",
                    border_style="green"
                ))
            except:
                console.print(Panel(content, title="Response", border_style="green"))
        else:
            console.print(Panel(content, title="Response", border_style="green"))
except Exception as e:
        logger.error(f"LLM request failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
```

#### Line 294
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 261

**Context:**
```python
                content = response.choices[0].message.content
            else:
                content = str(response)
            
            chat_history.append({"role": "assistant", "content": content})
            console.print(f"[bold magenta]Assistant:[/bold magenta] {content}")
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Chat interrupted.[/bold yellow]")
            break
except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command()
```

#### Line 348
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 318

**Context:**
```python
        # Display response
        if isinstance(response, dict):
            console.print(Panel(
                Syntax(json.dumps(response, indent=2), "json"),
                title="Response",
                border_style="green"
            ))
        else:
            console.print(Panel(str(response), title="Response", border_style="green"))
except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@app.command()
```

#### Line 384
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 364

**Context:**
```python
        console.print("[bold]Available Models:[/bold]")
        
        for provider_name, model_list in common_models.items():
            if provider and provider.lower() not in provider_name.lower():
                continue
                
            console.print(f"\n[bold cyan]{provider_name}:[/bold cyan]")
            for model in model_list:
                console.print(f"  • {model}")
except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
```

#### Line 524
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 505

**Context:**
```python
                    "optional": param.default != param.empty
                }
                
                if param.annotation != param.empty:
                    if param.annotation == int:
                        arg_config["type"] = "number"
                    elif param.annotation == bool:
                        arg_config["type"] = "boolean"
                
                slash_config["args"].append(arg_config)
except Exception as e:
            if verbose:
                console.print(f"[yellow]Warning: Could not parse signature for {cmd_name}: {e}[/yellow]")
        
        # Write command file
```

#### Line 823
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 765

**Context:**
```python
            }
            
        except subprocess.TimeoutExpired:
            return {
                "file": test_file.name,
                "success": False,
                "elapsed": timeout,
                "error": f"Timeout after {timeout}s",
                "output": ""
            }
except Exception as e:
            return {
                "file": test_file.name,
                "success": False,
                "elapsed": time.time() - start_time,
```

#### Line 1021
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 920

**Context:**
```python
            console.print(f"\n[dim]Model: {result.get('model', 'unknown')}[/dim]")
            console.print(f"[dim]Strategy: {result.get('strategy', 'unknown')}[/dim]")
            if 'total_chunks' in result:
                console.print(f"[dim]Total chunks: {result['total_chunks']}[/dim]")
            if 'total_tokens' in result:
                console.print(f"[dim]Total tokens: {result['total_tokens']}[/dim]")
            
            if output:
                console.print(f"\n[green]Summary saved to {output}[/green]")
except Exception as e:
        error_str = str(e).lower()
        
        # Check if this is an authentication error
        if any(auth_term in error_str for auth_term in ["jwt", "token", "auth", "credential", "forbidden", "unauthorized", "403", "401"]):
```

#### Line 1097
**Current:** `except:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 1087

**Context:**
```python
                try:
                    with open(f) as file:
                        lines = file.readlines()[:10]
                        for line in lines:
                            if "POC-" in line and ":" in line:
                                desc = line.split(":", 1)[1].strip()
                                console.print(f"  • {f.name} - {desc}")
                                break
                        else:
                            console.print(f"  • {f.name}")
except:
                    console.print(f"  • {f.name}")
        
        if poc_number is None:
            raise typer.Exit(0)
```

### src/llm_call/cli/slash_mcp_mixin.py
Issues: 1

#### Line 367
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 310

**Context:**
```python
                            typer.echo = original_echo
                    
                    except SystemExit as e:
                        # Commands might call sys.exit()
                        return {
                            "status": "success" if e.code == 0 else "error",
                            "output": "\n".join(captured_output),
                            "exit_code": e.code
                        }
except Exception as e:
                        return {
                            "status": "error",
                            "error": str(e),
                            "traceback": traceback.format_exc() if debug else None
```

### src/llm_call/core/api/claude_cli_executor.py
Issues: 5

#### Line 72
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 69

**Context:**
```python
    if not target_dir.is_dir():
        logger.error(f"[Claude Executor] Target directory not found: {target_dir}")
        return f"Target directory not found: {target_dir}"
    
    # Handle MCP configuration if provided
    mcp_file_path: Optional[Path] = None
    if mcp_config:
        try:
            mcp_file_path = write_mcp_config(target_dir, mcp_config)
            logger.info(f"[Claude Executor] Wrote MCP config with tools: {list(mcp_config.get('mcpServers', {}).keys())}")
except Exception as e:
            logger.error(f"[Claude Executor] Failed to write MCP config: {e}")
            return f"Failed to write MCP configuration: {e}"
    
    # Parse model name from max/ prefix if provided
```

#### Line 170
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 139

**Context:**
```python
                    break
                
                # Handle errors (from POC)
                elif data.get("type") == "result" and data.get("subtype") == "error":
                    logger.error(f"[Claude Executor] Claude CLI stream reported error: {data}")
                    final_result_content = f"Error from Claude CLI: {data.get('error', 'Unknown error')}"
                    break
                    
            except json.JSONDecodeError:
                logger.warning(f"[Claude Executor] Non-JSON line in stream: {stripped_line}")
except Exception as e:
                logger.error(f"[Claude Executor] Error processing streamed JSON: {e}")
        
        # If no result yet but we have accumulated text, use it (from POC)
        if final_result_content is None and full_response_text:
```

#### Line 207
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 119

**Context:**
```python
        logger.error("[Claude Executor] Claude process timed out")
        if process:
            process.kill()
            process.communicate()
        return "Claude process timed out."
    
    except FileNotFoundError:
        logger.error(f"[Claude Executor] Claude CLI executable not found at {claude_exe_path}")
        return f"Claude CLI not found at {claude_exe_path}"
except Exception as e:
        logger.exception(f"[Claude Executor] Unexpected error: {e}")
        return f"Unexpected server error: {e}"
    
    finally:
```

#### Line 258
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 245

**Context:**
```python
                system_prompt_content="You are a test assistant. Follow instructions exactly.",
                target_dir=settings.claude_proxy.workspace_dir,
                claude_exe_path=cli_path,
                timeout=30
            )
            
            if response and "test successful" in response.lower():
                logger.success(f" Claude CLI execution works: {response[:100]}...")
            else:
                all_validation_failures.append(f"Unexpected response: {response}")
except Exception as e:
            all_validation_failures.append(f"Execution test failed: {e}")
    else:
        logger.warning(f"⚠️ Skipping execution test - Claude CLI not found at {cli_path}")
        logger.info("This is expected in test environments without Claude CLI")
```

#### Line 277
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 266

**Context:**
```python
        response = execute_claude_cli(
            prompt="Test",
            system_prompt_content="Test",
            target_dir=settings.claude_proxy.workspace_dir,
            claude_exe_path=Path("/nonexistent/claude"),
            timeout=5
        )
        
        assert "Claude CLI not found" in response
        logger.success(" Missing executable error handling works")
except Exception as e:
        all_validation_failures.append(f"Error handling test failed: {e}")
    
    # Final validation result
    if all_validation_failures:
```

### src/llm_call/core/api/handlers.py
Issues: 2

#### Line 148
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 144

**Context:**
```python
    # Test the handler components
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Router is properly configured
    total_tests += 1
    try:
        assert len(router.routes) > 0
        assert any(route.path == "/v1/chat/completions" for route in router.routes)
        logger.success(" Router configured with chat completions endpoint")
except Exception as e:
        all_validation_failures.append(f"Router configuration failed: {e}")
    
    # Test 2: Configuration is accessible
    total_tests += 1
```

#### Line 157
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 153

**Context:**
```python
        logger.success(" Router configured with chat completions endpoint")
    except Exception as e:
        all_validation_failures.append(f"Router configuration failed: {e}")
    
    # Test 2: Configuration is accessible
    total_tests += 1
    try:
        assert settings.claude_proxy.cli_path
        assert settings.claude_proxy.workspace_dir
        logger.success(" Configuration accessible in handlers")
except Exception as e:
        all_validation_failures.append(f"Configuration access failed: {e}")
    
    # Final validation result
    if all_validation_failures:
```

### src/llm_call/core/api/mcp_handler.py
Issues: 2

#### Line 107
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 99

**Context:**
```python
    mcp_json_path = target_dir / ".mcp.json"
    
    try:
        with open(mcp_json_path, 'w', encoding='utf-8') as f:
            json.dump(config_to_write, f, indent=2)
        
        tools_list = list(config_to_write.get('mcpServers', {}).keys())
        logger.info(f"Wrote MCP config to '{mcp_json_path}' with tools: {tools_list}")
        return mcp_json_path
except Exception as e:
        logger.error(f"Failed to write MCP config to '{mcp_json_path}': {e}")
        raise IOError(f"Could not write MCP configuration: {e}")
```

#### Line 123
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 119

**Context:**
```python
    """
    Remove MCP configuration file.
    
    Args:
        mcp_json_path: Path to .mcp.json file to remove
    """
    try:
        if mcp_json_path.exists():
            mcp_json_path.unlink()
            logger.info(f"Removed MCP config from '{mcp_json_path}'")
except Exception as e:
        logger.warning(f"Failed to remove MCP config '{mcp_json_path}': {e}")


def get_tool_config(tool_name: str) -> Optional[Dict[str, Any]]:
```

### src/llm_call/core/api/mcp_handler_enhanced.py
Issues: 1

#### Line 168
**Current:** `except Exception:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 164

**Context:**
```python
        self.temp_configs[temp_file.name] = True
        
        return temp_file.name
    
    def cleanup_temp_config(self, config_path: str):
        """Clean up temporary MCP config file"""
        try:
            if config_path in self.temp_configs:
                os.unlink(config_path)
                del self.temp_configs[config_path]
except Exception:
            pass  # Ignore cleanup errors
    
    def cleanup_all_temp_configs(self):
        """Clean up all temporary configs"""
```

### src/llm_call/core/api/mcp_handler_wrapper.py
Issues: 2

#### Line 119
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 114

**Context:**
```python
        """
        if server_name not in self._available_servers:
            logger.error(f"Server '{server_name}' not found")
            return False
        
        try:
            # Merge configurations
            self._available_servers[server_name].update(config)
            logger.info(f"Updated configuration for server '{server_name}'")
            return True
except Exception as e:
            logger.error(f"Failed to update server config: {e}")
            return False
    
    async def test_server(self, server_name: str) -> Dict[str, Any]:
```

#### Line 168
**Current:** `except Exception:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 166

**Context:**
```python
            "server": server_name,
            "description": server_config.get("description", ""),
            "version": server_config.get("version", "1.0.0")
        }
    
    def __del__(self):
        """Clean up any remaining temporary configs."""
        for config_path in self.temp_configs[:]:
            try:
                self.cleanup_temp_config(config_path)
except Exception:
                pass


if __name__ == "__main__":
```

### src/llm_call/core/caller.py
Issues: 7

#### Line 188
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 177

**Context:**
```python
                # Get validator from registry
                validator_instance = get_validator(strategy_type, **strategy_params)
                
                # Handle AI validators that need LLM caller
                if hasattr(validator_instance, "set_llm_caller"):
                    validator_instance.set_llm_caller(make_llm_request)
                
                validation_strategies.append(validator_instance)
                logger.debug(f"Added validator: {strategy_type}")
except Exception as e:
                logger.error(f"Failed to load validator '{strategy_type}': {e}")
        
        # Get response format for validation and provider calls
        response_format = processed_config.get("response_format")
```

#### Line 234
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 142

**Context:**
```python
            validation_strategies=validation_strategies,
            config=retry_config,
            **api_params_cleaned
        )
        
        return response
        
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        return None
except Exception as e:
        logger.error(f"Unexpected error in make_llm_request: {type(e).__name__} - {e}")
        return None
```

#### Line 264
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 252

**Context:**
```python
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "test"}]
            }
            
            # We can't actually make the request without API keys/server
            # but we can test the preprocessing
            processed = _prepare_messages_and_params(test_config)
            assert "messages" in processed
            assert processed["model"] == "gpt-3.5-turbo"
            logger.success("Basic preprocessing works")
except Exception as e:
            all_validation_failures.append(f"Basic test failed: {e}")
        
        # Test 2: JSON mode preprocessing
        total_tests += 1
```

#### Line 284
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 269

**Context:**
```python
            }
            
            processed = _prepare_messages_and_params(test_config)
            
            # Should have added system message with JSON instruction
            assert len(processed["messages"]) > len(test_config["messages"])
            system_msg = next((m for m in processed["messages"] if m["role"] == "system"), None)
            assert system_msg is not None
            assert "JSON" in system_msg["content"]
            logger.success("JSON mode preprocessing works")
except Exception as e:
            all_validation_failures.append(f"JSON mode test failed: {e}")
        
        # Test 3: Multimodal processing for max/ models
        total_tests += 1
```

#### Line 306
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 289

**Context:**
```python
                        {"type": "image_url", "image_url": {"url": "test.jpg"}}
                    ]
                }]
            }
            
            processed = _prepare_messages_and_params(test_config)
            # Should process multimodal content normally
            assert "skip_claude_multimodal" not in processed
            assert processed["model"] == "max/test"
            logger.success("Multimodal processing for max/ models works")
except Exception as e:
            all_validation_failures.append(f"Multimodal processing test failed: {e}")
        
        # Test 4: Missing messages error
        total_tests += 1
```

#### Line 315
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 311

**Context:**
```python
            logger.success("Multimodal processing for max/ models works")
        except Exception as e:
            all_validation_failures.append(f"Multimodal processing test failed: {e}")
        
        # Test 4: Missing messages error
        total_tests += 1
        try:
            result = await make_llm_request({"model": "gpt-4"})
            assert result is None  # Should return None on error
            logger.success("Missing messages error handling works")
except Exception as e:
            all_validation_failures.append(f"Error handling test failed: {e}")
        
        # Test 5: Validation strategies selection
        total_tests += 1
```

#### Line 339
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 320

**Context:**
```python
            
            # For JSON request, should have both validators
            json_config = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "test"}],
                "response_format": {"type": "json_object"}
            }
            json_processed = _prepare_messages_and_params(json_config)
            
            logger.success("Validation strategy selection logic verified")
except Exception as e:
            all_validation_failures.append(f"Validation strategy test failed: {e}")
        
        return all_validation_failures, total_tests
```

### src/llm_call/core/config/loader.py
Issues: 4

#### Line 71
**Current:** `except Exception as e:`
**Suggested:** `except yaml.YAMLError:`
**Comment:** # YAML parsing failed

**Try block starts at line:** 68

**Context:**
```python
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
```

#### Line 81
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 78

**Context:**
```python
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
```

#### Line 185
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 181

**Context:**
```python
    
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
```

#### Line 242
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 198

**Context:**
```python
        assert config3.llm.default_temperature == 0.5
        assert config3.claude_proxy.port == 8003
        logger.success(" Config file loading works")
        
        # Clean up
        test_config_path.unlink()
        
        logger.success(" All configuration loader tests passed")
        sys.exit(0)
except Exception as e:
        logger.error(f" Configuration loader test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### src/llm_call/core/config/settings.py
Issues: 1

#### Line 188
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 156

**Context:**
```python
            claude_proxy=ClaudeProxySettings(port=8002),
            log_level="DEBUG"
        )
        assert custom_settings.claude_proxy.port == 8002
        assert custom_settings.log_level == "DEBUG"
        logger.success(f" Custom settings work")
        
        logger.success(" All settings tests passed")
        sys.exit(0)
except Exception as e:
        logger.error(f" Settings test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### src/llm_call/core/config_manager.py
Issues: 4

#### Line 59
**Current:** `except Exception as e:`
**Suggested:** `except yaml.YAMLError:`
**Comment:** # YAML parsing failed

**Try block starts at line:** 53

**Context:**
```python
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
```

#### Line 145
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 137

**Context:**
```python
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
```

#### Line 173
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 166

**Context:**
```python
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
```

#### Line 206
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 192

**Context:**
```python
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
```

### src/llm_call/core/conversation_manager.py
Issues: 1

#### Line 461
**Current:** `except Exception as e:`
**Suggested:** `except sqlite3.Error:`
**Comment:** # Database operation failed

**Try block starts at line:** 450

**Context:**
```python
            return ConversationManager(
                storage_backend="arango",
                arango_config={
                    "host": "localhost",
                    "port": 8529,
                    "username": "root",
                    "password": "openSesame",
                    "database": "llm_conversations"
                }
            )
except Exception as e:
            logger.warning(f"Failed to connect to ArangoDB: {e}. Falling back to SQLite.")
    
    # Default to SQLite
    return ConversationManager(storage_backend="sqlite")
```

### src/llm_call/core/debug.py
Issues: 1

#### Line 258
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 254

**Context:**
```python
        if debug_manager:
            trace = debug_manager.start_trace(
                strategy_name=getattr(self, "name", self.__class__.__name__),
                context={"response": str(response)[:100], **context}
            )
            
            try:
                result = func(self, response, context)
                debug_manager.end_trace(result)
                return result
except Exception as e:
                error_result = ValidationResult(
                    valid=False,
                    error=f"Exception: {str(e)}"
                )
```

### src/llm_call/core/providers/base_provider.py
Issues: 1

#### Line 89
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 85

**Context:**
```python
    
    # Test that we can create a concrete implementation
    class TestProvider(BaseLLMProvider):
        async def complete(self, messages, response_format=None, **kwargs):
            return {"test": "response"}
    
    try:
        provider = TestProvider()
        logger.success(" Can create concrete implementation")
        sys.exit(0)
except Exception as e:
        logger.error(f"L Failed to create concrete implementation: {e}")
        sys.exit(1)
```

### src/llm_call/core/providers/claude/claude_executor.py
Issues: 8

#### Line 171
**Current:** `except Exception as e_parse:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 134

**Context:**
```python
                        # For this PoC, we assume it's a terminal message for content.
                    
                    if not event_yielded: # Log other unhandled JSON structures
                         logger.debug(f"Other JSON object received: {data}")
                         yield {"type": "unhandled_json_event", "data": data}


                except json.JSONDecodeError:
                    logger.warning(f"Non-JSON line in stream or decode error: {stripped_line}")
                    yield {"type": "stream_parsing_error", "line": stripped_line}
except Exception as e_parse:
                    logger.error(f"Error processing streamed JSON line '{stripped_line}': {e_parse}")
                    yield {"type": "stream_processing_error", "line": stripped_line, "error": str(e_parse)}
            
            # After loop, communicate to get final stderr and ensure process termination
```

#### Line 194
**Current:** `except Exception as e_global:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 114

**Context:**
```python

        except subprocess.TimeoutExpired:
            logger.error("Claude subprocess timed out during communicate().")
            if process:
                process.kill()
                process.communicate() # Clean up pipes
            yield {"type": "final_result", "subtype": "error", "details": {"message": "Subprocess timed out"}, "raw_stderr": "Timeout during communicate()"}
        except FileNotFoundError as e_fnf: # For Popen itself
            logger.error(f"Failed to start Claude subprocess: {e_fnf}. Check claude_exe_path.")
            yield {"type": "final_result", "subtype": "error", "details": {"message": str(e_fnf), "reason": "executable_not_found"}, "raw_stderr": ""}
except Exception as e_global:
            logger.exception(f"An unexpected error occurred during Claude execution: {e_global}")
            if process and process.poll() is None:
                process.kill()
                process.communicate()
```

#### Line 244
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 220

**Context:**
```python
        else:
            all_validation_failures.append(f"Test 1.1 FAILED: Command mismatch. Expected: {expected_cmd_part}, Got: {cmd}")

        cmd_no_sys = construct_claude_command(test_exe_path, "Hi", pass_verbose_to_claude_cli=False)
        expected_cmd_no_sys = [str(test_exe_path), "-p", "Hi", "--output-format", "stream-json"]
        if cmd_no_sys == expected_cmd_no_sys:
            logger.info("Test 1.2 PASSED: Command constructed correctly without system prompt and no verbose.")
        else:
            all_validation_failures.append(f"Test 1.2 FAILED: Command mismatch. Expected: {expected_cmd_no_sys}, Got: {cmd_no_sys}")
except Exception as e:
        all_validation_failures.append(f"Test 1 FAILED: Unexpected exception: {e}")

    # Test 2: Simulation Execution and Event Yielding
    total_tests += 1
```

#### Line 300
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 274

**Context:**
```python
        if not final_result_event or final_result_event.get("content") != "Sim chunk 1 Sim chunk 2":
            all_validation_failures.append(f"Test 2.3 FAILED: Final result content mismatch. Got: {final_result_event}")
        else:
            logger.info("Test 2.3 PASSED: Correct final result event received.")

        if not any(e.get("type") == "subprocess_event" and e.get("event_type") == "exit" and e.get("code") == 0 for e in events_received):
            all_validation_failures.append("Test 2.4 FAILED: Did not receive 'subprocess_event exit' with code 0.")
        else:
            logger.info("Test 2.4 PASSED: Subprocess exit event with code 0 received.")
except Exception as e:
        all_validation_failures.append(f"Test 2 FAILED: Unexpected exception during simulation: {e}")
    finally:
        if dummy_target_dir.exists():
            try:
```

#### Line 309
**Current:** `except Exception as e_clean:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 304

**Context:**
```python

    except Exception as e:
        all_validation_failures.append(f"Test 2 FAILED: Unexpected exception during simulation: {e}")
    finally:
        if dummy_target_dir.exists():
            try:
                # Clean up dummy directory - be careful with rmtree
                import shutil
                shutil.rmtree(dummy_target_dir)
                logger.info(f"Cleaned up dummy target directory: {dummy_target_dir}")
except Exception as e_clean:
                logger.error(f"Error cleaning up dummy target directory: {e_clean}")
    
    # Test 3: Handling Executable Not Found
    total_tests += 1
```

#### Line 322
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 316

**Context:**
```python
    # Test 3: Handling Executable Not Found
    total_tests += 1
    logger.info("\nTest 3: Handling Executable Not Found")
    non_existent_exe = Path("./non_existent_claude_executable_for_test")
    try:
        cmd_fail = construct_claude_command(non_existent_exe, "test")
        # This should raise FileNotFoundError in construct_claude_command
        all_validation_failures.append("Test 3.1 FAILED: construct_claude_command did not raise FileNotFoundError for non-existent exe.")
    except FileNotFoundError:
        logger.info("Test 3.1 PASSED: construct_claude_command correctly raised FileNotFoundError.")
except Exception as e:
        all_validation_failures.append(f"Test 3.1 FAILED: Unexpected exception: {e}")

    events_fail_exe = []
    try:
```

#### Line 346
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 326

**Context:**
```python
        for event in execute_claude_task("val_exec_fail", fail_cmd_list, dummy_target_dir): # dummy_target_dir might be cleaned up, recreate if needed
            if not dummy_target_dir.exists(): dummy_target_dir.mkdir(exist_ok=True)
            events_fail_exe.append(event)
        
        final_error_event = next((e for e in events_fail_exe if e.get("type") == "final_result" and e.get("subtype") == "error"), None)
        if final_error_event and final_error_event.get("details", {}).get("reason") == "executable_not_found":
            logger.info("Test 3.2 PASSED: execute_claude_task yielded correct error for non-existent executable.")
        else:
            all_validation_failures.append(f"Test 3.2 FAILED: Incorrect or missing error event for non-existent exe. Got: {final_error_event}")
except Exception as e:
         all_validation_failures.append(f"Test 3.2 FAILED: Unexpected exception: {e}")
    finally:
        if dummy_target_dir.exists():
            try:
```

#### Line 353
**Current:** `except Exception: # nosec`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 350

**Context:**
```python
        else:
            all_validation_failures.append(f"Test 3.2 FAILED: Incorrect or missing error event for non-existent exe. Got: {final_error_event}")

    except Exception as e:
         all_validation_failures.append(f"Test 3.2 FAILED: Unexpected exception: {e}")
    finally:
        if dummy_target_dir.exists():
            try:
                import shutil
                shutil.rmtree(dummy_target_dir)
except Exception: # nosec
                pass


    # Final validation result
```

### src/llm_call/core/providers/claude/db_manager.py
Issues: 5

#### Line 249
**Current:** `except Exception as e:`
**Suggested:** `except sqlite3.Error:`
**Comment:** # Database operation failed

**Try block starts at line:** 236

**Context:**
```python
            all_validation_failures.append("Test 1.1 FAILED: create_database did not return a Connection object.")
        else:
            logger.info("Test 1.1 PASSED: Database connection established.")
            # Check if table exists
            cursor = conn_test.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='progress';")
            if cursor.fetchone() is None:
                all_validation_failures.append("Test 1.2 FAILED: 'progress' table not created.")
            else:
                logger.info("Test 1.2 PASSED: 'progress' table exists.")
except Exception as e:
        all_validation_failures.append(f"Test 1 FAILED: Unexpected exception during DB creation: {e}")
    finally:
        if conn_test:
            conn_test.close() # Close after this initial test
```

#### Line 287
**Current:** `except Exception as e:`
**Suggested:** `except sqlite3.Error:`
**Comment:** # Database operation failed

**Try block starts at line:** 264

**Context:**
```python
            cursor.execute("SELECT * FROM progress WHERE id = ?", (test_progress_id,))
            row = cursor.fetchone()
            if row is None:
                all_validation_failures.append("Test 2.1 FAILED: Record not inserted.")
            elif row[1] != "started":
                 all_validation_failures.append(f"Test 2.2 FAILED: Initial status is '{row[1]}', expected 'started'.")
            elif row[6] != sample_requester or row[7] != sample_responder:
                 all_validation_failures.append(f"Test 2.3 FAILED: Requester/Responder mismatch.")
            else:
                logger.info("Test 2 PASSED: Initial record inserted and basic fields verified.")
except Exception as e:
            all_validation_failures.append(f"Test 2 FAILED: Unexpected exception during record insertion: {e}")
    else:
        all_validation_failures.append("Test 2 SKIPPED: DB connection not available.")
```

#### Line 329
**Current:** `except Exception as e:`
**Suggested:** `except sqlite3.Error:`
**Comment:** # Database operation failed

**Try block starts at line:** 297

**Context:**
```python
                all_validation_failures.append(f"Test 3.B FAILED: Second update incorrect. Status: {row[0] if row else 'N/A'}, Content: {row[1] if row else 'N/A'}, Chunks: {row[2] if row else 'N/A'}")

            update_task_progress(conn_test, test_progress_id, "complete") # Update status only
            cursor.execute("SELECT status, chunk_count FROM progress WHERE id = ?", (test_progress_id,))
            row = cursor.fetchone()
            if row and row[0] == "complete" and row[1] == 2: # Chunk count should remain 2
                 logger.info("Test 3.C PASSED: Status-only update successful, chunk_count preserved.")
            else:
                all_validation_failures.append(f"Test 3.C FAILED: Status-only update incorrect. Status: {row[0] if row else 'N/A'}, Chunks: {row[1] if row else 'N/A'}")
except Exception as e:
            all_validation_failures.append(f"Test 3 FAILED: Unexpected exception during progress update: {e}")
    else:
        all_validation_failures.append("Test 3 SKIPPED: DB connection not available.")
```

#### Line 357
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 338

**Context:**
```python
                 all_validation_failures.append(f"Test 4.4 FAILED: Retrieved requester mismatch.")
            else:
                logger.info(f"Test 4 PASSED: get_task_details retrieved correct data: {details.get('status')}, Chunks: {details.get('chunk_count')}")
            
            non_existent_details = get_task_details(conn_test, "non_existent_id")
            if non_existent_details is not None:
                all_validation_failures.append("Test 4.5 FAILED: get_task_details returned data for non-existent ID.")
            else:
                logger.info("Test 4.5 PASSED: get_task_details returned None for non-existent ID.")
except Exception as e:
            all_validation_failures.append(f"Test 4 FAILED: Unexpected exception: {e}")
    else:
        all_validation_failures.append("Test 4 SKIPPED: DB connection not available.")
```

#### Line 370
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 367

**Context:**
```python
        all_validation_failures.append("Test 4 SKIPPED: DB connection not available.")


    # Cleanup
    if conn_test:
        conn_test.close()
    if test_db_path.exists():
        try:
            test_db_path.unlink()
            logger.info(f"Cleaned up test database: {test_db_path}")
except Exception as e:
            logger.error(f"Could not clean up test database {test_db_path}: {e}")


    # Final validation result
```

### src/llm_call/core/providers/claude/focused_claude_extractor.py
Issues: 4

#### Line 121
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 100

**Context:**
```python
                    message_content_list = data["message"].get("content", [])
                    for content_item in message_content_list:
                        if content_item.get("type") == "text":
                            logger.debug(f"Assistant text chunk: {content_item.get('text', '')[:100]}...")
                elif data.get("type") == "result" and data.get("subtype") == "error":
                    logger.error(f"Claude stream reported an error: {data}")
                    # Continue streaming to see if more info comes, but note the error

            except json.JSONDecodeError:
                logger.warning(f"Non-JSON line in stream or decode error: {stripped_line}")
except Exception as e:
                logger.error(f"Error processing streamed JSON line '{stripped_line}': {e}")
        
        # Wait for the process to complete and get remaining outputs
        stdout_remaining, stderr_output = process.communicate(timeout=60) # Timeout for safety
```

#### Line 149
**Current:** `except: #nosec`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 143

**Context:**
```python
        if not final_result_content:
            logger.warning("Final 'result' field not found in Claude's output stream from a 'success' message.")
            # Attempt to find it in the full capture if it was the last object and not fully streamed
            for captured_line in reversed(full_stdout_capture):
                try:
                    data = json.loads(captured_line)
                    if data.get("type") == "result" and data.get("subtype") == "success" and "result" in data:
                        final_result_content = data["result"]
                        logger.info("Found 'result' in late-stage captured output.")
                        break
except: #nosec
                    pass


    except subprocess.TimeoutExpired:
```

#### Line 159
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 81

**Context:**
```python
                except: #nosec
                    pass


    except subprocess.TimeoutExpired:
        logger.error("Claude process timed out.")
        if process:
            process.kill()
            process.communicate() # Clean up pipes
        return None
except Exception as e:
        logger.exception(f"An error occurred while running Claude: {e}")
        return None
    finally:
        if process and process.poll() is None:
```

#### Line 192
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 188

**Context:**
```python
    
    test_target_dir = Path(test_target_dir_str)
    test_system_prompt_file = Path(test_system_prompt_file_str)

    system_prompt_text_content = ""
    if test_system_prompt_file.is_file():
        try:
            with open(test_system_prompt_file, 'r') as f:
                system_prompt_text_content = f.read()
            logger.info(f"Read system prompt from: {test_system_prompt_file}")
except Exception as e:
            logger.error(f"Could not read system prompt file {test_system_prompt_file}: {e}")
            sys.exit(1)
    else:
        logger.error(f"System prompt file not found: {test_system_prompt_file}")
```

### src/llm_call/core/providers/claude_cli_proxy.py
Issues: 2

#### Line 113
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 109

**Context:**
```python
    async def test_provider():
        all_validation_failures = []
        total_tests = 0
        
        # Test 1: Provider initialization
        total_tests += 1
        try:
            provider = ClaudeCLIProxyProvider()
            assert provider.proxy_url == config.claude_proxy.proxy_url
            logger.success(" Provider initializes with correct URL")
except Exception as e:
            all_validation_failures.append(f"Initialization failed: {e}")
        
        # Test 2: Payload preparation
        total_tests += 1
```

#### Line 132
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 118

**Context:**
```python
            test_messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"}
            ]
            
            # We can't actually call complete without a server, but we can verify
            # the provider is ready and has the right structure
            assert hasattr(provider, 'complete')
            assert hasattr(provider, 'proxy_url')
            logger.success(" Provider has correct structure")
except Exception as e:
            all_validation_failures.append(f"Structure test failed: {e}")
        
        return all_validation_failures, total_tests
```

### src/llm_call/core/providers/litellm_provider.py
Issues: 3

#### Line 96
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 73

**Context:**
```python
            # Check if this is actually an auth error in disguise
            error_str = str(e).lower()
            if any(auth_term in error_str for auth_term in ["jwt", "token", "unauthorized", "forbidden", "401", "403"]):
                logger.error(f"[LiteLLMProvider] Authentication-related bad request for '{model_name}'")
                diagnose_auth_error(e, model_name, context={"api_params": api_params})
            else:
                logger.error(f"[LiteLLMProvider] BadRequestError for '{model_name}': {e}")
                logger.error(f"Request params: {api_params}")
            raise
except Exception as e:
            # Check for auth-related errors in generic exceptions
            error_str = str(e).lower()
            if any(auth_term in error_str for auth_term in ["jwt", "token", "auth", "credential", "forbidden", "unauthorized"]):
                logger.error(f"[LiteLLMProvider] Possible authentication error for '{model_name}'")
```

#### Line 124
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 120

**Context:**
```python
    async def test_provider():
        all_validation_failures = []
        total_tests = 0
        
        # Test 1: Provider initialization
        total_tests += 1
        try:
            provider = LiteLLMProvider()
            assert hasattr(provider, 'complete')
            logger.success(" LiteLLM provider initialized")
except Exception as e:
            all_validation_failures.append(f"Initialization failed: {e}")
        
        # Test 2: Verify it can handle different model formats
        total_tests += 1
```

#### Line 138
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 129

**Context:**
```python
        total_tests += 1
        try:
            provider = LiteLLMProvider()
            
            # Test that it would prepare correct params for different models
            test_messages = [{"role": "user", "content": "test"}]
            
            # We can't actually call complete without API keys, but verify structure
            assert asyncio.iscoroutinefunction(provider.complete)
            logger.success(" Provider has async complete method")
except Exception as e:
            all_validation_failures.append(f"Structure test failed: {e}")
        
        return all_validation_failures, total_tests
```

### src/llm_call/core/retry.py
Issues: 6

#### Line 253
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 233

**Context:**
```python
        elif hasattr(response, "choices") and response.choices:
            # Access the first choice's message content
            first_choice = response.choices[0]
            if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
                return first_choice.message.content or ""
        
        # Handle string responses directly
        elif isinstance(response, str):
            return response
except Exception as e:
        logger.warning(f"Failed to extract content from response: {e}")
    
    # Fallback: convert entire response to string
    logger.debug(f"Using fallback string conversion for response type: {type(response)}")
```

#### Line 388
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 386

**Context:**
```python
        cb_config = config.circuit_breaker_config or CircuitBreakerConfig()
        circuit_breaker = CircuitBreaker(
            name=kwargs.get("model", "default"),
            config=cb_config
        )
    
    # Initialize caching if enabled
    if config.enable_cache:
        try:
            initialize_litellm_cache()
except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
    
    # Enable JSON schema validation if response format is provided
    if response_format:
```

#### Line 557
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 408

**Context:**
```python
                if config.debug_mode:
                    logger.debug(f"Waiting {delay:.1f} seconds before retry...")
                await asyncio.sleep(delay)
            
        except HumanReviewNeededError:
            # Re-raise human review errors
            raise
        except CircuitOpenError:
            # Re-raise circuit breaker errors
            raise
except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {type(e).__name__}: {e}")
            
            # Check if this is an authentication error
            error_str = str(e).lower()
```

#### Line 650
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 648

**Context:**
```python
    max_attempts_before_tool_use = original_llm_config.get("max_attempts_before_tool_use")
    max_attempts_before_human = original_llm_config.get("max_attempts_before_human", config.max_attempts)
    debug_tool_name = original_llm_config.get("debug_tool_name")
    debug_tool_mcp_config = original_llm_config.get("debug_tool_mcp_config")
    original_user_prompt = original_llm_config.get("original_user_prompt")
    
    # Initialize caching if enabled
    if config.enable_cache:
        try:
            initialize_litellm_cache()
except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
    
    # Initialize circuit breaker if enabled
    circuit_breaker = None
```

#### Line 807
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 678

**Context:**
```python
                
                # Apply delay
                delay = config.calculate_delay(attempt)
                time.sleep(delay)
                
        except HumanReviewNeededError:
            raise
        except CircuitOpenError:
            # Re-raise circuit open errors without recording failure
            raise
except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            
            # Record failure if circuit breaker is enabled
            if circuit_breaker:
```

#### Line 878
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 870

**Context:**
```python
        ValidationResult with validation outcome
    """
    try:
        # Check if strategy has async validate method
        if hasattr(strategy, '__avalidate__') or asyncio.iscoroutinefunction(strategy.validate):
            return await strategy.validate(response, context)
        else:
            # Run sync validation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, strategy.validate, response, context)
except Exception as e:
        logger.error(f"Validation error in {strategy.name}: {e}")
        return ValidationResult(
            valid=False,
            error=f"Validation failed with error: {str(e)}",
```

### src/llm_call/core/router.py
Issues: 7

#### Line 158
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 145

**Context:**
```python
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 0.5
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == ClaudeCLIProxyProvider
        assert params["model"] == "max/test-model"
        assert params["temperature"] == 0.5
        logger.success(" Claude proxy routing works")
except Exception as e:
        all_validation_failures.append(f"Claude routing failed: {e}")
    
    # Test 2: LiteLLM routing
    total_tests += 1
```

#### Line 177
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 163

**Context:**
```python
            "max_tokens": 100
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["model"] == "gpt-4"
        assert params["max_tokens"] == 100
        assert "messages" in params
        logger.success(" LiteLLM routing works")
except Exception as e:
        all_validation_failures.append(f"LiteLLM routing failed: {e}")
    
    # Test 3: Vertex AI parameter injection
    total_tests += 1
```

#### Line 198
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 182

**Context:**
```python
        # Set env vars for test
        os.environ["LITELLM_VERTEX_PROJECT"] = "test-project"
        os.environ["LITELLM_VERTEX_LOCATION"] = "us-central1"
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["vertex_project"] == "test-project"
        assert params["vertex_location"] == "us-central1"
        logger.success(" Vertex AI parameter injection works")
except Exception as e:
        all_validation_failures.append(f"Vertex AI routing failed: {e}")
    
    # Test 4: Runpod routing with pod ID
    total_tests += 1
```

#### Line 217
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 203

**Context:**
```python
            "temperature": 0.7
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["model"] == "openai/llama-3-70b"
        assert params["api_base"] == "https://abc123xyz-8000.proxy.runpod.net/v1"
        assert params["api_key"] == "EMPTY"
        logger.success(" Runpod routing with pod ID works")
except Exception as e:
        all_validation_failures.append(f"Runpod routing with pod ID failed: {e}")
    
    # Test 5: Runpod routing with api_base
    total_tests += 1
```

#### Line 236
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 222

**Context:**
```python
            "api_base": "https://custom-8000.proxy.runpod.net/v1"
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["model"] == "openai/llama-3-70b"
        assert params["api_base"] == "https://custom-8000.proxy.runpod.net/v1"
        assert params["api_key"] == "EMPTY"
        logger.success(" Runpod routing with api_base works")
except Exception as e:
        all_validation_failures.append(f"Runpod routing with api_base failed: {e}")
    
    # Test 6: Runpod without pod ID or api_base (should fail)
    total_tests += 1
```

#### Line 254
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 241

**Context:**
```python
            "messages": [{"role": "user", "content": "test"}]
        }
        
        provider_class, params = resolve_route(test_config)
        all_validation_failures.append("Should have raised ValueError for Runpod without pod ID or api_base")
    except ValueError as e:
        if "Runpod model requires" in str(e):
            logger.success(" Runpod error handling works")
        else:
            all_validation_failures.append(f"Wrong error message: {e}")
except Exception as e:
        all_validation_failures.append(f"Wrong exception type: {e}")
    
    # Test 7: Missing model error
    total_tests += 1
```

#### Line 268
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 259

**Context:**
```python
    total_tests += 1
    try:
        test_config = {"messages": [{"role": "user", "content": "test"}]}
        provider_class, params = resolve_route(test_config)
        all_validation_failures.append("Should have raised ValueError for missing model")
    except ValueError as e:
        if "'model' field is required" in str(e):
            logger.success(" Missing model error handling works")
        else:
            all_validation_failures.append(f"Wrong error message: {e}")
except Exception as e:
        all_validation_failures.append(f"Wrong exception type: {e}")
    
    # Final validation result
    if all_validation_failures:
```

### src/llm_call/core/strategies.py
Issues: 4

#### Line 90
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 85

**Context:**
```python
            available = ", ".join(self._strategies.keys())
            raise ValueError(f"Strategy '{name}' not found. Available: {available}")
        
        # Create new instance
        strategy_class = self._strategies[name]
        try:
            instance = strategy_class(**kwargs)
            self._instances[instance_key] = instance
            logger.debug(f"Created instance of strategy: {name}")
            return instance
except Exception as e:
            logger.error(f"Failed to instantiate strategy '{name}': {e}")
            raise
    
    def list_all(self) -> List[Dict[str, Any]]:
```

#### Line 146
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 123

**Context:**
```python
                            
                            # Check if class has the @validator decorator
                            if hasattr(obj, "_validator_name"):
                                strategy_name = obj._validator_name
                            else:
                                strategy_name = name.lower()
                            
                            self.register(strategy_name, obj)
                            logger.info(f"Discovered strategy: {strategy_name} in {py_file.name}")
except Exception as e:
                logger.error(f"Failed to load strategies from {py_file}: {e}")
    
    def load_from_file(self, file_path: Path, name: Optional[str] = None) -> None:
        """Load a specific validator from a file.
```

#### Line 232
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 229

**Context:**
```python
        
        return cls
    
    return decorator


# Import validation module to load all validators
try:
    from llm_call.core import validation
    logger.info("Validation module loaded, validators should be registered")
except Exception as e:
    logger.warning(f"Failed to load validation module: {e}")

# Also try to discover validators in the validation directory
try:
```

#### Line 241
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 236

**Context:**
```python
    logger.info("Validation module loaded, validators should be registered")
except Exception as e:
    logger.warning(f"Failed to load validation module: {e}")

# Also try to discover validators in the validation directory
try:
    builtin_validators_path = Path(__file__).parent / "validation" / "builtin_strategies"
    if builtin_validators_path.exists():
        registry.discover_strategies(builtin_validators_path)
        logger.info(f"Discovered additional validators in {builtin_validators_path}")
except Exception as e:
    logger.warning(f"Failed to discover built-in validators: {e}")

# Create a VALIDATION_STRATEGIES dict for backward compatibility
VALIDATION_STRATEGIES = {}
```

### src/llm_call/core/utils/auth_diagnostics.py
Issues: 2

#### Line 135
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 99

**Context:**
```python
                    "difference_seconds": time_diff,
                    "time_sync_ok": time_diff < 60,  # Allow 1 minute difference
                    "recommendation": None if time_diff < 60 else "System time is off by more than 1 minute. Sync your system clock."
                }
            else:
                return {
                    "system_time": system_time.isoformat(),
                    "network_time": "Could not fetch",
                    "time_sync_ok": "unknown"
                }
except Exception as e:
            return {
                "system_time": datetime.datetime.now().isoformat(),
                "network_time": "Check failed",
                "error": str(e),
```

#### Line 164
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 159

**Context:**
```python
            # Check Vertex AI credentials
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path:
                checks["credentials_found"]["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
                if Path(creds_path).exists():
                    try:
                        with open(creds_path, 'r') as f:
                            sa_data = json.load(f)
                            checks["credentials_found"]["service_account_email"] = sa_data.get("client_email", "Not found")
                            checks["credentials_found"]["project_id"] = sa_data.get("project_id", "Not found")
except Exception as e:
                        checks["issues"].append(f"Could not read service account file: {e}")
                else:
                    checks["issues"].append(f"Service account file not found: {creds_path}")
            else:
```

### src/llm_call/core/utils/document_summarizer.py
Issues: 6

#### Line 104
**Current:** `except:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 102

**Context:**
```python
            for model_prefix, context_size in self.LARGE_CONTEXT_MODELS.items():
                if model.startswith(model_prefix):
                    # Use 80% of context to leave room for prompts and output
                    self.max_tokens_per_chunk = int(context_size * 0.8)
                    break
            logger.info(f"Using large context model {model} with {self.max_tokens_per_chunk} tokens per chunk")
        
        # Simple chunking setup
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
```

#### Line 196
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 181

**Context:**
```python
                "temperature": 0.3
            })
            
            # Extract the text content from the response
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
except Exception as e:
            logger.error(f"Failed to get summary with {self.model}: {e}")
            
            # Provide detailed diagnostics for auth errors
            error_str = str(e).lower()
```

#### Line 385
**Current:** `except:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 383

**Context:**
```python
    """
    summarizer = DocumentSummarizer(
        model=model,
        max_tokens_per_chunk=max_tokens_per_chunk
    )
    
    # Auto-select strategy based on document size and model capabilities
    if strategy == "auto":
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
except:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        token_count = len(encoding.encode(text))
```

#### Line 494
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 491

**Context:**
```python
        natural language processing. However, challenges remain in making AI
        systems more interpretable and ethically aligned with human values.
        """ * 50  # Make it longer to test chunking
        
        logger.info("Testing document summarizer...")
        
        # Test simple summarization
        try:
            result = await summarize_document(test_text, strategy="simple")
            logger.success(f" Simple strategy: {result['summary'][:100]}...")
except Exception as e:
            logger.error(f" Simple strategy failed: {e}")
        
        # Test rolling window
        try:
```

#### Line 501
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 498

**Context:**
```python
        try:
            result = await summarize_document(test_text, strategy="simple")
            logger.success(f" Simple strategy: {result['summary'][:100]}...")
        except Exception as e:
            logger.error(f" Simple strategy failed: {e}")
        
        # Test rolling window
        try:
            result = await summarize_document(test_text, strategy="rolling_window")
            logger.success(f" Rolling window strategy: Generated {len(result.get('window_summaries', []))} window summaries")
except Exception as e:
            logger.error(f" Rolling window strategy failed: {e}")
        
        # Test hierarchical
        try:
```

#### Line 508
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 505

**Context:**
```python
        try:
            result = await summarize_document(test_text, strategy="rolling_window")
            logger.success(f" Rolling window strategy: Generated {len(result.get('window_summaries', []))} window summaries")
        except Exception as e:
            logger.error(f" Rolling window strategy failed: {e}")
        
        # Test hierarchical
        try:
            result = await summarize_document(test_text, strategy="hierarchical")
            logger.success(f" Hierarchical strategy: {result['summary'][:100]}...")
except Exception as e:
            logger.error(f" Hierarchical strategy failed: {e}")
    
    asyncio.run(test_summarizer())
```

### src/llm_call/core/utils/embedding_openai_utils.py
Issues: 1

#### Line 64
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 46

**Context:**
```python
        # Optional: Validate embedding dimension if needed for consistency
        if EMBEDDING_DIMENSIONS > 0 and len(embedding) != EMBEDDING_DIMENSIONS:
            logger.error(
                f"Embedding dimension mismatch! Expected {EMBEDDING_DIMENSIONS}, got {len(embedding)}. Check model '{model}'."
            )
            # Decide if this is critical enough to return None or just warn
            # return None # Make it critical

        logger.debug(f"Generated embedding ({len(embedding)} dims).")
        return embedding
except Exception as e:
        # Log the full exception details using Loguru's exception handling
        logger.exception(f"LiteLLM embedding error: model='{model}', error='{e}'")
        # Return None to indicate failure to the calling function
        return None
```

### src/llm_call/core/utils/embedding_utils.py
Issues: 2

#### Line 71
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 58

**Context:**
```python
        _model = AutoModel.from_pretrained(EMBEDDING_MODEL)
        
        # Move model to GPU if available
        if torch.cuda.is_available():
            _model = _model.to("cuda")
            logger.info("Model loaded on GPU")
        else:
            logger.info("Model loaded on CPU")
        
        return True
except Exception as e:
        logger.error(f"Error initializing embedding model: {e}")
        return False

def get_embedding(text: str, model: str = None) -> Optional[List[float]]:
```

#### Line 121
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 100

**Context:**
```python
                model_output = _model(**encoded_input)
                embedding = model_output.last_hidden_state[:, 0, :].cpu().numpy()[0]
            
            # Normalize embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding.tolist()
except Exception as e:
            logger.error(f"Error generating embedding with {EMBEDDING_MODEL}: {e}")
            # Fall back to hash-based method
            return _fallback_embedding(text)
```

### src/llm_call/core/utils/file_utils.py
Issues: 1

#### Line 56
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 45

**Context:**
```python
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            logger.success(f"Successfully loaded file: {file_path} (size: {len(content)} bytes)")
            return content
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}") from e
    except IOError as e:
        logger.error(f"IOError while reading file {file_path}: {str(e)}")
        raise IOError(f"Error reading file {file_path}: {str(e)}") from e
except Exception as e:
        logger.critical(f"Unexpected error loading file {file_path}: {str(e)}")
        raise
```

### src/llm_call/core/utils/image_processing_utils.py
Issues: 6

#### Line 76
**Current:** `except Exception:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 69

**Context:**
```python
                return fmt
    
    # Use PIL as fallback
    try:
        with Image.open(image_path) as img:
            format_str = img.format.lower() if img.format else "unknown"
            # Normalize jpeg/jpg
            if format_str == "jpeg":
                return "jpeg"
            return format_str
except Exception:
        return "unknown"


# download_and_cache_image remains the same
```

#### Line 152
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 104

**Context:**
```python
                    break # Stop trying if it gets too small
                current_width, current_height = new_width, new_height
                # The actual resize will happen at the start of the next loop or before final save
                logger.info(f"Dimensions reduced to {current_width}x{current_height} for next attempt on {original_file_name}.")
        
        logger.warning(f"Could not compress '{original_image_path}' under {max_size_kb}KB after {max_attempts} attempts. Current size: {compressed_size_kb:.2f}KB. Returning path to last attempt: '{compressed_file_path}'")
        return str(compressed_file_path) # Return the last compressed version even if over budget

    except FileNotFoundError: # Should be caught by initial check, but as a safeguard
        raise
except Exception as e:
        logger.exception(f"Error compressing image '{original_image_path}': {e}")
        return image_path_str # Fallback to original path on error
```

#### Line 181
**Current:** `except Exception as pil_e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 172

**Context:**
```python
            logger.warning(f"Could not determine MIME type for '{image_path}' via mimetypes. Trying with PIL.")
            try:
                with Image.open(image_path) as img:
                    img_format = img.format
                    if img_format:
                        mime_type = Image.MIME.get(img_format.upper())
                    if not mime_type or not mime_type.startswith("image/"):
                        logger.error(f"File '{image_path}' is not a recognized image type (PIL check also failed).")
                        return None
                    logger.info(f"Determined MIME type with PIL: {mime_type} for '{image_path}'")
except Exception as pil_e:
                logger.error(f"PIL could not open or identify image type for '{image_path}': {pil_e}")
                return None
        
        with image_path.open("rb") as image_file:
```

#### Line 192
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 164

**Context:**
```python
                logger.error(f"PIL could not open or identify image type for '{image_path}': {pil_e}")
                return None
        
        with image_path.open("rb") as image_file:
            encoded_bytes = base64.b64encode(image_file.read())
            base64_encoded_str = encoded_bytes.decode("utf-8")
        
        data_uri = f"data:{mime_type};base64,{base64_encoded_str}"
        logger.info(f"Successfully converted '{image_path}' to Base64 Data URI (length: {len(data_uri)}).")
        return data_uri
except Exception as e:
        logger.exception(f"Failed to convert image '{image_path}' to Base64: {e}")
        return None

def decode_base64_image(base64_image_str: str, image_directory_str: str, max_size_kb: int) -> Optional[str]:
```

#### Line 240
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 206

**Context:**
```python
        final_base64 = convert_image_to_base64(compressed_image_file_path)
        
        try:
            os.remove(temp_image_path)
            if Path(compressed_image_file_path).exists() and compressed_image_file_path != str(temp_image_path):
                os.remove(compressed_image_file_path)
        except OSError as e_remove:
            logger.warning(f"Could not remove temporary image files: {e_remove}")
            
        return final_base64
except Exception as e:
        logger.error(f"Error decoding/compressing Base64 image: {e}")
        return None # Signal failure
```

#### Line 290
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 277

**Context:**
```python
            base64_image_data_uri = convert_image_to_base64(compressed_image_file_path)
            
            if base64_image_data_uri:
                return {"type": "image_url", "image_url": {"url": base64_image_data_uri}}
            else:
                logger.error(f"Failed to convert local image to Base64: {compressed_image_file_path}")
                return None
        except FileNotFoundError:
            logger.error(f"Local image file not found: {image_input_url_or_path}")
            return None
except Exception as e:
            logger.exception(f"Unexpected error processing local image '{image_input_url_or_path}': {e}")
            return None
```

### src/llm_call/core/utils/initialize_litellm_cache.py
Issues: 2

#### Line 97
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 47

**Context:**
```python
            f"⚠️ Redis connection/setup failed: {e}. Falling back to in-memory caching."
        )
        logger.debug("Configuring LiteLLM in-memory cache...")
        litellm.cache = litellm.Cache(
            type="local",
            supported_call_types=["acompletion", "completion", "embedding"],
            ttl=(60 * 60 * 1),
        )
        litellm.enable_cache()
        logger.info(" LiteLLM Caching enabled using in-memory (local) cache.")
except Exception as e:
        logger.exception(f"Unexpected error during LiteLLM cache initialization: {e}")
# --- Test Function (Kept for standalone testing) ---
def test_litellm_cache():
    """Test the LiteLLM cache functionality with a sample completion call"""
```

#### Line 131
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 104

**Context:**
```python
        # Second call should hit cache
        response2 = litellm.completion(
            model="gpt-4o-mini",
            messages=test_messages,
            cache={"no-cache": False},
        )
        logger.info(f"Second call usage: {response2.usage}")
        if m := response2._hidden_params.get("cache_hit"):
            logger.info(f"Response 2: Cache hit: {m}")
except Exception as e:
        logger.error(f"Cache test failed with error: {e}")
        raise

if __name__ == "__main__":
```

### src/llm_call/core/utils/json_utils.py
Issues: 3

#### Line 106
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 102

**Context:**
```python
        if directory:
            os.makedirs(directory, exist_ok=True)
            logger.info(f'Ensured the directory exists: {directory}')
    except OSError as e:
        logger.error(f'Failed to create directory {directory}: {e}')
        raise
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            logger.info(f'Saved extracted tables to JSON cache at: {file_path}')
except Exception as e:
        logger.error(f'Failed to save cache to {file_path}: {e}')
        raise
```

#### Line 140
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 127

**Context:**
```python
            content = json_match.group(1)
        repaired_json = repair_json(content, return_objects=True)
        if isinstance(repaired_json, (dict, list)):
            logger.info('Successfully repaired and validated JSON response')
            return repaired_json
        parsed_content = json.loads(repaired_json)
        logger.debug('Successfully validated JSON response')
        return parsed_content
    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error after repair attempt: {e}')
except Exception as e:
        logger.error(f'Failed to parse JSON response: {e}')
    logger.debug(f'Returning original content as string: {content}')
    return content
```

#### Line 182
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 180

**Context:**
```python
                except json.JSONDecodeError:
                    logger.debug("Failed to parse extracted content as JSON, falling back to parse_json")
                    parsed_content = parse_json(json_content, logger)
                    return parsed_content if isinstance(parsed_content, (dict, list)) else json_content

        # Default behavior if no JSON was extracted from code blocks
        parsed_content = parse_json(content, logger)
        if return_dict and isinstance(parsed_content, str):
            try:
                return json.loads(parsed_content)
except Exception as e:
                logger.error(f'Failed to convert parsed content to dict/list: {e}\nFailed content: {type(parsed_content)}: {parsed_content}')
                return parsed_content
        return parsed_content
    logger.info(f'Returning original content: {content}')
```

### src/llm_call/core/utils/log_utils.py
Issues: 6

#### Line 241
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 237

**Context:**
```python

    print("\n--- Testing Invalid Inputs ---")

    # Test Case 1: Input is not a list
    invalid_input_1 = {"a": 1, "b": 2}  # A dictionary
    print(f"\nTesting input: {invalid_input_1} ({type(invalid_input_1).__name__})")
    try:
        log_safe_results(invalid_input_1)
    except TypeError as e:
        print(f" Successfully caught expected error: {e}")
except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 2: Input is a list, but contains non-dict elements
    invalid_input_2 = [{"a": 1}, "string_element", {"c": 3}]  # List with a string
```

#### Line 251
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 247

**Context:**
```python
    except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 2: Input is a list, but contains non-dict elements
    invalid_input_2 = [{"a": 1}, "string_element", {"c": 3}]  # List with a string
    print(f"\nTesting input: {invalid_input_2}")
    try:
        log_safe_results(invalid_input_2)
    except TypeError as e:
        print(f" Successfully caught expected error: {e}")
except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 3: Input is a list of simple types
    invalid_input_3 = [1, 2, 3, 4]  # List of integers
```

#### Line 261
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 257

**Context:**
```python
    except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 3: Input is a list of simple types
    invalid_input_3 = [1, 2, 3, 4]  # List of integers
    print(f"\nTesting input: {invalid_input_3}")
    try:
        log_safe_results(invalid_input_3)
    except TypeError as e:
        print(f" Successfully caught expected error: {e}")
except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 4: Input is None
    invalid_input_4 = None
```

#### Line 271
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 267

**Context:**
```python
    except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 4: Input is None
    invalid_input_4 = None
    print(f"\nTesting input: {invalid_input_4}")
    try:
        log_safe_results(invalid_input_4)
    except TypeError as e:
        print(f" Successfully caught expected error: {e}")
except Exception as e:
        print(f" Caught unexpected error: {e}")

    # Test Case 5: Empty list (should be valid)
    valid_input_empty = []
```

#### Line 283
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 277

**Context:**
```python

    # Test Case 5: Empty list (should be valid)
    valid_input_empty = []
    print(f"\nTesting input: {valid_input_empty}")
    try:
        result = log_safe_results(valid_input_empty)
        if result == []:
            print(f" Successfully processed empty list.")
        else:
            print(f" Processing empty list resulted in unexpected output: {result}")
except Exception as e:
        print(f" Caught unexpected error processing empty list: {e}")

    # Test API logging functions
    print("\n--- Testing API Logging Functions ---")
```

#### Line 293
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 288

**Context:**
```python
    except Exception as e:
        print(f" Caught unexpected error processing empty list: {e}")

    # Test API logging functions
    print("\n--- Testing API Logging Functions ---")
    try:
        log_api_request("TestService", {"model": "test-model", "prompt": "This is a test prompt"})
        log_api_response("TestService", {"result": "This is a test result", "status": "success"})
        log_api_error("TestService", Exception("Test error"), {"model": "test-model"})
        print(" API logging functions executed successfully.")
except Exception as e:
        print(f" Error testing API logging functions: {e}")
```

### src/llm_call/core/utils/multimodal_utils.py
Issues: 1

#### Line 188
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 182

**Context:**
```python

    logger.debug("Checking for multimodal content in messages...")
    if is_multimodal(messages):
        logger.info("Multimodal content detected. Processing messages...")
        try:
            processed_messages = format_multimodal_messages(
                messages, image_directory, max_image_size_kb
            )
            logger.info("Multimodal processing completed successfully.")
            return processed_messages
except Exception as e:
            logger.exception(f"Error during multimodal processing: {e}")
            logger.debug("Falling back to raw messages.")
            return messages
    logger.info("No multimodal content detected. Returning original messages.")
```

### src/llm_call/core/utils/summarization.py
Issues: 1

#### Line 273
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 170

**Context:**
```python
                    repo_workflow.workflow_logger.log_data(
                        {"summary_path": summary_path, "format": "markdown"},
                        level=LogLevel.SUCCESS,
                        source=ComponentType.LLM,
                        description="LLM summary saved"
                    )
                    repo_workflow.workflow_logger.complete_step("Save LLM summary")
            finally:
                os.remove(tmp_json_path)
except Exception as e:
        logger.error(f"LLM summarization failed: {e}")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"error": str(e)}))
        raise
```

### src/llm_call/core/utils/text_chunker.py
Issues: 4

#### Line 264
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 252

**Context:**
```python
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k",
                "gpt-4o", "gpt-4-turbo"
            }
            if any(self.model_name.startswith(m) for m in openai_models):
                # For OpenAI models, use the specific encoding
                self.encoding = tiktoken.encoding_for_model(self.model_name)
            else:
                # For other models, use cl100k_base as default
                self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.debug(f"Using tiktoken with {self.model_name} encoding")
except Exception as e:
            logger.warning(f"Error initializing tiktoken: {e}. Using fallback counting.")
            self.encoding = None

    def _setup_sentence_splitter(self):
```

#### Line 276
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 270

**Context:**
```python
            self.encoding = None

    def _setup_sentence_splitter(self):
        """Set up the sentence splitter."""
        try:
            self.nlp = spacy.load(self.spacy_model_name)
            logger.debug(f"Using spaCy model {self.spacy_model_name} for sentence splitting")
        except OSError:
            logger.warning(f"SpaCy model '{self.spacy_model_name}' not found. Using regex fallback.")
            self.nlp = None
except Exception as e:
            logger.warning(f"Error loading spaCy model: {e}. Using regex fallback.")
            self.nlp = None

    def count_tokens(self, text: str) -> int:
```

#### Line 699
**Current:** `except Exception:`
**Suggested:** `except Exception:`
**Comment:** # OpenAI API call failed

**Try block starts at line:** 689

**Context:**
```python
    try:
        openai_models = {
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k",
            "gpt-4o", "gpt-4-turbo"
        }
        if any(model.startswith(m) for m in openai_models):
            encoding = tiktoken.encoding_for_model(model)
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
except Exception:
        # Fallback to character estimation if encoding fails
        return int(len(text) / 4)
```

#### Line 763
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 759

**Context:**
```python

This sample document should be sufficient to verify the basic functionality.
"""
    
    # Use provided file if available
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                test_text = f.read()
                console.print(f"[green]Using text from file:[/green] {args.file}")
except Exception as e:
            console.print(f"[red]Error reading file:[/red] {e}")
            console.print("[yellow]Using built-in sample text instead[/yellow]")
            test_text = sample_text
    else:
```

### src/llm_call/core/utils/tree_sitter_utils.py
Issues: 5

#### Line 216
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 213

**Context:**
```python
        The language identifier if supported, None otherwise
    """
    code_type = code_type.lstrip(".").lower()
    language_name = LANGUAGE_MAPPINGS.get(code_type)
    if not language_name:
        logger.debug(f"No language mapping for code type: {code_type}")
        return None
    try:
        tlp.get_language(language_name)
        return language_name
except Exception as e:
        logger.debug(f"Language {language_name} not supported by tree-sitter-language-pack: {e}")
        return None
```

#### Line 762
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 623

**Context:**
```python
                                current_class["name"] = node.text.decode("utf-8")
                        
                        elif name == "class_body":
                            if current_class:
                                current_class["docstring"] = extract_docstring(node, language_id)
                
                metadata["functions"] = functions
                metadata["classes"] = classes
                metadata["tree_sitter_success"] = True
except Exception as e:
                # Fallback to a simple approach if the query-based processing fails
                logger.warning(f"Query-based extraction processing failed: {e}, falling back to traversal")
                functions, classes = traverse_fallback(root_node, code, language_id)
                metadata["functions"] = functions
```

#### Line 770
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 606

**Context:**
```python
                metadata["tree_sitter_success"] = True
                
            except Exception as e:
                # Fallback to a simple approach if the query-based processing fails
                logger.warning(f"Query-based extraction processing failed: {e}, falling back to traversal")
                functions, classes = traverse_fallback(root_node, code, language_id)
                metadata["functions"] = functions
                metadata["classes"] = classes
                metadata["tree_sitter_success"] = True
except Exception as e:
            # Fallback to a simple approach if the query fails
            logger.warning(f"Query-based extraction failed: {e}, falling back to traversal")
            functions, classes = traverse_fallback(root_node, code, language_id)
            metadata["functions"] = functions
```

#### Line 778
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 485

**Context:**
```python
                metadata["tree_sitter_success"] = True
            
        except Exception as e:
            # Fallback to a simple approach if the query fails
            logger.warning(f"Query-based extraction failed: {e}, falling back to traversal")
            functions, classes = traverse_fallback(root_node, code, language_id)
            metadata["functions"] = functions
            metadata["classes"] = classes
            metadata["tree_sitter_success"] = True
except Exception as e:
        logger.error(f"Error parsing code with tree-sitter: {e}")
        metadata["error"] = str(e)
        metadata["tree_sitter_success"] = False
```

#### Line 973
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 955

**Context:**
```python
                "error": f"Unsupported file extension: {os.path.splitext(file_path)[1]}"
            }
            
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            code = f.read()
            
        metadata = extract_code_metadata(code, language)
        metadata["file_path"] = file_path
        return metadata
except Exception as e:
        logger.error(f"Error extracting metadata from file {file_path}: {e}")
        return {
            "language": get_language_by_extension(file_path) or "unknown",
            "functions": [],
```

### src/llm_call/core/validation/__init__.py
Issues: 4

#### Line 18
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 15

**Context:**
```python

from pathlib import Path
from loguru import logger

from llm_call.core.strategies import registry

# Import all validator modules to ensure they register themselves
try:
    from llm_call.core.validation.builtin_strategies import basic_validators
    logger.info("Loaded basic validators")
except Exception as e:
    logger.error(f"Failed to load basic validators: {e}")

try:
    from llm_call.core.validation.builtin_strategies import ai_validators
```

#### Line 24
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 21

**Context:**
```python
# Import all validator modules to ensure they register themselves
try:
    from llm_call.core.validation.builtin_strategies import basic_validators
    logger.info("Loaded basic validators")
except Exception as e:
    logger.error(f"Failed to load basic validators: {e}")

try:
    from llm_call.core.validation.builtin_strategies import ai_validators
    logger.info("Loaded AI validators")
except Exception as e:
    logger.error(f"Failed to load AI validators: {e}")

try:
    from llm_call.core.validation.builtin_strategies import advanced_validators
```

#### Line 30
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 27

**Context:**
```python

try:
    from llm_call.core.validation.builtin_strategies import ai_validators
    logger.info("Loaded AI validators")
except Exception as e:
    logger.error(f"Failed to load AI validators: {e}")

try:
    from llm_call.core.validation.builtin_strategies import advanced_validators
    logger.info("Loaded advanced validators")
except Exception as e:
    logger.error(f"Failed to load advanced validators: {e}")

# Also discover any validators in this directory
try:
```

#### Line 39
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 34

**Context:**
```python
    logger.info("Loaded advanced validators")
except Exception as e:
    logger.error(f"Failed to load advanced validators: {e}")

# Also discover any validators in this directory
try:
    validation_dir = Path(__file__).parent / "builtin_strategies"
    if validation_dir.exists():
        registry.discover_strategies(validation_dir)
        logger.info(f"Discovered validators in {validation_dir}")
except Exception as e:
    logger.warning(f"Failed to discover validators: {e}")

# Log what's available
available = registry.list_all()
```

### src/llm_call/core/validation/ai_validator_base.py
Issues: 2

#### Line 175
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 159

**Context:**
```python
            
            # Parse response
            result = await self.parse_validation_response(llm_response)
            
            # Add metadata
            result.metadata["call_history"] = self._call_history
            result.metadata["validator_class"] = self.__class__.__name__
            
            return result
except Exception as e:
            logger.error(f"Validation error in {self.__class__.__name__}: {e}")
            # Return failed validation with error details
            return ValidationResult(
                valid=False,
```

#### Line 365
**Current:** `except:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 362

**Context:**
```python
2. Security issues
3. Best practices

Respond with JSON containing valid, confidence, reasoning, and suggestions."""
                
            async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
                content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                try:
                    parsed = json.loads(content)
                    return ValidationResult(**parsed)
except:
                    return ValidationResult(valid=True, confidence=0.5, reasoning="Parse error")
                    
        code_validator = CodeValidator(AIValidatorConfig(validation_model="gpt-4"))
        code_validator.set_llm_caller(mock_llm_caller)
```

### src/llm_call/core/validation/builtin_strategies/advanced_validators.py
Issues: 3

#### Line 268
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 263

**Context:**
```python
        # The main validate method will use the entire content
        return blocks
    
    def _validate_python(self, code: str) -> Optional[str]:
        """Validate Python code syntax."""
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return f"Syntax error at line {e.lineno}: {e.msg}"
except Exception as e:
            return str(e)


if HAS_JSONSCHEMA:
```

#### Line 315
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 307

**Context:**
```python
            
            # Try to parse JSON
            try:
                data = clean_json_string(content, return_dict=True)
                if data is None:
                    return ValidationResult(
                        valid=False,
                        error="No valid JSON found in response",
                        suggestions=["Ensure response contains valid JSON"]
                    )
except Exception as e:
                return ValidationResult(
                    valid=False,
                    error=f"Failed to parse JSON: {e}",
                    suggestions=["Ensure response is valid JSON"]
```

#### Line 389
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 381

**Context:**
```python
        
        # Parse JSON
        try:
            data = clean_json_string(content, return_dict=True)
            if data is None:
                return ValidationResult(
                    valid=False,
                    error="No valid JSON found to check fields",
                    suggestions=["Ensure response contains valid JSON"]
                )
except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Failed to parse JSON: {e}"
            )
```

### src/llm_call/core/validation/builtin_strategies/ai_validators.py
Issues: 3

#### Line 93
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 91

**Context:**
```python
            
        Returns:
            LLM response dict or None if error
        """
        if not self._llm_caller:
            logger.error(f"[{self.name}] LLM caller not set for AI-assisted validation")
            return None
        
        try:
            return await self._llm_caller(llm_config)
except Exception as e:
            logger.error(f"[{self.name}] Error calling LLM: {e}")
            return None
```

#### Line 242
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 204

**Context:**
```python
                    valid=True,
                    debug_info={"agent_report": agent_report}
                )
                
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                error=f"AI Validator: Could not parse JSON response: {e}",
                debug_info={"raw_response": content[:300]}
            )
except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response")
            return ValidationResult(
                valid=False,
                error=f"AI Validator: Error processing response: {e}"
```

#### Line 374
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 340

**Context:**
```python
                    error=f"Agent validation failed: {explanation}",
                    debug_info={"agent_result": result, "details": details}
                )
                
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                error=f"Agent Task Validator: Invalid JSON response: {e}",
                debug_info={"raw_response": content[:300]}
            )
except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response")
            return ValidationResult(
                valid=False,
                error=f"Agent Task Validator: Error: {e}"
```

### src/llm_call/core/validation/builtin_strategies/basic_validators.py
Issues: 6

#### Line 101
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 45

**Context:**
```python
                    valid=False,
                    error="Response content is empty",
                    suggestions=["Try rephrasing the prompt", "Check model availability"]
                )
            
            return ValidationResult(
                valid=True,
                debug_info={"content_length": len(content)}
            )
except Exception as e:
            logger.error(f"Error in ResponseNotEmptyValidator: {e}")
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}",
```

#### Line 185
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 129

**Context:**
```python
                        "Ensure prompt requests JSON format",
                        "Try adding 'You must respond with valid JSON' to prompt",
                        "Check for trailing commas or unquoted strings"
                    ],
                    debug_info={
                        "parse_error": str(e),
                        "error_position": e.pos if hasattr(e, 'pos') else None
                    }
                )
except Exception as e:
            logger.error(f"Error in JsonStringValidator: {e}")
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}",
```

#### Line 220
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 207

**Context:**
```python
            # Test with dict response (Claude proxy format)
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": "Hello, world!"}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == True
            logger.success(" ResponseNotEmptyValidator accepts valid content")
except Exception as e:
            all_validation_failures.append(f"Empty validator test failed: {e}")
        
        # Test 2: ResponseNotEmptyValidator with empty response
        total_tests += 1
```

#### Line 238
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 225

**Context:**
```python
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": ""}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == False
            assert "empty" in result.error.lower()
            logger.success(" ResponseNotEmptyValidator rejects empty content")
except Exception as e:
            all_validation_failures.append(f"Empty validator rejection test failed: {e}")
        
        # Test 3: JsonStringValidator with valid JSON
        total_tests += 1
```

#### Line 256
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 243

**Context:**
```python
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": '{"key": "value", "number": 42}'}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == True
            assert result.debug_info["json_keys"] == ["key", "number"]
            logger.success(" JsonStringValidator accepts valid JSON")
except Exception as e:
            all_validation_failures.append(f"JSON validator test failed: {e}")
        
        # Test 4: JsonStringValidator with invalid JSON
        total_tests += 1
```

#### Line 275
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 261

**Context:**
```python
                "choices": [{
                    "message": {"role": "assistant", "content": 'This is not JSON'}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == False
            assert "Invalid JSON" in result.error
            assert len(result.suggestions) > 0
            logger.success(" JsonStringValidator rejects invalid JSON")
except Exception as e:
            all_validation_failures.append(f"JSON validator rejection test failed: {e}")
        
        return all_validation_failures, total_tests
```

### src/llm_call/core/validation/builtin_strategies/specialized_validators.py
Issues: 1

#### Line 152
**Current:** `except Exception as e:`
**Suggested:** `except yaml.YAMLError:`
**Comment:** # YAML parsing failed

**Try block starts at line:** 137

**Context:**
```python
                # Try YAML
                try:
                    import yaml
                    spec = yaml.safe_load(content)
                except ImportError:
                    return ValidationResult(
                        valid=False,
                        error="YAML support not available, please provide JSON format",
                        suggestions=["Convert to JSON format or install PyYAML"]
                    )
except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Failed to parse OpenAPI spec: {e}",
                suggestions=["Ensure response is valid JSON or YAML"]
```

### src/llm_call/core/validation/json_validators.py
Issues: 4

#### Line 266
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 257

**Context:**
```python
    total_tests += 1
    try:
        validator = JSONExtractionValidator()
        test_response = "Here's the data: ```json\n{\"name\": \"test\", \"value\": 42}\n```"
        result = validator.validate(test_response)
        
        assert result["valid"] == True
        assert result["data"]["name"] == "test"
        assert result["data"]["value"] == 42
        logger.success("✅ Basic JSON extraction works")
except Exception as e:
        all_validation_failures.append(f"Basic extraction failed: {e}")
    
    # Test 2: Field validation
    total_tests += 1
```

#### Line 283
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 271

**Context:**
```python
        test_data = {"user": {"name": "Alice", "age": 30}}
        
        result = field_validator.validate_field_presence(test_data, ["user"])
        assert result["valid"] == True
        
        result = field_validator.validate_nested_field(test_data, "user.name", str)
        assert result["valid"] == True
        assert result["value"] == "Alice"
        
        logger.success("✅ Field validation works")
except Exception as e:
        all_validation_failures.append(f"Field validation failed: {e}")
    
    # Test 3: JSON repair
    total_tests += 1
```

#### Line 297
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 288

**Context:**
```python
    total_tests += 1
    try:
        repairer = JSONErrorRecovery()
        malformed = "{'name': 'test', 'values': [1, 2, 3,]}"
        
        result = repairer.repair_json(malformed)
        assert result["valid"] == True
        assert result["data"]["name"] == "test"
        assert len(result["data"]["values"]) == 3
        logger.success("✅ JSON repair works")
except Exception as e:
        all_validation_failures.append(f"JSON repair failed: {e}")
    
    # Test 4: Performance check
    total_tests += 1
```

#### Line 314
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 302

**Context:**
```python
        validator = JSONExtractionValidator()
        test_json = '{"test": "data"}' * 100
        
        start = time.perf_counter()
        for _ in range(100):
            result = validator.validate(f"```json\n{test_json}\n```")
        elapsed = (time.perf_counter() - start) / 100 * 1000
        
        assert elapsed < 10, f"Too slow: {elapsed:.2f}ms"
        logger.success(f"✅ Performance: {elapsed:.2f}ms per validation")
except Exception as e:
        all_validation_failures.append(f"Performance test failed: {e}")
    
    # Final result
    if all_validation_failures:
```

### src/llm_call/core/validation/retry_manager.py
Issues: 5

#### Line 158
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 153

**Context:**
```python
        self._retry_callbacks[stage].append(callback)
        
    async def _execute_stage_callbacks(self, stage: RetryStage, context: RetryContext):
        """Execute all callbacks for a stage"""
        for callback in self._retry_callbacks[stage]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(context)
                else:
                    callback(context)
except Exception as e:
                logger.error(f"Stage callback error: {e}")
                
    def _determine_stage(self, attempt: int) -> RetryStage:
        """Determine retry stage based on attempt count"""
```

#### Line 258
**Current:** `except Exception as e:`
**Suggested:** `except asyncio.TimeoutError:`
**Comment:** # Async operation failed

**Try block starts at line:** 253

**Context:**
```python
            before=before_retry,
            after=after_retry,
            reraise=True
        )
        
        try:
            return await retrying(wrapped_func)
        except HumanReviewNeededError:
            # Re-raise human review errors
            raise
except Exception as e:
            # Check if we should escalate to human review
            if context.attempt_count >= self.config.max_attempts_before_human:
                raise HumanReviewNeededError(
                    f"Human review required: {str(e)}",
```

#### Line 330
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 321

**Context:**
```python
        context1 = RetryContext(original_request={"test": 1})
        try:
            result = await manager.execute_with_retry(
                test_function,
                context1,
                validate_result,
                value=15
            )
            print(f" Success: {result}")
            print(f"Final stage: {context1.current_stage.value}")
except Exception as e:
            print(f" Failed: {e}")
            
        # Test 2: Success with tool assistance
        print("\n=== Test 2: Tool-Assisted Success ===")
```

#### Line 346
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 336

**Context:**
```python
        try:
            result = await manager.execute_with_retry(
                test_function,
                context2,
                validate_result,
                value=3
            )
            print(f" Success: {result}")
            print(f"Final stage: {context2.current_stage.value}")
            print(f"Total attempts: {context2.attempt_count}")
except Exception as e:
            print(f" Failed: {e}")
            
        # Test 3: Human review needed
        print("\n=== Test 3: Human Review Escalation ===")
```

#### Line 364
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 352

**Context:**
```python
                test_function,
                context3,
                validate_result,
                value=1
            )
            print(f" Success: {result}")
        except HumanReviewNeededError as e:
            print(f" Human review required: {e}")
            print(f"Total errors: {len(e.validation_errors)}")
            print(f"Stage history: {[s.value for s in context3.stage_history]}")
except Exception as e:
            print(f" Unexpected error: {e}")
            
        # Test 4: Configuration validation
        print("\n=== Test 4: Config Validation ===")
```

### src/llm_call/mcp_server.py
Issues: 7

#### Line 64
**Current:** `except Exception as e:`
**Suggested:** `except asyncio.TimeoutError:`
**Comment:** # Async operation failed

**Try block starts at line:** 49

**Context:**
```python
            return await handle_validation(params)
        
        elif command == "analyze_code":
            return await handle_code_analysis(params)
        
        elif command == "configure_mcp":
            return await handle_mcp_configuration(params)
        
        else:
            raise HTTPException(400, f"Unknown command: {command}")
except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "command": command
```

#### Line 140
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 105

**Context:**
```python
                "metadata": {
                    "mcp_servers": request.mcp_servers or [],
                    "working_directory": working_dir
                }
            }
        finally:
            # Clean up temporary config
            if temp_config_path:
                mcp_handler.cleanup_temp_config(temp_config_path)
except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "model": request.model
```

#### Line 172
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 156

**Context:**
```python
        response = await llm_call(
            prompt=messages[-1]["content"],
            model=model,
            messages=messages[:-1] if len(messages) > 1 else None
        )
        content = response if isinstance(response, str) else response.get("content", "")
        yield f"data: {json.dumps({'content': content})}\n\n"
        
        yield "data: [DONE]\n\n"
except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    finally:
        # Clean up temporary config
        if temp_config_path:
```

#### Line 216
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 198

**Context:**
```python
            validate=validator_name,
            max_retries=3
        )
        
        return {
            "type": "validation_response",
            "valid": True,
            "content": response if isinstance(response, str) else response.get("content", ""),
            "validator": validator_type
        }
except Exception as e:
        return {
            "type": "validation_response",
            "valid": False,
            "error": str(e),
```

#### Line 256
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 242

**Context:**
```python
            temperature=0.3  # Lower temperature for code analysis
        )
        
        return {
            "type": "code_analysis_response",
            "analysis_type": analysis_type,
            "language": language,
            "result": response if isinstance(response, str) else response.get("content", ""),
            "model": "max/claude-3-opus-20240229"
        }
except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "analysis_type": analysis_type
```

#### Line 405
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 399

**Context:**
```python
        "components": {}
    }
    
    # Check MCP handler
    try:
        mcp_servers = mcp_handler.get_available_servers()
        health_status["components"]["mcp_handler"] = {
            "status": "healthy",
            "servers_available": len(mcp_servers)
        }
except Exception as e:
        health_status["components"]["mcp_handler"] = {
            "status": "unhealthy",
            "error": str(e)
        }
```

#### Line 424
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 413

**Context:**
```python
        # Quick test with a simple prompt
        test_response = await llm_call(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            max_tokens=10
        )
        health_status["components"]["llm_routing"] = {
            "status": "healthy",
            "test_model": "claude-3-haiku-20240307"
        }
except Exception as e:
        health_status["components"]["llm_routing"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
```

### src/llm_call/proof_of_concept/archive/root_cleanup/scripts_v2/run_v4_simple_test.py
Issues: 2

#### Line 103
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 74

**Context:**
```python
            }
        else:
            logger.error(f" Test failed: {test_id} - No response")
            return {
                "test_id": test_id,
                "model": model,
                "status": "FAILED",
                "error": "No response received"
            }
except Exception as e:
        logger.error(f" Test failed: {test_id} - {type(e).__name__}: {str(e)}")
        return {
            "test_id": test_id,
            "model": model,
```

#### Line 134
**Current:** `except:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 132

**Context:**
```python
    try:
        data = json.loads(cleaned)
        test_cases = data.get("test_cases", data if isinstance(data, list) else [])
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        # Try to extract just the test cases array
        match = re.search(r'"test_cases":\s*(\[.*\])', cleaned, re.DOTALL)
        if match:
            try:
                test_cases = json.loads(match.group(1))
except:
                logger.error("Could not extract test cases")
                return
        else:
            return
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/debug_agent_empty_content.py
Issues: 1

#### Line 162
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 158

**Context:**
```python
        manager = AsyncPollingManager()
        status = await manager.get_status(full_response)
        if status:
            print(f"Task status: {status.status.value}")
            print(f"Waiting for completion...")
            
            try:
                result = await manager.wait_for_task(full_response, timeout=60)
                print(f"\nFinal result type: {type(result)}")
                print(f"Final result: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")
except Exception as e:
                print(f"Error waiting for task: {e}")
                
                # Check final status
                final_status = await manager.get_status(full_response)
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/debug_validation_error.py
Issues: 1

#### Line 113
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 102

**Context:**
```python
            result = await validator.validate("Test text", {})
            print(f"Validation result:")
            print(f"  Valid: {result.valid}")
            print(f"  Error: {result.error}")
            
            # Check what clean_json_string returns
            content = test['response']['choices'][0]['message']['content']
            parsed = clean_json_string(content, return_dict=True)
            print(f"  clean_json_string result: {type(parsed).__name__} = {repr(parsed)}")
except Exception as e:
            print(f"Exception during validation: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/extract_json.py
Issues: 1

#### Line 52
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 41

**Context:**
```python
    data = clean_json_string(json_str, return_dict=True)
    if isinstance(data, list):
        print(f"Successfully extracted {len(data)} test cases")
        
        # Save cleaned version
        with open('test_prompts_clean.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Saved to test_prompts_clean.json")
    else:
        print(f"Unexpected data type: {type(data)}")
except Exception as e:
    print(f"Error: {e}")
    
    # Try basic JSON parse to get better error message
    try:
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/fix_all_json_issues.py
Issues: 1

#### Line 105
**Current:** `except:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 102

**Context:**
```python
                                with open('test_prompts_debug.json', 'w') as f:
                                    f.write(json_content)

                                    # One more attempt - fix any remaining issues
                                    # Remove any control characters
                                    json_content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_content)

                                    try:
                                        data = json.loads(json_content)
                                        print(f"Fixed after removing control characters! {len(data)} test cases")
except:
                                        print("Still couldn't parse. Manual intervention needed.")
                                        exit(1)

                                        # Now properly format all the agent task prompts
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/fix_model_response_serialization.py
Issues: 2

#### Line 181
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 178

**Context:**
```python
            
        if hasattr(response, 'model_dump_json'):
            result = response.model_dump_json()
            print(f" model_dump_json() works: {type(result)}")
            
        # Test JSON serialization with default=str
        test_dict = {"response": response}
        try:
            json_str = json.dumps(test_dict, default=str)
            print(f" json.dumps with default=str works: {len(json_str)} chars")
except Exception as e:
            print(f" json.dumps with default=str failed: {e}")
            
    except Exception as e:
        print(f" Test failed: {e}")
```

#### Line 184
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 154

**Context:**
```python
            print(f" model_dump_json() works: {type(result)}")
            
        # Test JSON serialization with default=str
        test_dict = {"response": response}
        try:
            json_str = json.dumps(test_dict, default=str)
            print(f" json.dumps with default=str works: {len(json_str)} chars")
        except Exception as e:
            print(f" json.dumps with default=str failed: {e}")
except Exception as e:
        print(f" Test failed: {e}")


if __name__ == "__main__":
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/litellm_client_poc.py
Issues: 2

#### Line 329
**Current:** `except Exception as e_val_init:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 323

**Context:**
```python
            strategy_params = val_conf.get("params", {})
            
            ValidatorClass = poc_strategy_registry.get(strategy_type_name)
            if ValidatorClass:
                try:
                    validator_instance = ValidatorClass(**strategy_params)
                    if hasattr(validator_instance, "set_llm_caller") and _recursive_llm_caller:
                         validator_instance.set_llm_caller(_recursive_llm_caller) 
                    active_validation_strategies.append(validator_instance)
                    logger.info(f"Loaded validator for '{model_name_for_logging}': {strategy_type_name} with params: {strategy_params}")
except Exception as e_val_init:
                    logger.error(f"Failed to instantiate validator '{strategy_type_name}' with params {strategy_params} for '{model_name_for_logging}': {e_val_init}")
            else:
                logger.warning(f"Unknown validation strategy type: '{strategy_type_name}' for model '{model_name_for_logging}'")
```

#### Line 385
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 243

**Context:**
```python
        logger.error(f"🚫 HUMAN REVIEW NEEDED for model '{model_name_for_logging}': {hrne.args[0]}") # hrne.args[0] is the message
        # Log more details if needed, hrne.last_response and hrne.validation_errors are available
        return {"error": "Human review needed", "details": str(hrne.args[0]), 
                "last_response": hrne.last_response, 
                "validation_errors": [ve.error for ve in hrne.validation_errors if hasattr(ve, 'error')]}
    except RetryError as re_outer: # Fallback if tenacity retries (within _execute_... if any) are re-raised
        final_exception = re_outer.last_attempt.exception()
        logger.error(f"❌ Call for model '{model_name_for_logging}' FAILED AFTER MAX RETRIES (Tenacity outer loop).")
        logger.error(f"   Last exception type: {type(final_exception).__name__}")
        logger.error(f"   Last exception details: {final_exception}")
except Exception as e:
        logger.error(f"💥 Unexpected error in llm_call orchestrator for model '{model_name_for_logging}': {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
    return None
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/litellm_client_poc_async.py
Issues: 1

#### Line 301
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 298

**Context:**
```python
        # Test 3: With timeout
        print("\nTest 3: Call with timeout")
        config3 = {
            "model": "max/text-general",
            "messages": [{"role": "user", "content": "Count to 10 slowly"}]
        }
        
        try:
            result3 = await llm_call_with_timeout(config3, timeout=5)
            print(f"Got result: {result3}")
except Exception as e:
            print(f"Error: {e}")
            
        # Test 4: List active tasks
        print("\nTest 4: List active tasks")
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/poc_validation_strategies.py
Issues: 3

#### Line 94
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 87

**Context:**
```python
            return ValidationResult(valid=False, error="Content for JSON validation is empty or not a string.")
        
        # Use clean_json_string for flexible JSON extraction
        try:
            parsed_data = clean_json_string(content_str, return_dict=True)
            if parsed_data is None:
                # clean_json_string returns None if no JSON found
                return ValidationResult(valid=False, error="No valid JSON found in content",
                                        suggestions=["Ensure LLM is instructed for JSON output.", "Try using `response_format={'type': 'json_object'}`."])
            return ValidationResult(valid=True, debug_info={"parsed_json_type": type(parsed_data).__name__})
except Exception as e:
            return ValidationResult(valid=False, error=f"Error extracting JSON: {e}",
                                    suggestions=["Ensure LLM is instructed for JSON output.", "Try using `response_format={'type': 'json_object'}`."])

class PoCFieldPresentValidator(AsyncValidationStrategy):
```

#### Line 126
**Current:** `except Exception:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 122

**Context:**
```python
        elif hasattr(response, "choices") and response.choices: 
            content_str = response.choices[0].message.content
        
        if not isinstance(content_str, str) or not content_str.strip(): 
            return ValidationResult(valid=False, error="Content is empty/not string for field check.")
        # Use clean_json_string for flexible JSON extraction
        try: 
            data_to_check = clean_json_string(content_str, return_dict=True)
            if data_to_check is None:
                return ValidationResult(valid=False, error=f"No valid JSON found, cannot check field '{self._field_name}'.")
except Exception:
            return ValidationResult(valid=False, error=f"Error extracting JSON, cannot check field '{self._field_name}'.")
        if not isinstance(data_to_check, dict): 
            return ValidationResult(valid=False, error=f"JSON content not dict, cannot check field '{self._field_name}'.")
```

#### Line 272
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 221

**Context:**
```python
            # Add more sophisticated success criteria checks here as needed

            if is_valid:
                logger.success(f"[{self.name}] Agent task validation PASSED. Agent reasoning: {reasoning}")
                return ValidationResult(valid=True, debug_info={"agent_report": agent_report})
            else:
                logger.warning(f"[{self.name}] Agent task validation FAILED. Final Reasoning: {reasoning}")
                return ValidationResult(valid=False, error=f"Agent validation failed: {reasoning}", 
                                        suggestions=[f"Review agent report. Agent reasoning: {agent_report.get('reasoning', 'N/A')[:200]}..."],
                                        debug_info={"agent_report": agent_report})
except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response.")
            return ValidationResult(valid=False, error=f"[{self.name}] Critical error processing agent response: {e}", debug_info={"raw_agent_response": str(agent_response_dict)})
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/reconstruct_tests.py
Issues: 1

#### Line 110
**Current:** `except:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 107

**Context:**
```python
        else:
            current_test += char
    elif char == '}':
        current_test += char
        brace_count -= 1
        if brace_count == 0 and in_test:
            # Try to parse this test
            try:
                test_obj = json.loads(current_test)
                test_cases.append(test_obj)
except:
                print(f"Failed to parse test case {len(test_cases) + 1}")
            current_test = ""
            in_test = False
    elif in_test:
```

### src/llm_call/proof_of_concept/archive/root_cleanup/v4_claude_validator/safe_test_loader.py
Issues: 3

#### Line 76
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 63

**Context:**
```python
                
            # First attempt: Standard JSON parse
            try:
                data = json.loads(content)
                logger.success(f"Successfully loaded {len(data)} tests using standard JSON parser")
                return self._validate_test_structure(data), self.errors, self.warnings
            except json.JSONDecodeError as e:
                logger.warning(f"Standard JSON parse failed: {e}")
                self.warnings.append(f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}")
except Exception as e:
            self.errors.append(f"Failed to read file: {e}")
            return [], self.errors, self.warnings
            
        # Strategy 2: Try to fix common issues
```

#### Line 134
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 111

**Context:**
```python
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel alarm
            
            if cleaned and isinstance(cleaned, list):
                logger.success(f"Recovered {len(cleaned)} tests using clean_json_string")
                self.warnings.append("Tests recovered using clean_json_string - structure may be altered")
                return self._validate_test_structure(cleaned), self.errors, self.warnings
        except TimeoutError:
            logger.warning("clean_json_string timed out")
            self.warnings.append("clean_json_string recovery timed out")
except Exception as e:
            logger.warning(f"clean_json_string failed: {e}")
            self.warnings.append(f"clean_json_string recovery failed: {e}")
            
        # All strategies failed
```

#### Line 218
**Current:** `except:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 213

**Context:**
```python
            # Balance braces
            brace_count = test_str.count('{') - test_str.count('}')
            if brace_count > 0:
                test_str += '}' * brace_count
                
            try:
                test_obj = json.loads(test_str)
                if self._is_valid_test(test_obj):
                    tests.append(test_obj)
                    logger.debug(f"Extracted test: {test_obj.get('test_case_id', 'unknown')}")
except:
                # Try with clean_json_string
                cleaned = clean_json_string(test_str, return_dict=True)
                if cleaned and self._is_valid_test(cleaned):
                    tests.append(cleaned)
```

### src/llm_call/proof_of_concept/async_polling_manager.py
Issues: 3

#### Line 211
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 187

**Context:**
```python
        except asyncio.CancelledError:
            # Handle cancellation
            await self._update_status(
                task_id,
                TaskStatus.CANCELLED,
                completed_at=time.time(),
                error="Task cancelled"
            )
            raise
except Exception as e:
            # Handle errors
            await self._update_status(
                task_id,
                TaskStatus.FAILED,
```

#### Line 389
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 382

**Context:**
```python
    async def _periodic_cleanup(self):
        """Periodically clean up old tasks."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff = time.time() - (self.cleanup_after_hours * 3600)
                
                await asyncio.to_thread(self._cleanup_old_tasks, cutoff)
except Exception as e:
                logger.error(f"Cleanup error: {e}")
                
    def _cleanup_old_tasks(self, cutoff: float):
        """Clean up tasks older than cutoff."""
```

#### Line 439
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 436

**Context:**
```python
        print(f"Submitted task: {task_id}")
        
        # Check status
        status = await manager.get_status(task_id)
        print(f"Initial status: {status.status.value}")
        
        # Wait for completion
        try:
            result = await manager.wait_for_task(task_id, timeout=30)
            print(f"Result: {result}")
except Exception as e:
            print(f"Error: {e}")
            
        # Check final status
        final_status = await manager.get_status(task_id)
```

### src/llm_call/proof_of_concept/claude_cli_via_api_poc_v1_working.py
Issues: 4

#### Line 131
**Current:** `except Exception as e_parse:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 115

**Context:**
```python
                            full_response_text += item["text"] # Accumulate text
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"] # This usually contains the full message
                        logger.info(f"[SERVER-SIDE PoC] Successfully extracted final 'result' content.")
                        # If the 'result' field is what we want, we can stop accumulating
                        # For this simple PoC, the last 'result' is typically the full one.
                    break # Assuming the first "success" result is the one we want
            except json.JSONDecodeError:
                logger.warning(f"[SERVER-SIDE PoC] Non-JSON line in stream: {stripped_line}")
except Exception as e_parse:
                logger.error(f"[SERVER-SIDE PoC] Error processing streamed JSON: {e_parse}")
        
        # If final_result_content wasn't found in a "result" message, use accumulated text
        if final_result_content is None and full_response_text:
```

#### Line 155
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 96

**Context:**
```python
            # Return None or raise an exception to indicate failure to the FastAPI endpoint handler
            return None # Or more specific error

    except subprocess.TimeoutExpired:
        logger.error("[SERVER-SIDE PoC] Claude process timed out.")
        if process: process.kill(); process.communicate()
        return None
    except FileNotFoundError:
        logger.error(f"[SERVER-SIDE PoC] Claude CLI executable not found at {claude_exe_path}. Cannot run Popen.")
        return None
except Exception as e:
        logger.exception(f"[SERVER-SIDE PoC] An error occurred while running Claude: {e}")
        return None
    finally:
        if process and process.poll() is None:
```

#### Line 256
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 239

**Context:**
```python
        logger.success("🎉 [PoC Client] Successfully received JSON response from PoC server!")
        
        if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
            assistant_message = response_data["choices"][0].get("message", {}).get("content", "")
            print("\n" + "="*30)
            print(f"💬 Claude (via PoC Server) says: '{assistant_message}'")
            print("="*30 + "\n")
        else:
            logger.warning(f"⚠️ [PoC Client] Response structure might be unexpected: {json.dumps(response_data, indent=2)}")
except Exception as e:
        logger.error(f"💥 [PoC Client] An error occurred: {e}")
        import traceback
        traceback.print_exc()
```

#### Line 329
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 325

**Context:**
```python
    # tries to manage its own loop in certain ways.
    # A more robust way for a single-file PoC like this is often:
    # 1. Start server (uvicorn command in one terminal)
    # 2. Run client (python this_script.py --client-only in another terminal)

    # However, let's try the programmatic approach first for self-containment.
    try:
        asyncio.run(main_self_contained_poc())
    except KeyboardInterrupt:
        logger.info("PoC interrupted by user.")
except Exception as e:
        logger.error(f"Main PoC runner encountered an error: {e}")
        import traceback
        traceback.print_exc()
    finally:
```

### src/llm_call/proof_of_concept/claude_cli_via_api_poc_v2_untested.py
Issues: 4

#### Line 141
**Current:** `except Exception as e_parse:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 125

**Context:**
```python
                            full_response_text += item["text"] # Accumulate text
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"] # This usually contains the full message
                        logger.info(f"[SERVER-SIDE PoC] Successfully extracted final 'result' content.")
                        # If the 'result' field is what we want, we can stop accumulating
                        # For this simple PoC, the last 'result' is typically the full one.
                    break # Assuming the first "success" result is the one we want
            except json.JSONDecodeError:
                logger.warning(f"[SERVER-SIDE PoC] Non-JSON line in stream: {stripped_line}")
except Exception as e_parse:
                logger.error(f"[SERVER-SIDE PoC] Error processing streamed JSON: {e_parse}")
        
        # If final_result_content wasn't found in a "result" message, use accumulated text
        if final_result_content is None and full_response_text:
```

#### Line 165
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 106

**Context:**
```python
            # Return None or raise an exception to indicate failure to the FastAPI endpoint handler
            return None # Or more specific error

    except subprocess.TimeoutExpired:
        logger.error("[SERVER-SIDE PoC] Claude process timed out.")
        if process: process.kill(); process.communicate()
        return None
    except FileNotFoundError:
        logger.error(f"[SERVER-SIDE PoC] Claude CLI executable not found at {claude_exe_path}. Cannot run Popen.")
        return None
except Exception as e:
        logger.exception(f"[SERVER-SIDE PoC] An error occurred while running Claude: {e}")
        return None
    finally:
        if process and process.poll() is None:
```

#### Line 266
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 249

**Context:**
```python
        logger.success("🎉 [PoC Client] Successfully received JSON response from PoC server!")
        
        if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
            assistant_message = response_data["choices"][0].get("message", {}).get("content", "")
            print("\n" + "="*30)
            print(f"💬 Claude (via PoC Server) says: '{assistant_message}'")
            print("="*30 + "\n")
        else:
            logger.warning(f"⚠️ [PoC Client] Response structure might be unexpected: {json.dumps(response_data, indent=2)}")
except Exception as e:
        logger.error(f"💥 [PoC Client] An error occurred: {e}")
        import traceback
        traceback.print_exc()
```

#### Line 339
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 335

**Context:**
```python
    # tries to manage its own loop in certain ways.
    # A more robust way for a single-file PoC like this is often:
    # 1. Start server (uvicorn command in one terminal)
    # 2. Run client (python this_script.py --client-only in another terminal)

    # However, let's try the programmatic approach first for self-containment.
    try:
        asyncio.run(main_self_contained_poc())
    except KeyboardInterrupt:
        logger.info("PoC interrupted by user.")
except Exception as e:
        logger.error(f"Main PoC runner encountered an error: {e}")
        import traceback
        traceback.print_exc()
    finally:
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_01_claude_proxy_routing.py
Issues: 2

#### Line 192
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 163

**Context:**
```python
            logger.success(f" Routing successful: {route_type}")
            logger.info(f"API Base: {result['api_base']}")
            logger.info(f"Message count: {result['message_count']}")
            logger.info(f"Has system message: {result['has_system_message']}")
            
            # Validate routing decision
            if not result["routing_success"]:
                result["error"] = "Expected claude_proxy route for max/* model"
                logger.error(f" {result['error']}")
except Exception as e:
            logger.exception(f"Error in test case {test_case['test_case_id']}")
            result = {
                "test_case_id": test_case["test_case_id"],
                "routing_success": False,
```

#### Line 256
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 252

**Context:**
```python
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic routing functionality
    total_tests += 1
    try:
        success = asyncio.run(test_claude_proxy_routing())
        if not success:
            all_validation_failures.append("Basic routing tests failed")
except Exception as e:
        all_validation_failures.append(f"Routing test exception: {str(e)}")
    
    # Test 2: Edge cases
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_02_litellm_routing.py
Issues: 2

#### Line 271
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 237

**Context:**
```python
            # Log results
            logger.info(f"Model: {config.get('model')}")
            logger.info(f"Detected Provider: {result['detected_provider']}")
            logger.info(f"Expected Provider: {result['expected_provider']}")
            logger.info(f"Provider Match: {'' if result['provider_match'] else ''}")
            logger.info(f"Configuration Valid: {'' if is_valid else ''}")
            if error_msg:
                logger.warning(f"Validation Error: {error_msg}")
            logger.info(f"Routing Time: {result['routing_time_ms']:.3f}ms")
except Exception as e:
            logger.exception(f"Error in test case {test_case['test_case_id']}")
            result = {
                "test_case_id": test_case["test_case_id"],
                "provider_match": False,
```

#### Line 320
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 314

**Context:**
```python
    total_tests = 0
    
    # Test 1: Basic LiteLLM routing
    total_tests += 1
    try:
        # Note: This will fail if API keys are not set, which is expected
        success = asyncio.run(test_litellm_routing())
        if not success:
            logger.warning("Some LiteLLM routing tests failed (likely due to missing API keys)")
            # Don't count as failure if it's just missing API keys
except Exception as e:
        all_validation_failures.append(f"LiteLLM routing test exception: {str(e)}")
    
    # Test 2: Provider detection edge cases
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_03_message_conversion.py
Issues: 2

#### Line 381
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 313

**Context:**
```python
            
            if success:
                logger.success(f"✅ {test_case['name']} passed")
            else:
                logger.error(f"❌ {test_case['name']} failed:")
                for error in errors:
                    logger.error(f"   - {error}")
            
            logger.debug(f"Converted messages: {json.dumps(messages, indent=2)}")
except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            result = {
                "test": test_case["name"],
                "success": False,
```

#### Line 415
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 412

**Context:**
```python
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Message conversion pipeline
    total_tests += 1
    try:
        if not test_message_conversions():
            all_validation_failures.append("Message conversion tests failed")
except Exception as e:
        all_validation_failures.append(f"Conversion test exception: {str(e)}")
    
    # Test 2: Edge cases
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_04_routing_errors.py
Issues: 2

#### Line 329
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 297

**Context:**
```python
                if not success:
                    logger.error(f" Expected success but got error: {result.get('error_message')}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected success"})
                else:
                    if use_fallback and result.get("_fallback_used"):
                        logger.success(f" Successfully used fallback model")
                    else:
                        logger.success(f" Routing succeeded")
                    results.append({"test": test_case["name"], "passed": True})
except Exception as e:
            logger.exception(f"Unexpected error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
```

#### Line 363
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 360

**Context:**
```python
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Error handling scenarios
    total_tests += 1
    try:
        if not test_error_handling():
            all_validation_failures.append("Error handling tests failed")
except Exception as e:
        all_validation_failures.append(f"Error handling test exception: {str(e)}")
    
    # Test 2: Error type detection
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_05_routing_performance.py
Issues: 2

#### Line 353
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 349

**Context:**
```python
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Comprehensive performance tests
    total_tests += 1
    try:
        meets_target = asyncio.run(run_performance_tests())
        if not meets_target:
            all_validation_failures.append("Performance target not met (P95 > 50ms)")
except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
    
    # Test 2: Optimization strategies
    total_tests += 1
```

#### Line 361
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 358

**Context:**
```python
        if not meets_target:
            all_validation_failures.append("Performance target not met (P95 > 50ms)")
    except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
    
    # Test 2: Optimization strategies
    total_tests += 1
    try:
        if not test_optimization_strategies():
            all_validation_failures.append("Optimization strategies too slow")
except Exception as e:
        all_validation_failures.append(f"Optimization test exception: {str(e)}")
    
    # Test 3: Cache effectiveness
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_06_json_parsing.py
Issues: 2

#### Line 297
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 263

**Context:**
```python
            )
            
            if not is_valid:
                logger.error(f" Validation failed: {validation_error}")
                results.append({"test": test_case["name"], "passed": False, "reason": validation_error})
            else:
                logger.success(f" JSON parsed and validated successfully")
                logger.debug(f"Parsed content: {json.dumps(json_obj, indent=2)}")
                results.append({"test": test_case["name"], "passed": True})
except Exception as e:
            logger.exception(f"Unexpected error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
```

#### Line 331
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 328

**Context:**
```python
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: JSON parsing functionality
    total_tests += 1
    try:
        if not test_json_parsing():
            all_validation_failures.append("JSON parsing tests failed")
except Exception as e:
        all_validation_failures.append(f"JSON parsing test exception: {str(e)}")
    
    # Test 2: Edge cases
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_07_field_presence.py
Issues: 2

#### Line 341
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 320

**Context:**
```python
                    logger.error(f" Validation failed: {errors}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected success"})
            else:
                if not all_valid:
                    logger.success(f" Expected validation failure: {errors}")
                    results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error(f" Expected failure but validation passed")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected failure"})
except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
```

#### Line 375
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 372

**Context:**
```python
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Field presence functionality
    total_tests += 1
    try:
        if not test_field_presence():
            all_validation_failures.append("Field presence tests failed")
except Exception as e:
        all_validation_failures.append(f"Field presence test exception: {str(e)}")
    
    # Test 2: Complex nested paths
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_08_nested_fields.py
Issues: 2

#### Line 449
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 419

**Context:**
```python
                    if test_case.get("expect_error_contains") and test_case["expect_error_contains"] in error_str:
                        logger.success(f" Got expected error containing '{test_case['expect_error_contains']}'")
                        results.append({"test": test_case["name"], "passed": True})
                    else:
                        logger.error(f" Got errors but not the expected ones: {errors}")
                        results.append({"test": test_case["name"], "passed": False, "reason": "Wrong error"})
                else:
                    logger.error(" Expected errors but validation passed")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected errors"})
except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
```

#### Line 483
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 480

**Context:**
```python
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Nested validation functionality
    total_tests += 1
    try:
        if not test_nested_validation():
            all_validation_failures.append("Nested validation tests failed")
except Exception as e:
        all_validation_failures.append(f"Nested validation test exception: {str(e)}")
    
    # Test 2: Schema generation
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_09_schema_validation.py
Issues: 2

#### Line 496
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 458

**Context:**
```python
                        else:
                            logger.error(f"❌ Expected {test_case['expect_error_count']} errors, got {len(errors)}")
                            results.append({"test": test_case["name"], "passed": False, "reason": "Wrong error count"})
                    else:
                        logger.success(f"✅ Validation failed as expected ({len(errors)} errors)")
                        results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error("❌ Expected errors but validation passed")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected errors"})
except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
```

#### Line 530
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 527

**Context:**
```python
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Schema validation functionality
    total_tests += 1
    try:
        if not test_schema_validation():
            all_validation_failures.append("Schema validation tests failed")
except Exception as e:
        all_validation_failures.append(f"Schema validation test exception: {str(e)}")
    
    # Test 2: Complex schema features
    total_tests += 1
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_10_json_errors.py
Issues: 4

#### Line 401
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 398

**Context:**
```python
        ("Very long strings", '{"data": "' + "x" * 10000 + '"}')
    ]
    
    logger.info("\nTesting edge cases...")
    all_handled = True
    
    for name, test_input in edge_cases:
        try:
            data, errors, fallback = handler.parse_with_recovery(test_input)
            logger.info(f"✅ {name}: Handled successfully (fallback: {fallback})")
except Exception as e:
            logger.error(f"❌ {name}: Unhandled exception: {e}")
            all_handled = False
    
    return all_handled
```

#### Line 420
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 415

**Context:**
```python
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Error handling
    total_tests += 1
    try:
        if test_json_error_handling():
            logger.success("✅ JSON error handling tests passed")
        else:
            all_validation_failures.append("JSON error handling tests failed")
except Exception as e:
        all_validation_failures.append(f"JSON error handling exception: {str(e)}")
        logger.error(f"Exception in error handling test: {e}")
        traceback.print_exc()
```

#### Line 432
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 427

**Context:**
```python
        logger.error(f"Exception in error handling test: {e}")
        traceback.print_exc()
    
    # Test 2: Performance
    total_tests += 1
    try:
        if test_performance():
            logger.success("✅ Performance test passed")
        else:
            all_validation_failures.append("Performance test failed (>100ms)")
except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
        logger.error(f"Exception in performance test: {e}")
    
    # Test 3: Edge cases
```

#### Line 443
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 438

**Context:**
```python
        all_validation_failures.append(f"Performance test exception: {str(e)}")
        logger.error(f"Exception in performance test: {e}")
    
    # Test 3: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge case handling passed")
        else:
            all_validation_failures.append("Edge case handling failed")
except Exception as e:
        all_validation_failures.append(f"Edge case test exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_11_image_encoding.py
Issues: 8

#### Line 168
**Current:** `except Exception:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 165

**Context:**
```python
        mime_type = mimetypes.guess_type(str(image_path))[0]
        if mime_type:
            for fmt, mime in self.SUPPORTED_FORMATS.items():
                if mime == mime_type:
                    return fmt
        
        # Use PIL as fallback
        try:
            with Image.open(image_path) as img:
                return img.format.lower()
except Exception:
            return "unknown"
    
    def decode_base64_image(self, encoded_str: str) -> Tuple[bytes, str]:
        """
```

#### Line 334
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 321

**Context:**
```python
                
                # Verify encoding
                if result["encoded"].startswith("data:"):
                    decoded_data, fmt = encoder.decode_base64_image(result["encoded"])
                    if len(decoded_data) > 0:
                        logger.success(f"✅ Successfully decoded {len(decoded_data)} bytes")
                        results.append({"test": f"base64_{img_path.suffix}", "passed": True})
                    else:
                        logger.error(f"❌ Failed to decode")
                        results.append({"test": f"base64_{img_path.suffix}", "passed": False})
except Exception as e:
                logger.error(f"❌ Failed to encode {img_path}: {e}")
                results.append({"test": f"base64_{img_path.suffix}", "passed": False})
        
        # Test URL encoding
```

#### Line 349
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 341

**Context:**
```python
        logger.info("\nTesting URL encoding...")
        for img_path in test_images[:1]:  # Just test one
            try:
                result = encoder.encode_image(img_path, "url")
                if result["encoded"].startswith("file://"):
                    logger.success(f"✅ URL encoded: {result['encoded']}")
                    results.append({"test": "url_encoding", "passed": True})
                else:
                    logger.error(f"❌ Invalid URL: {result['encoded']}")
                    results.append({"test": "url_encoding", "passed": False})
except Exception as e:
                logger.error(f"❌ URL encoding failed: {e}")
                results.append({"test": "url_encoding", "passed": False})
        
        # Test optimization
```

#### Line 363
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 359

**Context:**
```python
        # Test optimization
        logger.info("\nTesting image optimization...")
        large_img = Image.new('RGB', (3000, 3000), color='yellow')
        large_path = Path("test_large.jpg")
        large_img.save(large_path, format='JPEG')
        
        try:
            optimized = encoder.optimize_image(large_path, max_size=500*1024)  # 500KB limit
            logger.success(f"✅ Optimized from {large_path.stat().st_size} to {len(optimized)} bytes")
            results.append({"test": "optimization", "passed": len(optimized) <= 500*1024})
except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            results.append({"test": "optimization", "passed": False})
        finally:
            large_path.unlink(missing_ok=True)
```

#### Line 376
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 372

**Context:**
```python
        finally:
            large_path.unlink(missing_ok=True)
        
        # Test API formatting
        logger.info("\nTesting API formatting...")
        for api_type in ["openai", "anthropic", "litellm"]:
            try:
                formatted = encoder.format_for_api(test_images[0], api_type)
                logger.success(f"✅ Formatted for {api_type}: {list(formatted.keys())}")
                results.append({"test": f"format_{api_type}", "passed": True})
except Exception as e:
                logger.error(f"❌ Formatting for {api_type} failed: {e}")
                results.append({"test": f"format_{api_type}", "passed": False})
        
    finally:
```

#### Line 472
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 465

**Context:**
```python
    
    # Test 1: Image encoding
    total_tests += 1
    try:
        passed, results = test_image_encoding()
        if passed:
            logger.success("✅ Image encoding tests passed")
        else:
            failed_tests = [r["test"] for r in results if not r["passed"]]
            all_validation_failures.append(f"Image encoding tests failed: {failed_tests}")
except Exception as e:
        all_validation_failures.append(f"Image encoding exception: {str(e)}")
        logger.error(f"Exception in encoding test: {e}")
    
    # Test 2: Format detection
```

#### Line 483
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 478

**Context:**
```python
        all_validation_failures.append(f"Image encoding exception: {str(e)}")
        logger.error(f"Exception in encoding test: {e}")
    
    # Test 2: Format detection
    total_tests += 1
    try:
        if test_format_detection():
            logger.success("✅ Format detection tests passed")
        else:
            all_validation_failures.append("Format detection tests failed")
except Exception as e:
        all_validation_failures.append(f"Format detection exception: {str(e)}")
        logger.error(f"Exception in format test: {e}")
    
    # Test 3: Performance
```

#### Line 494
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 489

**Context:**
```python
        all_validation_failures.append(f"Format detection exception: {str(e)}")
        logger.error(f"Exception in format test: {e}")
    
    # Test 3: Performance
    total_tests += 1
    try:
        if test_performance():
            logger.success("✅ Performance test passed")
        else:
            all_validation_failures.append("Performance test failed (>100ms)")
except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
        logger.error(f"Exception in performance test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_12_size_optimization.py
Issues: 6

#### Line 329
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 325

**Context:**
```python
        **kwargs
    ) -> List[Dict[str, any]]:
        """Optimize multiple images."""
        results = []
        
        for path in image_paths:
            try:
                result = self.optimize_for_api(path, **kwargs)
                result['path'] = str(path)
                results.append(result)
except Exception as e:
                logger.error(f"Failed to optimize {path}: {e}")
                results.append({
                    'path': str(path),
                    'error': str(e)
```

#### Line 575
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 570

**Context:**
```python
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic optimization
    total_tests += 1
    try:
        if test_basic_optimization():
            logger.success(" Basic optimization tests passed")
        else:
            all_validation_failures.append("Basic optimization tests failed")
except Exception as e:
        all_validation_failures.append(f"Basic optimization exception: {str(e)}")
        logger.error(f"Exception in basic test: {e}")
    
    # Test 2: Target size optimization
```

#### Line 586
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 581

**Context:**
```python
        all_validation_failures.append(f"Basic optimization exception: {str(e)}")
        logger.error(f"Exception in basic test: {e}")
    
    # Test 2: Target size optimization
    total_tests += 1
    try:
        if test_target_size_optimization():
            logger.success(" Target size optimization tests passed")
        else:
            all_validation_failures.append("Target size optimization tests failed")
except Exception as e:
        all_validation_failures.append(f"Target size exception: {str(e)}")
        logger.error(f"Exception in target size test: {e}")
    
    # Test 3: Format conversion
```

#### Line 597
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 592

**Context:**
```python
        all_validation_failures.append(f"Target size exception: {str(e)}")
        logger.error(f"Exception in target size test: {e}")
    
    # Test 3: Format conversion
    total_tests += 1
    try:
        if test_format_conversion():
            logger.success(" Format conversion tests passed")
        else:
            all_validation_failures.append("Format conversion tests failed")
except Exception as e:
        all_validation_failures.append(f"Format conversion exception: {str(e)}")
        logger.error(f"Exception in format test: {e}")
    
    # Test 4: Edge cases
```

#### Line 608
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 603

**Context:**
```python
        all_validation_failures.append(f"Format conversion exception: {str(e)}")
        logger.error(f"Exception in format test: {e}")
    
    # Test 4: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success(" Edge case tests passed")
        else:
            all_validation_failures.append("Edge case tests failed")
except Exception as e:
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Test 5: Performance
```

#### Line 619
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 614

**Context:**
```python
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Test 5: Performance
    total_tests += 1
    try:
        if test_performance():
            logger.success(" Performance test passed")
        else:
            all_validation_failures.append("Performance test failed (>1000ms)")
except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
        logger.error(f"Exception in performance test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_13_multimodal_messages.py
Issues: 7

#### Line 425
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 410

**Context:**
```python
                )
                
                # Verify structure
                if "messages" in result and result["content_count"] == 2:
                    logger.success(f"✅ {provider}: Formatted correctly with {result['content_count']} content items")
                    results.append(True)
                else:
                    logger.error(f"❌ {provider}: Invalid format")
                    results.append(False)
except Exception as e:
                logger.error(f"❌ {provider}: {e}")
                results.append(False)
    
    finally:
```

#### Line 571
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 557

**Context:**
```python
                    to_fmt
                )
                
                if converted["formatted_for"] == to_fmt:
                    logger.success(f"✅ Converted {from_fmt} → {to_fmt}")
                    results.append(True)
                else:
                    logger.error(f"❌ Conversion {from_fmt} → {to_fmt} failed")
                    results.append(False)
except Exception as e:
                logger.error(f"❌ Conversion error: {e}")
                results.append(False)
                
    finally:
```

#### Line 663
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 658

**Context:**
```python
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic formatting
    total_tests += 1
    try:
        if test_basic_formatting():
            logger.success("✅ Basic formatting tests passed")
        else:
            all_validation_failures.append("Basic formatting tests failed")
except Exception as e:
        all_validation_failures.append(f"Basic formatting exception: {str(e)}")
        logger.error(f"Exception in basic test: {e}")
    
    # Test 2: Multiple images
```

#### Line 674
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 669

**Context:**
```python
        all_validation_failures.append(f"Basic formatting exception: {str(e)}")
        logger.error(f"Exception in basic test: {e}")
    
    # Test 2: Multiple images
    total_tests += 1
    try:
        if test_multiple_images():
            logger.success("✅ Multiple images tests passed")
        else:
            all_validation_failures.append("Multiple images tests failed")
except Exception as e:
        all_validation_failures.append(f"Multiple images exception: {str(e)}")
        logger.error(f"Exception in multiple images test: {e}")
    
    # Test 3: System prompts
```

#### Line 685
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 680

**Context:**
```python
        all_validation_failures.append(f"Multiple images exception: {str(e)}")
        logger.error(f"Exception in multiple images test: {e}")
    
    # Test 3: System prompts
    total_tests += 1
    try:
        if test_system_prompts():
            logger.success("✅ System prompts tests passed")
        else:
            all_validation_failures.append("System prompts tests failed")
except Exception as e:
        all_validation_failures.append(f"System prompts exception: {str(e)}")
        logger.error(f"Exception in system prompts test: {e}")
    
    # Test 4: Format conversion
```

#### Line 696
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 691

**Context:**
```python
        all_validation_failures.append(f"System prompts exception: {str(e)}")
        logger.error(f"Exception in system prompts test: {e}")
    
    # Test 4: Format conversion
    total_tests += 1
    try:
        if test_format_conversion():
            logger.success("✅ Format conversion tests passed")
        else:
            all_validation_failures.append("Format conversion tests failed")
except Exception as e:
        all_validation_failures.append(f"Format conversion exception: {str(e)}")
        logger.error(f"Exception in format conversion test: {e}")
    
    # Test 5: Edge cases
```

#### Line 707
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 702

**Context:**
```python
        all_validation_failures.append(f"Format conversion exception: {str(e)}")
        logger.error(f"Exception in format conversion test: {e}")
    
    # Test 5: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge cases tests passed")
        else:
            all_validation_failures.append("Edge cases tests failed")
except Exception as e:
        all_validation_failures.append(f"Edge cases exception: {str(e)}")
        logger.error(f"Exception in edge cases test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_14_agent_delegation.py
Issues: 4

#### Line 427
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 425

**Context:**
```python
    
    async def _run_agent_validation(
        self,
        agent: ValidationAgent,
        data: Any,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Run validation for a single agent."""
        try:
            return await agent.validate(data, context)
except Exception as e:
            logger.error(f"Agent {agent.name} failed: {e}")
            return ValidationResult(
                agent_name=agent.name,
                valid=False,
```

#### Line 635
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 630

**Context:**
```python
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Agent delegation
    total_tests += 1
    try:
        if await test_agent_delegation():
            logger.success(" Agent delegation tests passed")
        else:
            all_validation_failures.append("Agent delegation tests failed")
except Exception as e:
        all_validation_failures.append(f"Agent delegation exception: {str(e)}")
        logger.error(f"Exception in delegation test: {e}")
    
    # Test 2: Concurrent validation
```

#### Line 646
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 641

**Context:**
```python
        all_validation_failures.append(f"Agent delegation exception: {str(e)}")
        logger.error(f"Exception in delegation test: {e}")
    
    # Test 2: Concurrent validation
    total_tests += 1
    try:
        if await test_concurrent_validation():
            logger.success(" Concurrent validation tests passed")
        else:
            all_validation_failures.append("Concurrent validation tests failed")
except Exception as e:
        all_validation_failures.append(f"Concurrent validation exception: {str(e)}")
        logger.error(f"Exception in concurrent test: {e}")
    
    # Test 3: Error handling
```

#### Line 657
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 652

**Context:**
```python
        all_validation_failures.append(f"Concurrent validation exception: {str(e)}")
        logger.error(f"Exception in concurrent test: {e}")
    
    # Test 3: Error handling
    total_tests += 1
    try:
        if await test_error_handling():
            logger.success(" Error handling tests passed")
        else:
            all_validation_failures.append("Error handling tests failed")
except Exception as e:
        all_validation_failures.append(f"Error handling exception: {str(e)}")
        logger.error(f"Exception in error handling test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_15_specialized_agents.py
Issues: 4

#### Line 731
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 710

**Context:**
```python
                if all_low:
                    logger.success("✅ Non-safety scores low as expected")
                    results.append(True)
                else:
                    logger.error(f"❌ Expected low non-safety scores, got: {non_safety_scores}")
                    results.append(False)
            else:
                logger.success("✅ Handled edge case without errors")
                results.append(True)
except Exception as e:
            logger.error(f"❌ Error handling edge case: {e}")
            results.append(False)
    
    return all(results)
```

#### Line 750
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 745

**Context:**
```python
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Specialized agents
    total_tests += 1
    try:
        if test_specialized_agents():
            logger.success("✅ Specialized agents tests passed")
        else:
            all_validation_failures.append("Specialized agents tests failed")
except Exception as e:
        all_validation_failures.append(f"Specialized agents exception: {str(e)}")
        logger.error(f"Exception in specialized test: {e}")
    
    # Test 2: Agent combinations
```

#### Line 761
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 756

**Context:**
```python
        all_validation_failures.append(f"Specialized agents exception: {str(e)}")
        logger.error(f"Exception in specialized test: {e}")
    
    # Test 2: Agent combinations
    total_tests += 1
    try:
        if test_agent_combinations():
            logger.success("✅ Agent combination tests passed")
        else:
            all_validation_failures.append("Agent combination tests failed")
except Exception as e:
        all_validation_failures.append(f"Agent combination exception: {str(e)}")
        logger.error(f"Exception in combination test: {e}")
    
    # Test 3: Edge cases
```

#### Line 772
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 767

**Context:**
```python
        all_validation_failures.append(f"Agent combination exception: {str(e)}")
        logger.error(f"Exception in combination test: {e}")
    
    # Test 3: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge case tests passed")
        else:
            all_validation_failures.append("Edge case tests failed")
except Exception as e:
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_16_result_aggregation.py
Issues: 4

#### Line 563
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 549

**Context:**
```python
            logger.info(f"Decision: {result.decision.value}")
            logger.info(f"Reasoning: {result.reasoning}")
            
            if case.get("expect_reject") and result.decision == Decision.REJECT:
                logger.success("✅ Correctly rejected as expected")
                results.append(True)
            else:
                logger.success("✅ Handled edge case successfully")
                results.append(True)
except Exception as e:
            logger.error(f"❌ Error handling edge case: {e}")
            results.append(False)
    
    return all(results)
```

#### Line 635
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 630

**Context:**
```python
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Aggregation strategies
    total_tests += 1
    try:
        if test_aggregation_strategies():
            logger.success("✅ Aggregation strategies tests passed")
        else:
            all_validation_failures.append("Aggregation strategies tests failed")
except Exception as e:
        all_validation_failures.append(f"Aggregation strategies exception: {str(e)}")
        logger.error(f"Exception in strategies test: {e}")
    
    # Test 2: Edge cases
```

#### Line 646
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 641

**Context:**
```python
        all_validation_failures.append(f"Aggregation strategies exception: {str(e)}")
        logger.error(f"Exception in strategies test: {e}")
    
    # Test 2: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge case tests passed")
        else:
            all_validation_failures.append("Edge case tests failed")
except Exception as e:
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Test 3: Decision thresholds
```

#### Line 657
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 652

**Context:**
```python
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Test 3: Decision thresholds
    total_tests += 1
    try:
        if test_decision_thresholds():
            logger.success("✅ Decision threshold tests passed")
        else:
            all_validation_failures.append("Decision threshold tests failed")
except Exception as e:
        all_validation_failures.append(f"Decision threshold exception: {str(e)}")
        logger.error(f"Exception in threshold test: {e}")
    
    # Final result
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_26_basic_retry.py
Issues: 1

#### Line 173
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 158

**Context:**
```python
                logger.success(f" Success on attempt {attempt}")
                
                return RetryResult(
                    success=True,
                    attempts=attempts,
                    total_time=total_time,
                    final_result=result,
                    delays=delays
                )
except Exception as e:
                if not self.should_retry(e) or attempt == self.config.max_attempts:
                    # Non-retryable error or max attempts reached
                    total_time = time.time() - start_time
                    logger.error(f" Failed after {attempt} attempts: {e}")
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_27_exponential_backoff.py
Issues: 6

#### Line 205
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 196

**Context:**
```python
        # Execute the function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._record_success()
            return result
except Exception as e:
            if not self._is_excluded_exception(e):
                self._record_failure(e)
            raise
```

#### Line 303
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 295

**Context:**
```python
    # Make calls until circuit opens
    for i in range(4):
        try:
            await breaker.call(service.make_request, f"data_{i}")
        except CircuitOpenError:
            logger.info(f"Call {i+1}: Circuit is open")
            if i == 3:  # Should be open on 4th call
                passed += 1
                logger.success("✅ Circuit opened correctly after threshold")
            break
except Exception as e:
            logger.warning(f"Call {i+1}: {e}")
    else:
        failed += 1
        logger.error("❌ Circuit did not open as expected")
```

#### Line 325
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 322

**Context:**
```python
    await asyncio.sleep(2.5)
    
    # Service should succeed now
    service.should_fail = False
    
    # Make successful calls to close circuit
    for i in range(3):
        try:
            result = await breaker.call(service.make_request, f"recovery_{i}")
            logger.success(f"Call {i+1}: Success - {result}")
except Exception as e:
            logger.error(f"Call {i+1}: {e}")
    
    if breaker.state == CircuitState.CLOSED:
        passed += 1
```

#### Line 352
**Current:** `except:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 350

**Context:**
```python
        timeout=1.0
    )
    breaker2 = CircuitBreaker("test3", config2)
    service2 = TestService()
    
    # Open the circuit
    service2.should_fail = True
    for i in range(3):
        try:
            await breaker2.call(service2.make_request, "fail")
except:
            pass
    
    # Wait for timeout
    await asyncio.sleep(1.5)
```

#### Line 361
**Current:** `except Exception:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 359

**Context:**
```python
            await breaker2.call(service2.make_request, "fail")
        except:
            pass
    
    # Wait for timeout
    await asyncio.sleep(1.5)
    
    # Still failing - should return to open
    try:
        await breaker2.call(service2.make_request, "still_fail")
except Exception:
        pass
    
    if breaker2.state == CircuitState.OPEN:
        passed += 1
```

#### Line 391
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 386

**Context:**
```python
    
    # Pattern: fail, wait, fail, wait, fail (spread over time)
    service3.fail_pattern = [True, True, False, True, True]
    
    for i in range(5):
        try:
            await breaker3.call(service3.make_request, f"window_{i}")
            logger.success(f"Call {i+1}: Success")
        except CircuitOpenError:
            logger.info(f"Call {i+1}: Circuit open")
except Exception as e:
            logger.warning(f"Call {i+1}: {e}")
        
        if i < 4:
            await asyncio.sleep(0.8)  # Spread calls over time
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_29_human_escalation.py
Issues: 2

#### Line 263
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 209

**Context:**
```python
                        # Modify args based on human input
                        if human_result.modified_prompt:
                            # In real implementation, modify function args
                            pass
                        continue
                    elif human_result.decision == HumanDecision.ABORT:
                        raise HumanEscalationError(context)
                    else:
                        raise ValueError(f"Unhandled human decision: {human_result.decision}")
except Exception as e:
            if isinstance(e, HumanEscalationError):
                raise
            logger.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt >= max_retries:
```

#### Line 347
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 311

**Context:**
```python
                failed += 1
                logger.error(f" Expected {scenario['expected_decision'].value}, got {last_decision}")
                
        except HumanEscalationError as e:
            if scenario["expected_decision"] == HumanDecision.ABORT:
                passed += 1
                logger.success(" Correctly aborted after human review")
            else:
                failed += 1
                logger.error(f" Unexpected abort: {e}")
except Exception as e:
            failed += 1
            logger.error(f" Unexpected error: {e}")
    
    # Display statistics
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_30_debug_mode.py
Issues: 5

#### Line 179
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 159

**Context:**
```python
                validator_name,
                {
                    "valid": result.get("valid", False),
                    "duration_ms": duration,
                    "result_preview": str(result)[:200] if self.debug_context.log_payloads else "<redacted>"
                }
            )
            
            return result
except Exception as e:
            # Stop timing
            duration = self.debug_context.stop_timer(f"validation_{validator_name}")
            
            # Log error
```

#### Line 300
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 227

**Context:**
```python
                            "BACKOFF_DELAY",
                            "RetryManager",
                            {
                                "attempt": attempt + 1,
                                "delay_seconds": delay,
                                "next_attempt": attempt + 2
                            }
                        )
                        await asyncio.sleep(delay)
except Exception as e:
                self.debug_context.add_event(
                    "ATTEMPT_ERROR",
                    "RetryManager",
                    {"attempt": attempt + 1},
```

#### Line 437
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 430

**Context:**
```python
    debug_ctx1 = DebugContext(session_id="TEST-001")
    retry_mgr1 = DebugRetryManager(debug_ctx1)
    
    try:
        result = await retry_mgr1.retry_with_debug(
            successful_function,
            [{"name": "SuccessValidator", "func": validate_success}],
            max_attempts=3
        )
        logger.success(" Test 1 passed")
except Exception as e:
        logger.error(f" Test 1 failed: {e}")
    
    # Test 2: Retry with eventual success
    logger.info("\n Test 2: Retry with eventual success")
```

#### Line 452
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 445

**Context:**
```python
    debug_ctx2 = DebugContext(session_id="TEST-002")
    retry_mgr2 = DebugRetryManager(debug_ctx2)
    
    try:
        result = await retry_mgr2.retry_with_debug(
            flaky_function,
            [{"name": "ValidValidator", "func": validate_valid}],
            max_attempts=5
        )
        logger.success(" Test 2 passed")
except Exception as e:
        logger.error(f" Test 2 failed: {e}")
    
    # Test 3: Complete failure
    logger.info("\n Test 3: Complete failure with debugging")
```

#### Line 467
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 460

**Context:**
```python
    debug_ctx3 = DebugContext(session_id="TEST-003")
    retry_mgr3 = DebugRetryManager(debug_ctx3)
    
    try:
        result = await retry_mgr3.retry_with_debug(
            failing_function,
            [{"name": "SuccessValidator", "func": validate_success}],
            max_attempts=2
        )
        logger.error(" Test 3 should have failed")
except Exception as e:
        logger.success(f" Test 3 correctly failed: {e}")
    
    # Generate debug reports
    logger.info("\n" + "=" * 60)
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_31_test_runner.py
Issues: 2

#### Line 189
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 159

**Context:**
```python
                else:
                    result.status = TestStatus.FAILED
                    failed_validations = [
                        v for v in validation_passed if not v.get("passed", False)
                    ]
                    result.error_message = f"Validation failed: {failed_validations}"
            else:
                # No validation - assume pass if we got a response
                result.status = TestStatus.PASSED if llm_response else TestStatus.FAILED
except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.stack_trace = self._get_stack_trace()
            logger.error(f"Test {test_case.test_case_id} failed with error: {e}")
```

#### Line 247
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 240

**Context:**
```python
            
            if val_type in self.validator_registry:
                validator = self.validator_registry[val_type]
                try:
                    is_valid = await validator(response, val_params)
                    results.append({
                        "type": val_type,
                        "passed": is_valid,
                        "params": val_params
                    })
except Exception as e:
                    results.append({
                        "type": val_type,
                        "passed": False,
                        "error": str(e),
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_33_performance_track.py
Issues: 1

#### Line 155
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 147

**Context:**
```python
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Collect snapshot
                snapshot = self._collect_snapshot()
                self.snapshots.append(snapshot)
                
                # Check for anomalies
                self._check_anomalies(snapshot)
except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(self.sampling_interval)
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_35_parallel_tests.py
Issues: 2

#### Line 188
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 171

**Context:**
```python
                    if result.get("success", False):
                        self.completed_tests.append(test.test_id)
                    else:
                        self.failed_tests.append(test.test_id)
                
                # Update stats
                execution_time = time.time() - start_time
                self.worker_stats[worker_id].tests_executed += 1
                self.worker_stats[worker_id].total_time += execution_time
except Exception as e:
                logger.error(f"Worker {worker_id} error on {test.test_id}: {e}")
                self.failed_tests.append(test.test_id)
                self.results[test.test_id] = {"success": False, "error": str(e)}
```

#### Line 220
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 203

**Context:**
```python
                result = await loop.run_in_executor(None, test.test_func)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
```

### src/llm_call/proof_of_concept/code/task_004_test_prompts/run_all_pocs.py
Issues: 1

#### Line 138
**Current:** `except Exception as e:`
**Suggested:** `except subprocess.SubprocessError:`
**Comment:** # Subprocess execution failed

**Try block starts at line:** 101

**Context:**
```python
                else:
                    # Show last bit of output for debugging
                    last_output = output[-200:] if output else "No output"
                    return False, f" No validation confirmation\n{last_output}"
            else:
                error_output = result.stderr[-200:] if result.stderr else "No error output"
                return False, f" Exit code {result.returncode}\n{error_output}"
                
        except subprocess.TimeoutExpired:
            return False, " Timeout (>30s)"
except Exception as e:
            return False, f" Error: {str(e)}"
    
    async def run_all(self):
        """Run all POCs and collect results."""
```

### src/llm_call/proof_of_concept/code/task_async_polling/poc_claude_cli_test.py
Issues: 2

#### Line 55
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 46

**Context:**
```python
    print(f"\nTrying: {path}")
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:100]}...")
        print(f"Stderr: {result.stderr[:100]}...")
    except subprocess.TimeoutExpired:
        print("Timed out")
    except FileNotFoundError:
        print("Command not found")
except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

# Check if it's an npm package
print("\nChecking NPM:")
```

#### Line 63
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 60

**Context:**
```python
    except FileNotFoundError:
        print("Command not found")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

# Check if it's an npm package
print("\nChecking NPM:")
try:
    result = subprocess.run(["npm", "list", "-g", "claude"], capture_output=True, text=True)
    print(f"NPM global packages: {result.stdout[:200]}")
except Exception as e:
    print(f"NPM check failed: {e}")
```

### src/llm_call/proof_of_concept/code/task_async_polling/poc_litellm_integration.py
Issues: 2

#### Line 101
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 84

**Context:**
```python
        cursor = conn.execute(
            "SELECT status, result FROM tasks WHERE task_id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        if row and row[0] == "completed":
            stored_result = json.loads(row[1])
            print(f" Verified in SQLite: {stored_result['choices'][0]['message']['content']}")
        conn.close()
except Exception as e:
        print(f" Error: {type(e).__name__}: {e}")
    
    # Test 2: Error handling
    print("\nTest 2: Error handling")
```

#### Line 113
**Current:** `except Exception as e:`
**Suggested:** `except sqlite3.Error:`
**Comment:** # Database operation failed

**Try block starts at line:** 111

**Context:**
```python
    
    # Test 2: Error handling
    print("\nTest 2: Error handling")
    error_task_id = await manager.submit_task({
        "model": "invalid-model-xxx",
        "messages": [{"role": "user", "content": "This should fail"}]
    })
    
    try:
        await manager.wait_for_task(error_task_id, timeout=10)
except Exception as e:
        print(f" Error handled correctly: {type(e).__name__}")
        
        # Check error in SQLite
        conn = sqlite3.connect(manager.db_path)
```

### src/llm_call/proof_of_concept/code/task_async_polling/poc_model_response_serialization.py
Issues: 2

#### Line 87
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 77

**Context:**
```python
    try:
        json_str = json.dumps(data)
        print(f" Successfully serialized to JSON ({len(json_str)} chars)")
        
        # Test deserialization
        loaded = json.loads(json_str)
        print(f" Successfully deserialized from JSON")
        if 'choices' in loaded and loaded['choices']:
            content = loaded['choices'][0].get('message', {}).get('content', 'N/A')
            print(f"  Content: {content}")
except Exception as e:
        print(f" JSON serialization failed: {e}")

except ImportError as e:
    print(f" Import error: {e}")
```

#### Line 93
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 32

**Context:**
```python
        print(f" Successfully deserialized from JSON")
        if 'choices' in loaded and loaded['choices']:
            content = loaded['choices'][0].get('message', {}).get('content', 'N/A')
            print(f"  Content: {content}")
    except Exception as e:
        print(f" JSON serialization failed: {e}")

except ImportError as e:
    print(f" Import error: {e}")
    print("  Make sure litellm is installed: uv add litellm")
except Exception as e:
    print(f" Unexpected error: {type(e).__name__}: {e}")

print("\n=== POC Complete ===")
```

### src/llm_call/proof_of_concept/code/task_async_polling/poc_sqlite_json.py
Issues: 3

#### Line 43
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 40

**Context:**
```python
        result TEXT
    )
""")

# Test 1: Simple dict
print("\nTest 1: Simple dict")
simple_dict = {"message": "Hello world", "status": "ok"}
try:
    conn.execute("INSERT INTO tasks VALUES (?, ?)", ("task1", json.dumps(simple_dict)))
    print(" Simple dict serialized successfully")
except Exception as e:
    print(f" Failed: {e}")

# Test 2: Complex nested structure (like LiteLLM response)
print("\nTest 2: Complex nested structure")
```

#### Line 68
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 59

**Context:**
```python
}
try:
    conn.execute("INSERT INTO tasks VALUES (?, ?)", ("task2", json.dumps(complex_dict)))
    print(" Complex dict serialized successfully")
    
    # Read it back
    cursor = conn.execute("SELECT result FROM tasks WHERE task_id = ?", ("task2",))
    stored_json = cursor.fetchone()[0]
    restored = json.loads(stored_json)
    print(f" Restored content: {restored['choices'][0]['message']['content']}")
except Exception as e:
    print(f" Failed: {e}")

# Test 3: Object with __dict__
print("\nTest 3: Object with __dict__")
```

#### Line 84
**Current:** `except Exception as e:`
**Suggested:** `except sqlite3.Error:`
**Comment:** # Database operation failed

**Try block starts at line:** 79

**Context:**
```python
class MockResponse:
    id: str
    choices: list
    
obj = MockResponse("test-123", [{"message": {"content": "Test"}}])
try:
    # Convert using __dict__
    obj_dict = obj.__dict__
    conn.execute("INSERT INTO tasks VALUES (?, ?)", ("task3", json.dumps(obj_dict)))
    print(" Object serialized via __dict__")
except Exception as e:
    print(f" Failed: {e}")

conn.close()
print("\nDone!")
```

### src/llm_call/proof_of_concept/full_v4_validation.py
Issues: 1

#### Line 135
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Generic exception handler

**Try block starts at line:** 89

**Context:**
```python
        else:
            return {
                "test_id": test_id,
                "model": model,
                "status": " FAILED",
                "duration": duration,
                "response": "No response",
                "description": description
            }
except Exception as e:
        duration = 0
        error_msg = str(e)
        
        # Check for known issues
```

### src/llm_call/proof_of_concept/litellm_client_poc.py
Issues: 2

#### Line 275
**Current:** `except Exception as e_val_init:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 269

**Context:**
```python
            strategy_params = val_conf.get("params", {})
            
            ValidatorClass = poc_strategy_registry.get(strategy_type_name)
            if ValidatorClass:
                try:
                    validator_instance = ValidatorClass(**strategy_params)
                    if hasattr(validator_instance, "set_llm_caller") and _recursive_llm_caller:
                         validator_instance.set_llm_caller(_recursive_llm_caller) 
                    active_validation_strategies.append(validator_instance)
                    logger.info(f"Loaded validator for '{model_name_for_logging}': {strategy_type_name} with params: {strategy_params}")
except Exception as e_val_init:
                    logger.error(f"Failed to instantiate validator '{strategy_type_name}' with params {strategy_params} for '{model_name_for_logging}': {e_val_init}")
            else:
                logger.warning(f"Unknown validation strategy type: '{strategy_type_name}' for model '{model_name_for_logging}'")
```

#### Line 331
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 217

**Context:**
```python
        logger.error(f"🚫 HUMAN REVIEW NEEDED for model '{model_name_for_logging}': {hrne.args[0]}") # hrne.args[0] is the message
        # Log more details if needed, hrne.last_response and hrne.validation_errors are available
        return {"error": "Human review needed", "details": str(hrne.args[0]), 
                "last_response": hrne.last_response, 
                "validation_errors": [ve.error for ve in hrne.validation_errors if hasattr(ve, 'error')]}
    except RetryError as re_outer: # Fallback if tenacity retries (within _execute_... if any) are re-raised
        final_exception = re_outer.last_attempt.exception()
        logger.error(f"❌ Call for model '{model_name_for_logging}' FAILED AFTER MAX RETRIES (Tenacity outer loop).")
        logger.error(f"   Last exception type: {type(final_exception).__name__}")
        logger.error(f"   Last exception details: {final_exception}")
except Exception as e:
        logger.error(f"💥 Unexpected error in llm_call orchestrator for model '{model_name_for_logging}': {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
    return None
```

### src/llm_call/proof_of_concept/litellm_client_poc_polling.py
Issues: 2

#### Line 202
**Current:** `except Exception as e_val_init:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 196

**Context:**
```python
            strategy_params = val_conf.get("params", {})
            
            ValidatorClass = poc_strategy_registry.get(strategy_type_name)
            if ValidatorClass:
                try:
                    validator_instance = ValidatorClass(**strategy_params)
                    if hasattr(validator_instance, "set_llm_caller") and _recursive_llm_caller:
                         validator_instance.set_llm_caller(_recursive_llm_caller) 
                    active_validation_strategies.append(validator_instance)
                    logger.info(f"Loaded validator for '{model_name_for_logging}': {strategy_type_name} with params: {strategy_params}")
except Exception as e_val_init:
                    logger.error(f"Failed to instantiate validator '{strategy_type_name}' with params {strategy_params} for '{model_name_for_logging}': {e_val_init}")
            else:
                logger.warning(f"Unknown validation strategy type: '{strategy_type_name}' for model '{model_name_for_logging}'")
```

#### Line 251
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 147

**Context:**
```python
    except PoCHumanReviewNeededError as hrne: 
        logger.error(f" HUMAN REVIEW NEEDED for model '{model_name_for_logging}': {hrne.args[0]}")
        return {"error": "Human review needed", "details": str(hrne.args[0]), 
                "last_response": hrne.last_response, 
                "validation_errors": [ve.error for ve in hrne.validation_errors if hasattr(ve, 'error')]}
    except RetryError as re_outer:
        final_exception = re_outer.last_attempt.exception()
        logger.error(f" Call for model '{model_name_for_logging}' FAILED AFTER MAX RETRIES (Tenacity outer loop).")
        logger.error(f"   Last exception type: {type(final_exception).__name__}")
        logger.error(f"   Last exception details: {final_exception}")
except Exception as e:
        logger.error(f" Unexpected error in llm_call orchestrator for model '{model_name_for_logging}': {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
    return None
```

### src/llm_call/proof_of_concept/poc_claude_proxy_server.py
Issues: 7

#### Line 124
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 109

**Context:**
```python
        
        # Write the config
        with open(mcp_file_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        logger.info(f"Wrote MCP config to: {mcp_file_path}")
        logger.debug(f"MCP Config contents: {json.dumps(mcp_config, indent=2)}")
        
        return mcp_file_path
except Exception as e:
        logger.error(f"Failed to write MCP config: {e}")
        raise

def remove_dynamic_mcp_json(mcp_file_path: Path) -> None:
```

#### Line 134
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 130

**Context:**
```python
    except Exception as e:
        logger.error(f"Failed to write MCP config: {e}")
        raise

def remove_dynamic_mcp_json(mcp_file_path: Path) -> None:
    """Remove the dynamically created MCP config file."""
    try:
        if mcp_file_path.exists():
            mcp_file_path.unlink()
            logger.info(f"Removed MCP config file: {mcp_file_path}")
except Exception as e:
        logger.warning(f"Failed to remove MCP config file: {e}")

# --- Claude CLI Execution ---
def execute_claude_cli_for_poc(
```

#### Line 232
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 213

**Context:**
```python
                
                # Handle final result
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"]
                        logger.info("Successfully extracted final result")
                        break
                        
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON line: {stripped_line}")
except Exception as e:
                logger.error(f"Error processing stream: {e}")
        
        # Fallback to accumulated text if no final result
        if final_result_content is None and full_response_text:
```

#### Line 260
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 185

**Context:**
```python
                return f"Claude CLI not authenticated. Run: docker exec -it llm-call-claude-proxy claude auth login"
            return f"Claude CLI error: {stderr_output.strip() if stderr_output else 'Unknown error'}"
            
    except subprocess.TimeoutExpired:
        logger.error("Claude process timed out")
        if process:
            process.kill()
            process.communicate()
        return None
except Exception as e:
        logger.exception(f"Error running Claude: {e}")
        return None
        
    finally:
```

#### Line 410
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 292

**Context:**
```python
        logger.success("Sending response back to client")
        return JSONResponse(content=response_payload)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
```

#### Line 457
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 426

**Context:**
```python
                auth_message = "Authenticated"
            else:
                stderr = auth_test.stderr.lower()
                if "not authenticated" in stderr or "login" in stderr:
                    auth_message = "Not authenticated - run: ./docker/claude-proxy/authenticate.sh"
                else:
                    auth_message = f"Authentication check failed: {auth_test.stderr[:100]}"
        else:
            auth_message = "Claude CLI not found"
except Exception as e:
        auth_message = f"Error checking authentication: {str(e)}"
    
    return {
        "status": "healthy",
```

#### Line 538
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 523

**Context:**
```python
                )
                
                logger.info(f"Status: {response.status_code}")
                response.raise_for_status()
                
                data = response.json()
                if data.get("choices"):
                    content = data["choices"][0]["message"]["content"]
                    logger.success(f"Response: {content[:200]}...")
except Exception as e:
                logger.error(f"Test failed: {e}")

# --- Main ---
if __name__ == "__main__":
```

### src/llm_call/proof_of_concept/poc_claude_proxy_with_polling.py
Issues: 5

#### Line 119
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 108

**Context:**
```python
        if not mcp_config:
            mcp_config = DEFAULT_ALL_TOOLS_MCP_CONFIG
            logger.info("Using default MCP config (all tools)")
        
        with open(mcp_file_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        logger.info(f"Wrote MCP config to: {mcp_file_path}")
        return mcp_file_path
except Exception as e:
        logger.error(f"Failed to write MCP config: {e}")
        raise

def remove_dynamic_mcp_json(mcp_file_path: Path) -> None:
```

#### Line 129
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 125

**Context:**
```python
    except Exception as e:
        logger.error(f"Failed to write MCP config: {e}")
        raise

def remove_dynamic_mcp_json(mcp_file_path: Path) -> None:
    """Remove the dynamically created MCP config file."""
    try:
        if mcp_file_path.exists():
            mcp_file_path.unlink()
            logger.info(f"Removed MCP config file: {mcp_file_path}")
except Exception as e:
        logger.warning(f"Failed to remove MCP config file: {e}")

# --- Claude CLI Execution with Progress Updates ---
async def execute_claude_cli_with_progress(
```

#### Line 259
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 213

**Context:**
```python
                
                # Handle final result
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"]
                        logger.info("Successfully extracted final result")
                        break
                        
            except json.JSONDecodeError:
                logger.debug(f"Non-JSON line: {stripped_line}")
except Exception as e:
                logger.error(f"Error processing stream: {e}")
        
        # Fallback to accumulated text
        if final_result_content is None and full_response_text:
```

#### Line 285
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 185

**Context:**
```python
        
        # Read any remaining stderr
        stderr_data = await process.stderr.read()
        if stderr_data:
            stderr_output = stderr_data.decode()
            logger.error(f"STDERR from Claude:\n{stderr_output.strip()}")
        
        if process.returncode != 0:
            raise RuntimeError(f"Claude exited with code {process.returncode}")
except Exception as e:
        logger.exception(f"Error running Claude: {e}")
        raise
        
    finally:
```

#### Line 473
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 342

**Context:**
```python
                    content={
                        "error": "Request timeout",
                        "task_id": task_id,
                        "message": f"Task is still running. Check status at /v1/polling/status/{task_id}",
                        "timeout": timeout
                    }
                )
        
    except HTTPException:
        raise
except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
```

### src/llm_call/proof_of_concept/poc_retry_manager.py
Issues: 3

#### Line 83
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 64

**Context:**
```python
        # Handle ModelResponse objects (LiteLLM format)
        elif hasattr(response, "choices") and response.choices:
            first_choice = response.choices[0]
            if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
                return first_choice.message.content or ""
        
        # Handle string responses
        elif isinstance(response, str):
            return response
except Exception as e:
        logger.warning(f"Failed to extract content: {e}")
    
    # Fallback
    return str(response)
```

#### Line 322
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 189

**Context:**
```python
                
                # Apply backoff delay
                delay = config.calculate_delay(attempt)
                if config.debug_mode:
                    logger.debug(f"Waiting {delay:.1f}s before retry...")
                await asyncio.sleep(delay)
            
        except PoCHumanReviewNeededError:
            # Re-raise human review errors
            raise
except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            
            # Check human escalation on error
            if max_attempts_before_human and attempt + 1 >= max_attempts_before_human:
```

#### Line 384
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 376

**Context:**
```python
    Handles both sync and async validation strategies transparently.
    """
    try:
        # Check if strategy has async validate
        if hasattr(strategy, '__avalidate__') or asyncio.iscoroutinefunction(strategy.validate):
            return await strategy.validate(response, context)
        else:
            # Run sync validation in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, strategy.validate, response, context)
except Exception as e:
        logger.error(f"Validation error in {strategy.name}: {e}")
        return ValidationResult(
            valid=False,
            error=f"Validation failed with error: {str(e)}",
```

### src/llm_call/proof_of_concept/poc_validation_strategies.py
Issues: 1

#### Line 178
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 139

**Context:**
```python
                        break 
            
            if final_validation_passed:
                return ValidationResult(valid=True, debug_info={"agent_report": agent_report})
            else:
                return ValidationResult(valid=False, error=f"Agent task validation failed: {reasoning}", 
                                        suggestions=[f"Agent details: {str(details_from_agent)[:200]}..."],
                                        debug_info={"agent_report": agent_report})
        except json.JSONDecodeError as e:
            return ValidationResult(valid=False, error=f"[{self.name}] Could not parse JSON from agent: {e}. Raw: {agent_report_str[:300]}", debug_info={"raw_agent_response": agent_report_str})
except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response.")
            return ValidationResult(valid=False, error=f"[{self.name}] Error processing agent response: {e}", debug_info={"raw_agent_response": str(agent_response_dict)})

# PoCAIContradictionValidator (can be a specialized use of PoCAgentTaskValidator or separate)
```

### src/llm_call/proof_of_concept/poc_validation_strategies_enhanced.py
Issues: 1

#### Line 320
**Current:** `except Exception as e:`
**Suggested:** `except json.JSONDecodeError:`
**Comment:** # JSON parsing failed

**Try block starts at line:** 259

**Context:**
```python
                    suggestions=[f"Review agent report. Agent details: {str(details)[:200]}..."],
                    debug_info={"agent_report": agent_report}
                )
                
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                error=f"[{self.name}] Could not parse JSON from agent: {e}. Raw response: {agent_report_str[:300]}...",
                debug_info={"raw_agent_response": agent_report_str}
            )
except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response.")
            return ValidationResult(
                valid=False,
                error=f"[{self.name}] Critical error processing agent response: {e}",
```

### src/llm_call/proof_of_concept/polling_manager.py
Issues: 2

#### Line 321
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 293

**Context:**
```python
            self._update_task_status(
                task_id, 
                TaskStatus.COMPLETED,
                result=result,
                end_time=datetime.utcnow().isoformat(),
                progress=100
            )
            
            logger.info(f"Task {task_id} completed successfully")
except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self._update_task_status(
                task_id,
                TaskStatus.FAILED,
```

#### Line 430
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 426

**Context:**
```python
        return False
    
    async def start_cleanup_job(self, interval: int = 3600):
        """Start periodic cleanup of old tasks."""
        async def cleanup_loop():
            while True:
                try:
                    count = self.db.cleanup_old_tasks()
                    if count > 0:
                        logger.info(f"Cleaned up {count} old tasks")
except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                
                await asyncio.sleep(interval)
```

### src/llm_call/proof_of_concept/polling_server.py
Issues: 3

#### Line 123
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 94

**Context:**
```python
            # Immediate mode - create a completed task entry
            task_id = f"immediate_{hash(str(llm_config)) & 0xffffff:06x}"
            return TaskSubmitResponse(
                task_id=task_id,
                status="completed",
                message="Task completed immediately"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to submit task")
except Exception as e:
        logger.error(f"Task submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### Line 203
**Current:** `except Exception as e:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 200

**Context:**
```python
            }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check database
    try:
        active_tasks = polling_manager.db.get_active_tasks()
        db_healthy = True
except Exception as e:
        db_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # Check proxy if needed
```

#### Line 214
**Current:** `except:`
**Suggested:** `except KeyError:`
**Comment:** # Key not found

**Try block starts at line:** 209

**Context:**
```python
        db_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # Check proxy if needed
    proxy_healthy = True
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3010/health", timeout=2.0)
            proxy_healthy = response.status_code == 200
except:
        proxy_healthy = False
    
    return {
        "status": "healthy" if db_healthy else "degraded",
```

### src/llm_call/proof_of_concept/slash_commands/slash_commands_v1/poc_slash_command.py
Issues: 1

#### Line 359
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 318

**Context:**
```python
                        create(
                            name=cmd_name,
                            description=f"Wrapper for {node.name} command",
                            content=cmd_content,
                            typer_command=f"{typer_script} {node.name}"
                        )
                        commands_created += 1
        
        typer.echo(f"\n Created {commands_created} commands from {typer_script}")
except Exception as e:
        typer.echo(f" Error parsing Typer script: {e}", err=True)
        raise typer.Exit(1)
```

### src/llm_call/proof_of_concept/slash_commands/v2_typer_automated/typer_cli_to_slash_and_mcp.py
Issues: 1

#### Line 452
**Current:** `except Exception as e:`
**Suggested:** `except asyncio.TimeoutError:`
**Comment:** # Async operation failed

**Try block starts at line:** 447

**Context:**
```python
        async def mcp_tool_wrapper(**kwargs):
            """Wrapper that calls the original Typer command"""
            # Get the original function from the closure
            original_func = func
            
            try:
                # Call the original function
                # In production, you'd handle async/sync conversion properly
                result = original_func(**kwargs)
                return {"status": "success", "result": result}
except Exception as e:
                return {"status": "error", "error": str(e)}
        
        registered += 1
```

### src/llm_call/proof_of_concept/v4_implementation_verification.py
Issues: 1

#### Line 68
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Generic exception handler

**Try block starts at line:** 50

**Context:**
```python
                
                if func_start != -1:
                    func_section = content[func_start:func_start + 500]
                    if "pass" in func_section[:100] or "..." in func_section[:100]:
                        return False, f"{YELLOW}⚠ STUB ONLY{RESET}"
                    elif "TODO" in func_section or "FIXME" in func_section:
                        return False, f"{YELLOW}⚠ TODO FOUND{RESET}"
                    else:
                        return True, f"{GREEN}✓ IMPLEMENTED{RESET}"
            return False, f"{RED}✗ NOT FOUND{RESET}"
except Exception as e:
        return False, f"{RED}✗ ERROR: {e}{RESET}"

def verify_mcp_implementation():
    """Verify MCP implementation status."""
```

### src/llm_call/proof_of_concept/verify_v4_setup.py
Issues: 6

#### Line 47
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # LiteLLM call failed

**Try block starts at line:** 44

**Context:**
```python

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def check_imports():
    """Check all required imports work."""
    print("Checking imports...")
    try:
        from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
        print(" Can import llm_call")
except Exception as e:
        print(f" Failed to import llm_call: {e}")
        return False
    
    try:
```

#### Line 58
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 51

**Context:**
```python
        print(f" Failed to import llm_call: {e}")
        return False
    
    try:
        from src.llm_call.proof_of_concept.poc_validation_strategies import (
            PoCAgentTaskValidator,
            poc_strategy_registry
        )
        print(" Can import validation strategies")
        print(f"   Available validators: {list(poc_strategy_registry.keys())}")
except Exception as e:
        print(f" Failed to import validators: {e}")
        return False
    
    try:
```

#### Line 68
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 62

**Context:**
```python
    except Exception as e:
        print(f" Failed to import validators: {e}")
        return False
    
    try:
        from src.llm_call.proof_of_concept.poc_retry_manager import (
            retry_with_validation_poc,
            PoCHumanReviewNeededError
        )
        print(" Can import retry manager")
except Exception as e:
        print(f" Failed to import retry manager: {e}")
        return False
    
    return True
```

#### Line 89
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 79

**Context:**
```python
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:3010/health", timeout=2.0)
            response.raise_for_status()
            data = response.json()
            print(" Proxy server is running")
            print(f"   Claude CLI: {data.get('claude_cli_path', 'Unknown')}")
            print(f"   Working dir: {data.get('working_directory', 'Unknown')}")
            print(f"   MCP support: {data.get('mcp_support', False)}")
            return True
except Exception as e:
        print(f" Proxy server not reachable: {e}")
        print("   Start it with: python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return False
```

#### Line 158
**Current:** `except Exception as e:`
**Suggested:** `except ValueError:`
**Comment:** # Type conversion failed

**Try block starts at line:** 143

**Context:**
```python
                content = response["choices"][0]["message"]["content"]
                print(f" Got response: {content}")
                return True
            else:
                print(f" Unexpected response format: {response}")
                return False
        else:
            print(" No response received")
            return False
except Exception as e:
        print(f" Call failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
```

#### Line 191
**Current:** `except Exception as e:`
**Suggested:** `except Exception:`
**Comment:** # Claude API call failed

**Try block starts at line:** 178

**Context:**
```python
        if response:
            if isinstance(response, dict) and response.get("choices"):
                content = response["choices"][0]["message"]["content"]
                print(f" Claude reported available tools:")
                print(f"   {content[:200]}...")
                return True
        
        print(" Could not get tool list")
        return False
except Exception as e:
        print(f" Call failed: {e}")
        return False

async def main():
```

### src/llm_call/rl_integration/integration_example.py
Issues: 5

#### Line 51
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 48

**Context:**
```python
                providers=list(providers_config.keys()),
                exploration_rate=rl_exploration_rate
            )
            
            # Try to load existing model
            model_path = Path.home() / ".llm_call" / "rl_model.json"
            if model_path.exists():
                try:
                    self.rl_selector.load_model(model_path)
                    logger.info("Loaded existing RL model")
except Exception as e:
                    logger.warning(f"Failed to load RL model: {e}")
        else:
            self.rl_selector = None
```

#### Line 85
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 82

**Context:**
```python
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # Select provider
        if self.use_rl and self.rl_selector:
            try:
                provider, selection_metadata = self.rl_selector.select_provider(request)
                logger.info(f"RL selected provider: {provider}")
except Exception as e:
                logger.error(f"RL selection failed: {e}, using fallback")
                provider = self.fallback_provider
                selection_metadata = {"fallback": True}
        else:
```

#### Line 109
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 98

**Context:**
```python
            # This is where you would integrate with actual provider APIs
            # For now, we simulate a response
            response = await self._call_provider(provider, request)
            
            latency = time.time() - start_time
            success = True
            
            # Estimate cost (would be calculated from actual API response)
            cost = self._estimate_cost(provider, request, response)
except Exception as e:
            logger.error(f"Provider {provider} failed: {e}")
            response = {"error": str(e)}
            latency = time.time() - start_time
            success = False
```

#### Line 137
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 118

**Context:**
```python
                    cost=cost,
                    quality_score=quality_score
                )
                
                logger.debug(f"RL update metrics: {update_metrics}")
                
                # Periodically save model
                if self.rl_selector.bandit.training_steps % 100 == 0:
                    self._save_rl_model()
except Exception as e:
                logger.error(f"Failed to update RL model: {e}")
        
        # Return response with metadata
        return {
```

#### Line 223
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 220

**Context:**
```python
    
    def _save_rl_model(self):
        """Save the RL model to disk"""
        if self.rl_selector:
            model_path = Path.home() / ".llm_call" / "rl_model.json"
            model_path.parent.mkdir(exist_ok=True)
            
            try:
                self.rl_selector.save_model(model_path)
                logger.info("Saved RL model")
except Exception as e:
                logger.error(f"Failed to save RL model: {e}")
    
    def get_rl_report(self) -> Optional[str]:
        """Get RL optimization report"""
```

### src/llm_call/tools/conversational_delegator.py
Issues: 1

#### Line 198
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 160

**Context:**
```python
        logger.success(f"Response received from {model}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "model": model,
            "content": content,
            "message_count": len(messages) + 1
        }
except Exception as e:
        logger.error(f"Error calling {model}: {e}")
        
        # Save error to conversation
        await manager.add_message(
```

### src/llm_call/tools/llm_call_delegator.py
Issues: 2

#### Line 149
**Current:** `except Exception as e:`
**Suggested:** `except AttributeError:`
**Comment:** # Attribute not found

**Try block starts at line:** 120

**Context:**
```python
        else:
            content = str(response)
        
        return {
            "success": True,
            "model": model,
            "content": content,
            "recursion_depth": current_depth + 1
        }
except Exception as e:
        logger.exception(f"Error in delegated LLM call to {model}")
        return {
            "error": str(e),
            "error_type": type(e).__name__,
```

#### Line 246
**Current:** `except Exception as e:`
**Suggested:** `except IOError:`
**Comment:** # File operation failed

**Try block starts at line:** 242

**Context:**
```python
    # Load environment variables
    load_dotenv()
    
    # Build the full prompt
    full_prompt = args.prompt
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_content = f.read()
            full_prompt = f"{args.prompt}\n\nContent from {args.file}:\n{file_content}"
except Exception as e:
            error_result = {
                "error": f"Failed to read file {args.file}: {e}",
                "error_type": "FileReadError"
            }
```