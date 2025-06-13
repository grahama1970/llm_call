"""
Module: auth_diagnostics.py
Description: Enhanced authentication error diagnostics for LLM providers

This module provides detailed error analysis and troubleshooting guidance
for authentication failures across different LLM providers, preventing
confusion about the root causes of auth errors.

External Dependencies:
- litellm: https://docs.litellm.ai/
- google-auth: https://google-auth.readthedocs.io/

Sample Input:
>>> error = JWTError("Token used too early")
>>> diagnosis = diagnose_auth_error(error, "vertex_ai/gemini-1.5-pro")

Expected Output:
>>> {
...     "error_type": "JWT_TIME_VALIDATION",
...     "root_cause": "System time mismatch",
...     "solutions": ["Check system time", "Sync with NTP"],
...     "detailed_explanation": "..."
... }

Example Usage:
>>> from llm_call.core.utils.auth_diagnostics import diagnose_auth_error
>>> diagnosis = diagnose_auth_error(exception, model_name)
"""

import os
import json
import datetime
import subprocess
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from loguru import logger


class AuthDiagnostics:
    """Provides detailed diagnostics for authentication errors."""
    
    # Known error patterns and their diagnoses
    ERROR_PATTERNS = {
        "token used too early": {
            "type": "JWT_TIME_VALIDATION",
            "category": "Time Synchronization",
            "severity": "high",
            "common_causes": [
                "System clock is behind actual time",
                "JWT 'iat' (issued at) is in the future",
                "JWT 'nbf' (not before) hasn't been reached"
            ]
        },
        "jwt signature verification failed": {
            "type": "JWT_SIGNATURE_INVALID",
            "category": "Credentials",
            "severity": "critical",
            "common_causes": [
                "Service account key has been rotated",
                "Wrong project ID in configuration",
                "Corrupted service account JSON file"
            ]
        },
        "invalid api key": {
            "type": "API_KEY_INVALID",
            "category": "Credentials",
            "severity": "critical",
            "common_causes": [
                "API key has expired or been revoked",
                "Wrong API key for the service",
                "API key copied incorrectly (missing characters)"
            ]
        },
        "unauthorized": {
            "type": "UNAUTHORIZED",
            "category": "Permissions",
            "severity": "high",
            "common_causes": [
                "Service account lacks required permissions",
                "API not enabled for the project",
                "Wrong project or location specified"
            ]
        },
        "quota exceeded": {
            "type": "QUOTA_EXCEEDED",
            "category": "Usage Limits",
            "severity": "medium",
            "common_causes": [
                "API rate limit reached",
                "Monthly quota exhausted",
                "Concurrent request limit exceeded"
            ]
        }
    }
    
    @classmethod
    def check_system_time(cls) -> Dict[str, Any]:
        """Check system time and compare with actual time."""
        try:
            # Get current system time
            system_time = datetime.datetime.now()
            
            # Try to get network time (using a simple HTTP request)
            import requests
            response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC', timeout=5)
            if response.status_code == 200:
                network_time_str = response.json()['datetime']
                network_time = datetime.datetime.fromisoformat(network_time_str.replace('Z', '+00:00'))
                
                # Calculate difference - handle both naive and aware datetimes
                if network_time.tzinfo is not None and system_time.tzinfo is None:
                    # Convert system time to UTC aware
                    import pytz
                    system_time = pytz.UTC.localize(system_time)
                elif network_time.tzinfo is None and system_time.tzinfo is not None:
                    # Make network time aware
                    import pytz
                    network_time = pytz.UTC.localize(network_time)
                
                time_diff = abs((system_time - network_time).total_seconds())
                
                return {
                    "system_time": system_time.isoformat(),
                    "network_time": network_time.isoformat(),
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
                "time_sync_ok": "unknown"
            }
    
    @classmethod
    def check_credentials(cls, model: str) -> Dict[str, Any]:
        """Check credentials configuration for a given model."""
        checks = {
            "model": model,
            "provider": cls._get_provider_from_model(model),
            "credentials_found": {},
            "issues": []
        }
        
        if model.startswith("vertex_ai/"):
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
                checks["issues"].append("GOOGLE_APPLICATION_CREDENTIALS not set")
            
            # Check Vertex AI specific configs
            checks["credentials_found"]["LITELLM_VERTEX_PROJECT"] = os.getenv("LITELLM_VERTEX_PROJECT", "Not set")
            checks["credentials_found"]["LITELLM_VERTEX_LOCATION"] = os.getenv("LITELLM_VERTEX_LOCATION", "Not set")
            
        elif model.startswith("gemini/"):
            # Check Gemini API key
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                checks["credentials_found"]["GEMINI_API_KEY"] = f"***{api_key[-8:]}" if len(api_key) > 8 else "***"
            else:
                checks["issues"].append("GEMINI_API_KEY not set")
                
        elif model.startswith("gpt") or model.startswith("openai/"):
            # Check OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                checks["credentials_found"]["OPENAI_API_KEY"] = f"***{api_key[-8:]}" if len(api_key) > 8 else "***"
            else:
                checks["issues"].append("OPENAI_API_KEY not set")
                
        elif model.startswith("claude") or model.startswith("anthropic/"):
            # Check Anthropic API key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                checks["credentials_found"]["ANTHROPIC_API_KEY"] = f"***{api_key[-8:]}" if len(api_key) > 8 else "***"
            else:
                checks["issues"].append("ANTHROPIC_API_KEY not set")
        
        return checks
    
    @classmethod
    def _get_provider_from_model(cls, model: str) -> str:
        """Determine provider from model name."""
        if model.startswith("vertex_ai/"):
            return "Google Vertex AI"
        elif model.startswith("gemini/"):
            return "Google Gemini API"
        elif model.startswith("gpt") or model.startswith("openai/"):
            return "OpenAI"
        elif model.startswith("claude") or model.startswith("anthropic/"):
            return "Anthropic"
        else:
            return "Unknown"
    
    @classmethod
    def diagnose_auth_error(
        cls,
        error: Exception,
        model: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide detailed diagnosis of an authentication error.
        
        Args:
            error: The exception that occurred
            model: The model being used
            context: Additional context about the request
            
        Returns:
            Detailed diagnosis with solutions
        """
        error_str = str(error).lower()
        diagnosis = {
            "error": str(error),
            "error_type": type(error).__name__,
            "model": model,
            "provider": cls._get_provider_from_model(model),
            "diagnosis": None,
            "solutions": [],
            "checks": {}
        }
        
        # Match against known patterns
        for pattern, info in cls.ERROR_PATTERNS.items():
            if pattern in error_str:
                diagnosis["diagnosis"] = info
                break
        
        # Perform specific checks based on error type
        if "token used too early" in error_str or "jwt" in error_str:
            # Time-related JWT error
            diagnosis["checks"]["time"] = cls.check_system_time()
            
            diagnosis["solutions"].extend([
                "1. Check your system time: Is it accurate?",
                "2. Sync your system clock with NTP:",
                "   - Linux/Mac: sudo ntpdate -s time.nist.gov",
                "   - Windows: w32tm /resync",
                "3. If using WSL, sync WSL time: sudo hwclock -s",
                "4. Verify the service account key hasn't expired"
            ])
            
            if diagnosis["checks"]["time"].get("time_sync_ok") is False:
                diagnosis["primary_issue"] = "SYSTEM_TIME_MISMATCH"
                diagnosis["solutions"].insert(0, "⚠️  YOUR SYSTEM TIME IS INCORRECT - This is the primary issue!")
        
        # Check credentials
        diagnosis["checks"]["credentials"] = cls.check_credentials(model)
        
        if diagnosis["checks"]["credentials"]["issues"]:
            diagnosis["solutions"].extend([
                "Credential issues detected:",
                *[f"  - {issue}" for issue in diagnosis["checks"]["credentials"]["issues"]]
            ])
        
        # Provider-specific guidance
        if model.startswith("vertex_ai/"):
            diagnosis["solutions"].extend([
                "\nVertex AI specific checks:",
                "- Ensure the Vertex AI API is enabled in your GCP project",
                "- Verify service account has 'Vertex AI User' role",
                "- Check project ID and location are correct",
                f"- Current project: {os.getenv('LITELLM_VERTEX_PROJECT', 'Not set')}",
                f"- Current location: {os.getenv('LITELLM_VERTEX_LOCATION', 'Not set')}"
            ])
        
        return diagnosis
    
    @classmethod
    def format_diagnosis_message(cls, diagnosis: Dict[str, Any]) -> str:
        """Format diagnosis into a user-friendly message."""
        lines = [
            "\n" + "="*60,
            "🔍 AUTHENTICATION ERROR DIAGNOSIS",
            "="*60,
            f"Provider: {diagnosis['provider']}",
            f"Model: {diagnosis['model']}",
            f"Error: {diagnosis['error']}\n"
        ]
        
        if diagnosis.get("primary_issue"):
            lines.append(f"⚠️  PRIMARY ISSUE: {diagnosis['primary_issue']}\n")
        
        if diagnosis.get("diagnosis"):
            diag_info = diagnosis["diagnosis"]
            lines.extend([
                f"Category: {diag_info['category']}",
                f"Severity: {diag_info['severity'].upper()}",
                "\nCommon causes:"
            ])
            for cause in diag_info["common_causes"]:
                lines.append(f"  • {cause}")
        
        if diagnosis.get("checks", {}).get("time"):
            time_check = diagnosis["checks"]["time"]
            lines.extend([
                "\n📅 Time Check:",
                f"  System time: {time_check.get('system_time', 'Unknown')}",
                f"  Network time: {time_check.get('network_time', 'Unknown')}"
            ])
            if time_check.get("difference_seconds"):
                lines.append(f"  Difference: {time_check['difference_seconds']:.1f} seconds")
            if time_check.get("recommendation"):
                lines.append(f"  ⚠️  {time_check['recommendation']}")
        
        if diagnosis.get("solutions"):
            lines.extend(["\n💡 SOLUTIONS:"] + diagnosis["solutions"])
        
        lines.append("="*60 + "\n")
        
        return "\n".join(lines)


def diagnose_auth_error(
    error: Exception,
    model: str,
    context: Optional[Dict[str, Any]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Diagnose authentication error and optionally print detailed message.
    
    Args:
        error: The exception that occurred
        model: The model being used
        context: Additional context
        verbose: Whether to print the diagnosis
        
    Returns:
        Diagnosis dictionary
    """
    diagnosis = AuthDiagnostics.diagnose_auth_error(error, model, context)
    
    if verbose:
        message = AuthDiagnostics.format_diagnosis_message(diagnosis)
        logger.error(message)
    
    return diagnosis


# Test function
if __name__ == "__main__":
    # Test the diagnostics
    logger.info("Testing authentication diagnostics...")
    
    # Test 1: JWT time error
    class MockJWTError(Exception):
        pass
    
    error = MockJWTError("Token used too early (iat: 1234567890)")
    diagnosis = diagnose_auth_error(error, "vertex_ai/gemini-1.5-pro", verbose=True)
    
    # Test 2: API key error
    error = Exception("Invalid API key provided")
    diagnosis = diagnose_auth_error(error, "gemini/gemini-1.5-pro", verbose=True)
    
    # Test 3: Check system time
    time_check = AuthDiagnostics.check_system_time()
    logger.info(f"System time check: {time_check}")
    
    logger.success("✅ Authentication diagnostics module ready")