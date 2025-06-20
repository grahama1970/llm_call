# Critique Round Instructions - Claude Poll POC v2

## Objective
Perform a thorough, fresh critique of the entire Claude Poll POC v2 system. You must read every file completely - no skimming allowed. Identify any ambiguities, inconsistencies, or potential execution issues.

## Files to Review

### 1. Core Task Definition
- `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc_v2/tasks.yaml`
  - Read every task definition
  - Check all parameter references
  - Verify paths are correct and consistent
  - Ensure action types are clearly defined
  - Check that verify conditions are implementable

### 2. All Command Templates
Read each template in `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc_v2/commands/`:
- `archive-setup.md`
- `ask-gemini-flash.md`
- `ask-gemini-pro.md`
- `ask-ollama.md`
- `ask-perplexity.md`
- `claude-poll.md`
- `claude-verify.md`
- `logging-setup.md`

For each template, verify:
- Parameters section exists and is complete
- All variables in code use `{{ params.variable }}` syntax
- Code examples are syntactically correct Python
- Expected Output section is clear
- [SELF_CORRECTION] section is properly formatted
- No placeholder text remains (e.g., "YOUR_QUERY")

### 3. Documentation
- `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc_v2/README.md`
- `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc_v2/docs/orchestrator_design.md`

Check for:
- Accuracy of descriptions
- Consistency with actual implementation
- Clear execution flow explanation

## Critique Checklist

### A. Parameter Consistency
1. Do all parameters referenced in tasks.yaml have corresponding definitions in command templates?
2. Are parameter types consistent (string, integer, etc.)?
3. Do template parameters match what tasks.yaml provides?
4. Are there any undefined parameters being used?

### B. Path Consistency
1. Is the working_directory in tasks.yaml correct?
2. Do all file paths make sense relative to working_directory?
3. Are generated_scripts/, logs/, outputs/ directories referenced consistently?
4. Do command template references use correct relative paths?

### C. Execution Flow
1. Can T1_ENV_SETUP actually archive and set up the environment?
2. Will T3_RUN_CODE_INLINE find the script created by T2?
3. Does T4_BACKGROUND_VERIFICATION have all needed parameters?
4. Will T5_POLL_FOR_VERIFICATION work with the polling logic?
5. Can T6_FINAL_AUDIT access the files it references?

### D. Template Implementation
1. Is each template's Python code actually executable?
2. Are imports correct and available?
3. Do error handling blocks cover likely failure modes?
4. Are file I/O operations using correct paths?
5. Is the logging setup consistent across templates?

### E. Self-Correction Logic
1. Does each [SELF_CORRECTION] block follow the same format?
2. Are the JSON response formats consistent?
3. Can the orchestrator actually parse and use these corrections?
4. Are correction types clearly defined?

### F. Special Cases
1. How does background execution (mode: background) actually work?
2. Is the poll_file_status action type defined somewhere?
3. How does execute_after_generate in T5 work?
4. Are {{ settings.variable }} references resolved correctly?
5. How are {{ file_content('filename') }} functions implemented?

## Output Format

Create your critique as a structured markdown file with:

```markdown
# Claude Poll POC v2 - Critique Round Results

## Executive Summary
[Brief overview of findings]

## Critical Issues
[Issues that would prevent execution]

## Ambiguities
[Unclear or potentially confusing elements]

## Inconsistencies
[Mismatches between files]

## Missing Elements
[Required but undefined components]

## Recommendations
[Specific fixes for each issue]

## Questions for Clarification
[Things that need human input to resolve]
```

## Remember
- Read EVERY line of EVERY file
- Don't assume anything works - verify it
- Check cross-file references
- Think like an orchestrator trying to execute these tasks
- Be specific about line numbers and file locations
- Propose concrete solutions, not just identify problems
