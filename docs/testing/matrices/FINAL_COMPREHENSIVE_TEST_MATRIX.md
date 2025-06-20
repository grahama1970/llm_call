# LLM Call Comprehensive Test Matrix

**Version**: 2.0  
**Date**: January 14, 2025  
**Purpose**: Comprehensive testing framework for llm_call with specific configs, slash commands, and verification metrics

## Executive Summary

### Core Features Tested
- **Multi-Provider Support**: OpenAI (GPT-4/3.5), Anthropic (Claude via max/opus), Google (Vertex AI/Gemini), Ollama (local), Runpod (cloud GPU)
- **Conversation State Management**: SQLite-based persistence across model switches
- **Validation Framework**: 16 built-in validators (JSON, code, schema, length, regex, SQL safety, etc.)
- **Multimodal Capabilities**: Image analysis with max/opus and gpt-4-vision
- **Corpus Analysis**: Process entire directories with pattern matching
- **Text Processing**: Smart chunking, rolling window summarization, embeddings
- **Agent Collaboration**: Multi-model workflows with tool augmentation
- **Caching**: Redis with 48h TTL via --cache parameter
- **API Compatibility**: OpenAI-compatible /v1/chat/completions endpoint
- **Docker Deployment**: Multi-container setup with Claude proxy authentication

### Key Testing Interfaces
1. **CLI**: `llm ask`, `llm chat`, `llm models`
2. **Slash Commands**: `/llm`, `/llm_call`, `/llm_call_multimodal`
3. **Python API**: `make_llm_request()`, `conversational_delegate()`
4. **FastAPI**: REST endpoints at http://localhost:8001
5. **MCP Tools**: For Claude Desktop integration
6. **Config Files**: JSON/YAML configuration support

### Critical Requirements
- **ANTHROPIC_API_KEY**: Must be unset for max/opus models (OAuth only)
- **PYTHONPATH**: Must be set to ./src
- **Redis**: Required for caching functionality
- **Docker**: Recommended for Claude proxy mode

## Summary of Comprehensive Review

Based on the final codebase review, the test matrix includes:

1. **All documented features** from README.md and PURPOSE.md
2. **Hidden features discovered** in the codebase:
   - Corpus analysis functionality (found in CLI but not documented)
   - Text chunking utilities for large documents
   - Embeddings support (OpenAI text-embedding-ada-002)
   - SpaCy NLP integration for entity recognition and parsing
   - Tree-sitter code analysis for AST parsing
   - Rolling window summarization for documents exceeding token limits
   - Cost tracking and limits
   - Conversation export/import functionality
   - Streaming response support
3. **All configuration methods**:
   - CLI parameters
   - JSON/YAML config files
   - Environment variables
   - Slash command arguments
4. **Critical notes**:
   - max/opus models require unsetting ANTHROPIC_API_KEY
   - Redis caching uses --cache parameter with 48h TTL
   - Docker deployment includes Claude proxy authentication workflow
   - Conversational delegator is key for Claude Module Communicator integration

The complete test matrix with 600+ individual tests is available in LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md.