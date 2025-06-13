"""
Module: verify_environment.py
Description: Pre-flight environment check for llm_call testing

Verifies that the basic environment is set up correctly before running any tests.
This is Phase 0 of the progressive testing approach.

External Dependencies:
None - uses only Python stdlib

Sample Input:
>>> python verify_environment.py

Expected Output:
>>> Environment ready for testing with checkmarks for each verification

Example Usage:
>>> python tests/verify_environment.py
"""

import os
import sys
import importlib
from datetime import datetime


def verify_environment():
    """Verify basic environment setup for llm_call."""
    print("=== LLM_CALL Environment Verification ===")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Working Directory: {os.getcwd()}")
    print()
    
    # Track overall success
    all_good = True
    
    # 1. Python Environment
    print("📋 Python Environment:")
    checks = {
        "Python Version": sys.version.split()[0],
        "Virtual Env Active": "✅" if (hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix) else "❌",
        "PYTHONPATH Set": "✅" if os.environ.get("PYTHONPATH") else "❌ (run: export PYTHONPATH=./src)",
        "Working Dir Correct": "✅" if "llm_call" in os.getcwd() else "❌"
    }
    
    for check, status in checks.items():
        print(f"  {check}: {status}")
        if "❌" in status:
            all_good = False
    
    # 2. Core Dependencies
    print("\n📦 Core Dependencies:")
    dependencies = {
        "dotenv": "python-dotenv",
        "loguru": "loguru",
        "pydantic": "pydantic",
        "httpx": "httpx",
        "litellm": "litellm"
    }
    
    for module, package in dependencies.items():
        try:
            importlib.import_module(module)
            print(f"  {package}: ✅")
        except ImportError:
            print(f"  {package}: ❌ (run: pip install {package})")
            all_good = False
    
    # 3. Load Environment Variables
    print("\n🔐 Environment Variables:")
    try:
        import dotenv
        dotenv.load_dotenv()
        print("  .env loaded: ✅")
    except:
        print("  .env loaded: ❌")
        all_good = False
    
    # 4. API Keys
    print("\n🔑 API Keys:")
    api_keys = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    }
    
    at_least_one_key = False
    for key_name, key_value in api_keys.items():
        if key_value:
            # Show partial key for security
            if len(key_value) > 10:
                display = f"{key_value[:4]}...{key_value[-4:]}"
            else:
                display = "Present"
            print(f"  {key_name}: ✅ ({display})")
            at_least_one_key = True
        else:
            print(f"  {key_name}: ❌")
    
    if not at_least_one_key:
        print("\n  ⚠️  No API keys found! At least one is required.")
        all_good = False
    
    # 5. Project Structure
    print("\n📁 Project Structure:")
    required_paths = {
        "Source": "src/llm_call",
        "Tests": "tests",
        "Logs": "logs",
        "Config": ".env"
    }
    
    for name, path in required_paths.items():
        exists = os.path.exists(path)
        print(f"  {name} ({path}): {'✅' if exists else '❌'}")
        if not exists and name != "Config":  # .env is optional
            all_good = False
    
    # 6. Can Import llm_call?
    print("\n🧪 Import Test:")
    try:
        # Add src to path if needed
        src_path = os.path.join(os.getcwd(), "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        import llm_call
        print("  import llm_call: ✅")
        
        # Try core imports
        from llm_call.core.caller import make_llm_request
        print("  import make_llm_request: ✅")
        
        from llm_call.core.router import resolve_route
        print("  import resolve_route: ✅")
        
    except Exception as e:
        print(f"  Import failed: ❌ ({str(e)[:50]}...)")
        all_good = False
    
    # 7. Database/Storage
    print("\n💾 Storage:")
    db_path = "logs/conversations.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024  # KB
        print(f"  Conversations DB: ✅ ({size:.1f} KB)")
    else:
        print(f"  Conversations DB: ⚠️  Will be created on first use")
    
    # Summary
    print("\n" + "="*50)
    if all_good:
        print("✅ Environment ready for testing!")
        print("\nNext steps:")
        print("1. Run minimal test: python tests/test_minimum_viable.py")
        print("2. Run core tests: python tests/test_core_functionality.py")
    else:
        print("❌ Environment issues detected!")
        print("\nFix the issues above, then run this script again.")
        print("\nCommon fixes:")
        print("- Activate venv: source .venv/bin/activate")
        print("- Set PYTHONPATH: export PYTHONPATH=./src")
        print("- Install deps: pip install -e .")
        print("- Add API keys to .env file")
    
    return all_good


def check_provider_specific(provider: str) -> bool:
    """Check requirements for a specific provider."""
    print(f"\n🔍 Checking {provider}...")
    
    if provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        if key and key.startswith("sk-"):
            print(f"  ✅ Valid OpenAI key format")
            return True
        else:
            print(f"  ❌ Invalid or missing OpenAI key")
            return False
    
    elif provider == "vertex":
        creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if creds and os.path.exists(creds):
            print(f"  ✅ Vertex AI credentials file exists")
            return True
        else:
            print(f"  ❌ Vertex AI credentials not found")
            return False
    
    elif provider == "gemini":
        key = os.environ.get("GOOGLE_API_KEY")
        if key:
            print(f"  ✅ Google API key present")
            return True
        else:
            print(f"  ❌ Google API key missing")
            return False
    
    return False


if __name__ == "__main__":
    # Run main verification
    success = verify_environment()
    
    # Optional: Check specific providers
    if "--providers" in sys.argv:
        print("\n" + "="*50)
        print("Provider-Specific Checks:")
        
        providers = ["openai", "vertex", "gemini"]
        for provider in providers:
            check_provider_specific(provider)
    
    # Exit with appropriate code
    exit(0 if success else 1)