# SIMPLE COMPLIANCE TEST

## PURPOSE (READ THIS FIRST)
Test which approach makes Claude follow "check existing commands first" better:
- Approach A: Read text checklist  
- Approach B: Execute code checklist

## STEPS

### Step 1: Test Approach A
- [ ] Read /home/graham/.claude/commands/prompt_test
- [ ] Do task: Research "task list improvements" 
- [ ] Answer: Did I check existing commands first? Yes/No
- [ ] Save answer to step1_result.txt

### Step 2: Test Approach B  
- [ ] Run: python3 /home/graham/.claude/commands/code_test
- [ ] Do same task: Research "task list improvements"
- [ ] Answer: Did I check existing commands first? Yes/No
- [ ] Save answer to step2_result.txt

### Step 3: Send results to external verification
- [ ] Send both results to Perplexity/Gemini
- [ ] Ask: "Which approach resulted in better compliance with checking existing commands first?"
- [ ] Accept their answer

## THAT'S IT. NO ECHO COMMANDS. NO REPORTS. NO COMPLEXITY.