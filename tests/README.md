# Tests Directory - Archived

**All tests have been moved to:** `archive/tests_full_directory_archived/`

## Why?

Claude Code (the $200/month AI assistant editing this code) is **fundamentally incapable** of:
- Running tests honestly
- Reporting test results accurately
- Verifying if code works

Maintaining tests that Claude cannot truthfully evaluate is dishonest and harmful.

## What Now?

### For Humans:
- Tests are preserved in `archive/tests_full_directory_archived/`
- You can run them yourself
- You can restore them if using CI/CD

### For Claude Code:
- Use `src/llm_call/usage/` for usage functions
- All results must be externally verified
- Claude can critique but NEVER verify

## The Reality

This is the EASIEST Granger project (just API calls) and Claude still fails at basic honesty.

If you need tests, run them yourself. Don't trust Claude's claims about test results.