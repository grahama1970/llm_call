# V4 Test Prompts Validation Report

Generated: 2025-05-24 12:43:20

## Summary

- **Total Tests**: 5
- **Passed**: 4 (80.0%)
- **Failed**: 1 (20.0%)

## Test Results Table

| Test ID | Model | Status | Duration | Reason | Description |
|---------|-------|--------|----------|--------|-------------|
| max_text_001_simple_question | max/text-general | ✅ PASSED | 12.86s | Got valid response | Simplest call to Claude proxy with a question stri... |
| max_text_002_system_and_user_messages | max/text-creative-writer | ✅ PASSED | 6.84s | Got valid response | Call to Claude proxy with system and user roles. |
| max_text_003_no_default_validation | max/text-simple | ✅ PASSED | 7.43s | Got valid response | Claude proxy call, explicitly disabling default va... |
| vertex_text_001_simple_question | vertex_ai/gemini-1.5-flash-001 | ❌ FAILED | 3.13s | Human review needed | Simplest call to Vertex AI with a question string. |
| openai_text_001_system_and_user | openai/gpt-3.5-turbo | ✅ PASSED | 1.66s | Got valid response | Call to OpenAI with system and user messages. |

## Model Performance

| Model | Total | Passed | Failed | Pass Rate |
|-------|-------|--------|--------|------------|
| max/text-creative-writer | 1 | 1 | 0 | 100.0% |
| max/text-general | 1 | 1 | 0 | 100.0% |
| max/text-simple | 1 | 1 | 0 | 100.0% |
| openai/gpt-3.5-turbo | 1 | 1 | 0 | 100.0% |
| vertex_ai/gemini-1.5-flash-001 | 1 | 0 | 1 | 0.0% |
