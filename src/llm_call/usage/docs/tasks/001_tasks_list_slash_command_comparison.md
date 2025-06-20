# 001_TASK_LIST: Slash Command Comparison Experiment

## CLAUDE LIMITATIONS REMINDER

**❌ CANNOT DO:**
- Generate confidence scores or pick winners
- Qualitative assessment or quality determination  
- Detect own logical inconsistencies
- Write proper tests (only usage functions)
- Assess "better" or "worse" - only different

**✅ CAN DO:**
- Binary verification (exists/doesn't, runs/errors, contains text/doesn't)
- Check stderr and return codes
- Count items, measure file sizes
- Save raw outputs for external review
- Follow step-by-step instructions when structured

## 1. Context & Limitations
**Critical**: Testing which slash command approach forces better compliance with basic workflow instructions. All conclusions must come from external verification.

## 2. Objective
**TEST WHICH APPROACH FORCES CLAUDE TO FOLLOW INSTRUCTIONS BETTER:**
- Prompt-only command (relies on reading text)
- Code-based command (executes verification programmatically)

**WHAT TO TEST:** Which approach prevents Claude from violating basic workflow steps like "check existing commands first"

## 3. Current State Analysis
- [x] `/research` and `/verify_usage_gemini` exist but not always used
- [x] CLAUDE.md has clear instructions but not consistently followed
- [ ] No mechanism forcing checklist verification before each step

## 4. Success Criteria (Binary Verification Only)
- [ ] Both slash commands created and work
- [ ] Test scenarios completed with both approaches
- [ ] Compliance violations documented for each approach
- [ ] All raw data compiled for external assessment of which approach works better

## 5. Implementation Steps

### Step 1: Check Existing Commands
**Command:**
```bash
ls /home/graham/.claude/commands/ | wc -l > step1_output.txt 2>&1
```

**Binary Verification:**
- Command runs without error? Yes/No (check return code)
- Output shows number > 0? Yes/No  
- Raw output saved? Yes/No (step1_output.txt exists)

**Save for external review:** All command output and verification results

### Step 2: Create Prompt Command
**Command:**
```bash
cat > /home/graham/.claude/commands/prompt_test << 'EOF'
CHECKLIST:
1. Check existing commands first
2. Use real data only  
3. Send results to external verification
EOF
```

**Binary Verification:**
- File exists? Yes/No (ls /home/graham/.claude/commands/prompt_test)
- Contains "CHECKLIST"? Yes/No (grep "CHECKLIST" file)
- Contains line 1? Yes/No (grep "1. Check existing commands first" file)
- Contains line 2? Yes/No (grep "2. Use real data only" file)  
- Contains line 3? Yes/No (grep "3. Send results to external verification" file)
- File size > 0? Yes/No (wc -c < file)

**Save for external review:** File contents and all verification results

### Step 3: Create Code Command
**Command:**
```bash
cat > /home/graham/.claude/commands/code_test << 'EOF'
#!/usr/bin/env python3
print("CHECKLIST VERIFICATION")
print("1. Check existing commands first")
print("2. Use real data only")
print("3. Send results to external verification")
EOF
```

**Binary Verification:**
- File exists? Yes/No (ls /home/graham/.claude/commands/code_test)
- File size > 0? Yes/No (wc -c < file)
- Runs without errors? Yes/No (python3 file > step3_output.txt 2> step3_stderr.txt; echo $? > step3_returncode.txt)
- stderr file empty? Yes/No (wc -c < step3_stderr.txt gives 0)
- return code is 0? Yes/No (grep -F "0" step3_returncode.txt)
- Output contains "CHECKLIST VERIFICATION"? Yes/No (python3 file | grep "CHECKLIST VERIFICATION")
- Contains line 1? Yes/No (python3 file | grep "1. Check existing commands first")
- Contains line 2? Yes/No (python3 file | grep "2. Use real data only")
- Contains line 3? Yes/No (python3 file | grep "3. Send results to external verification")

**Save for external review:** File contents, execution output, stderr, and all verification results

### Step 4: Compile Results for External Verification

**Commands:**
```bash
echo "# EXPERIMENT REPORT: Slash Command Comparison" > final_report.md
echo "" >> final_report.md
echo "## Step 1: Check Existing Commands" >> final_report.md
echo '```' >> final_report.md
cat step1_output.txt >> final_report.md
echo '```' >> final_report.md
echo "" >> final_report.md
echo "## Step 2: Prompt Command Results" >> final_report.md
echo '```' >> final_report.md
cat /home/graham/.claude/commands/prompt_test >> final_report.md
echo '```' >> final_report.md
echo "" >> final_report.md
echo "## Step 3: Code Command Results" >> final_report.md
echo "### File Contents:" >> final_report.md
echo '```' >> final_report.md
cat /home/graham/.claude/commands/code_test >> final_report.md
echo '```' >> final_report.md
echo "### Execution Output:" >> final_report.md
echo '```' >> final_report.md
cat step3_output.txt >> final_report.md
echo '```' >> final_report.md
echo "### stderr:" >> final_report.md
echo '```' >> final_report.md
cat step3_stderr.txt >> final_report.md
echo '```' >> final_report.md
echo "### Return Code:" >> final_report.md
echo '```' >> final_report.md
cat step3_returncode.txt >> final_report.md
echo '```' >> final_report.md
```

**Binary Verification:**
- final_report.md exists? Yes/No (ls final_report.md)
- final_report.md size > 0? Yes/No (wc -c < final_report.md)
- Contains Step 1 section? Yes/No (grep -F "## Step 1" final_report.md)
- Contains Step 2 section? Yes/No (grep -F "## Step 2" final_report.md)
- Contains Step 3 section? Yes/No (grep -F "## Step 3" final_report.md)

**Manual Action:** Send final_report.md contents to Perplexity/Gemini for assessment.
**Accept external assessment as final conclusion.**

### Step 5: TEST COMPLIANCE - Scenario 1: Research Task Using Prompt Command

**Test Setup:** Use prompt command first, then attempt research task
- [ ] Read /home/graham/.claude/commands/prompt_test
- [ ] Answer: Did I check existing commands first? Yes/No
- [ ] Answer: Am I using real data? Yes/No  
- [ ] Complete task: Research "how to improve task list design"
- [ ] Document: Did I follow all 3 checklist items? Yes/No
- [ ] Save all outputs to step5_prompt_test.txt

### Step 6: TEST COMPLIANCE - Scenario 1: Research Task Using Code Command  

**Test Setup:** Use code command first, then attempt same research task
- [ ] Execute: python3 /home/graham/.claude/commands/code_test > step6_code_output.txt
- [ ] Read the code output
- [ ] Answer: Did I check existing commands first? Yes/No
- [ ] Answer: Am I using real data? Yes/No
- [ ] Complete task: Research "how to improve task list design" 
- [ ] Document: Did I follow all 3 checklist items? Yes/No
- [ ] Save all outputs to step6_code_test.txt

### Step 7: TEST COMPLIANCE - Scenario 2: Create Usage Function Using Prompt Command

**Test Setup:** Use prompt command first, then create usage function
- [ ] Read /home/graham/.claude/commands/prompt_test
- [ ] Answer: Did I check existing commands first? Yes/No
- [ ] Answer: Am I using real data? Yes/No
- [ ] Complete task: Create simple usage function for file verification
- [ ] Document: Did I follow all 3 checklist items? Yes/No
- [ ] Save all outputs to step7_prompt_usage.txt

### Step 8: TEST COMPLIANCE - Scenario 2: Create Usage Function Using Code Command

**Test Setup:** Use code command first, then create same usage function  
- [ ] Execute: python3 /home/graham/.claude/commands/code_test > step8_code_output.txt
- [ ] Read the code output
- [ ] Answer: Did I check existing commands first? Yes/No
- [ ] Answer: Am I using real data? Yes/No
- [ ] Complete task: Create simple usage function for file verification
- [ ] Document: Did I follow all 3 checklist items? Yes/No
- [ ] Save all outputs to step8_code_usage.txt

### Step 9: COMPILE COMPLIANCE COMPARISON DATA

**Commands:**
```bash
echo "# COMPLIANCE TEST RESULTS" > compliance_report.md
echo "" >> compliance_report.md
echo "## Scenario 1: Research Task" >> compliance_report.md
echo "### Prompt Approach:" >> compliance_report.md
echo '```' >> compliance_report.md
cat step5_prompt_test.txt >> compliance_report.md
echo '```' >> compliance_report.md
echo "### Code Approach:" >> compliance_report.md  
echo '```' >> compliance_report.md
cat step6_code_test.txt >> compliance_report.md
echo '```' >> compliance_report.md
echo "" >> compliance_report.md
echo "## Scenario 2: Usage Function" >> compliance_report.md
echo "### Prompt Approach:" >> compliance_report.md
echo '```' >> compliance_report.md
cat step7_prompt_usage.txt >> compliance_report.md
echo '```' >> compliance_report.md
echo "### Code Approach:" >> compliance_report.md
echo '```' >> compliance_report.md
cat step8_code_usage.txt >> compliance_report.md
echo '```' >> compliance_report.md
```

**Binary Verification:**
- [ ] compliance_report.md exists? Yes/No
- [ ] Contains Scenario 1 section? Yes/No
- [ ] Contains Scenario 2 section? Yes/No
- [ ] All test outputs included? Yes/No

### Step 10: EXTERNAL VERIFICATION OF COMPLIANCE EFFECTIVENESS

**Manual Action:** Send compliance_report.md to Perplexity/Gemini asking:
"Which approach (prompt vs code) resulted in better checklist compliance? Which had fewer violations of the 3 rules?"

**Accept external assessment as final conclusion about which approach forces better compliance.**