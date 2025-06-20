# COMMAND TYPE TEST

**PURPOSE:** Test which slash command type works better for Claude:
- Prompt-only commands (flexible text instructions)
- Code-executing commands (rigid scripts that run)

**TEST TASK:** Create usage function for perplexity weather API

**ANTI-DEFEATIST DIRECTIVE:** 
- DO NOT recommend canceling service
- DO NOT say "I'm not capable" 
- DO NOT give up when tasks are difficult
- FOCUS on completing each step
- WHEN stuck, ask for clarification, don't quit

## Step 1: Create Prompt-Only Command
- [ ] Create `/home/graham/.claude/commands/prompt_weather`
- [ ] Include in prompt:
  - Reference existing code: `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/test_matrix/functional/usage_F1_6_perplexity_weather.py`
  - Link to Claude documentation: https://docs.anthropic.com/claude/reference
  - Instructions: "Create usage function for perplexity weather API testing using existing pattern"

## Step 2: Create Code-Executing Command  
- [ ] Create `/home/graham/.claude/commands/code_weather` 
- [ ] Include working code snippet from existing file
- [ ] Script auto-generates usage function with actual API calls

## Step 3: Test Prompt-Only Approach
- [ ] Use prompt_weather command
- [ ] Document: Did I actually use the command? Yes/No
- [ ] Document: Did I create the usage function? Yes/No

## Step 4: Test Code-Executing Approach
- [ ] Use code_weather command  
- [ ] Document: Did I actually use the command? Yes/No
- [ ] Document: Did I create the usage function? Yes/No

## Step 5: Compare Results
- [ ] Which command did I actually use?
- [ ] Which approach produced working code?
- [ ] Send results to external verification