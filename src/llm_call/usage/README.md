# LLM Call Usage Functions

This directory contains usage functions that demonstrate and verify llm_call functionality against the comprehensive test matrix.

## Directory Structure

```
usage/
├── README.md                         # This file
├── docs/                            # Documentation
│   ├── TEST_MATRIX.md               # Comprehensive test matrix (v2.0)
│   └── WORKFLOW_TEMPLATE.md         # Workflow documentation
├── templates/                       # Templates for new tests
│   └── USAGE_FUNCTION_TEMPLATE.py   # Template for creating new usage functions
├── scripts/                         # Utility scripts
│   ├── collect_all_results.py      # Run all tests and aggregate results
│   └── show_test_status.py         # Show implementation progress
├── test_matrix/                     # All test implementations organized by category
│   ├── functional/                  # F#.# - Functional tests
│   │   └── usage_F1_1_gpt35_basic.py
│   ├── multimodal/                  # M#.# - Multimodal tests
│   ├── validation/                  # V#.# - Validation tests
│   └── conversation/                # C#.# - Conversation tests
├── results/                         # Test execution results (gitignored)
└── archive/                         # Old/deprecated test files
```

## Test ID Format

From docs/TEST_MATRIX.md, tests are organized by category:
- **F#.#** - Functional tests (basic queries, system prompts, parameters)
- **M#.#** - Multimodal tests (image analysis, vision models)
- **V#.#** - Validation tests (JSON, code, schema validation)
- **C#.#** - Conversation management tests
- **D#.#** - Document processing tests
- **S#.#** - Security & privacy tests
- **P#.#** - Performance tests
- **E#.#** - Error handling tests

Priority levels:
- **CRITICAL** - Must work for basic functionality
- **MODERATE** - Important features
- **LOW** - Nice-to-have features

## Creating New Usage Functions

1. Copy the template to appropriate subdirectory
2. Name it: `usage_[TEST_ID]_[short_description].py`
3. Replace all `[PLACEHOLDERS]` with actual values from docs/TEST_MATRIX.md
4. Customize the `check_result()` function for specific verification needs
5. Run and verify results

Example:
```bash
cp templates/USAGE_FUNCTION_TEMPLATE.py test_matrix/functional/usage_F1_5_vertex_gemini.py
# Edit the file to replace placeholders
python test_matrix/functional/usage_F1_5_vertex_gemini.py
```

## Running Tests

### Single Test
```bash
python test_matrix/functional/usage_F1_1_gpt35_basic.py
```

### All Tests
```bash
python scripts/collect_all_results.py
```

### Category-specific Tests
```bash
# Run all functional tests
for test in test_matrix/functional/usage_*.py; do
    python "$test"
done
```

## Verification Workflow

1. **Write** - Create usage function from template
2. **Run** - Execute the usage function
3. **Review** - Check rich table output for immediate verification
4. **Save** - Results automatically saved to `results/` directory
5. **Verify** - Send JSON results to Gemini/Perplexity for external verification

## Key Principles

- **Real API Calls** - No mocks, actual LLM interactions
- **Comparison Focus** - Always compare litellm vs llm_call
- **Human Verifiable** - Rich output tables for immediate verification
- **External Validation** - JSON output for AI verification
- **Self-Contained** - Each test is independent

## Notes

- Results are saved in `results/` directory (gitignored)
- Archive contains old test implementations for reference
- Template includes proper error handling and API key checks
- All tests follow consistent structure for easy automation