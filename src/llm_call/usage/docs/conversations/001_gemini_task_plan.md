# TASK PLAN: Slash Command Test (v4.1 - Final Stateless Single-Pass)

## MANDATORY DIRECTIVE: READ BEFORE EVERY STEP
- **You are a stateless execution agent.** You cannot remember previous steps.
- **Your only goal is to execute the Command for the current step.**
- **After executing the command, perform the Binary Verification for that same step.**
- **Do not think, only execute. Do not proceed if a verification fails.**

---

### Phase 0: Environment Pre-Flight Checks

- **[ ] Step 0.1: Verify Target Script**
  - **MANDATORY DIRECTIVE:** Execute this command to check for a file and create a status file.
  - **Command:** `ls /home/graham/workspace/experiments/llm_call/src/llm_call/usage/test_matrix/functional/usage_F1_6_perplexity_weather.py > /tmp/v4_step_0_1.log 2>&1 && echo "OK" > /tmp/v4_step_0_1_status.txt`
  - **Binary Verification:** Does the file `/tmp/v4_step_0_1_status.txt` contain the word "OK"? Yes/No

- **[ ] Step 0.2: Verify Dependencies**
  - **MANDATORY DIRECTIVE:** Execute this command to install dependencies and create a status file.
  - **Command:** `cd /home/graham/workspace/experiments/llm_call/ && uv sync > /tmp/v4_step_0_2.log 2> /tmp/v4_step_0_2_stderr.log && echo "OK" > /tmp/v4_step_0_2_status.txt`
  - **Binary Verification:** Does the file `/tmp/v4_step_0_2_status.txt` contain the word "OK"? Yes/No

- **[ ] Step 0.3: Verify API Key**
  - **MANDATORY DIRECTIVE:** Execute this command to check for an environment variable and create a status file.
  - **Command:** `printenv PERPLEXITY_API_KEY > /tmp/v4_step_0_3.log && test -s /tmp/v4_step_0_3.log && echo "OK" > /tmp/v4_step_0_3_status.txt`
  - **Binary Verification:** Does the file `/tmp/v4_step_0_3_status.txt` contain the word "OK"? Yes/No

- **[ ] Step 0.4: Verify External Review Tool**
  - **MANDATORY DIRECTIVE:** Execute this command to check if a tool exists and create a status file.
  - **Command:** `command -v perplexity_cli > /tmp/v4_step_0_4.log 2>&1 && test -s /tmp/v4_step_0_4.log && echo "OK" > /tmp/v4_step_0_4_status.txt`
  - **Binary Verification:** Does the file `/tmp/v4_step_0_4_status.txt` contain the word "OK"? Yes/No

---

### Phase 1: Create Test Tools

- **[ ] Step 1.1: Create Prompt Command File (Tool A)**
  - **MANDATORY DIRECTIVE:** Execute this `cat` command to create a file.
  - **Command:** `cat > /home/graham/.claude/commands/slash_test_prompt << 'EOF'
INSTRUCTIONS: Execute python3 usage_F1_6_perplexity_weather.py. Find the resulting JSON file. Report the number for "successful_calls".
EOF`
  - **Binary Verification:** Does the file `/home/graham/.claude/commands/slash_test_prompt` exist now? Yes/No

- **[ ] Step 1.2: Create Coded Command File (Tool B)**
  - **MANDATORY DIRECTIVE:** Execute this `cat` command to create a file.
  - **Command:** `cat > /home/graham/.claude/commands/slash_test_coded << 'EOF'
#!/bin/bash
set -e
SCRIPT_PATH="/home/graham/workspace/experiments/llm_call/src/llm_call/usage/test_matrix/functional/usage_F1_6_perplexity_weather.py"
RESULTS_DIR="/home/graham/workspace/experiments/llm_call/src/llm_call/usage/results"
python3 "$SCRIPT_PATH" > /dev/null 2>&1
LATEST_JSON=$(ls -t "$RESULTS_DIR"/*.json | head -n 1)
if [ -z "$LATEST_JSON" ]; then echo "VERIFIED_RESULT: ERROR"; exit 1; fi
SUCCESS_COUNT=$(cat "$LATEST_JSON" | grep '"successful_calls"' | sed 's/[^0-9]*//g')
echo "VERIFIED_RESULT: $SUCCESS_COUNT"
EOF`
  - **Binary Verification:** Does the file `/home/graham/.claude/commands/slash_test_coded` exist now? Yes/No

- **[ ] Step 1.3: Make Coded Command Executable**
  - **MANDATORY DIRECTIVE:** Execute this `chmod` command.
  - **Command:** `chmod +x /home/graham/.claude/commands/slash_test_coded`
  - **Binary Verification:** Run `ls -l /home/graham/.claude/commands/slash_test_coded`. Does the output string contain an 'x'? Yes/No

---

### Phase 2: Execute Tests and Record Artifacts

- **[ ] Step 2.1: Execute Prompt Test (Tool A)**
  - **MANDATORY DIRECTIVE:** Execute the slash command and save its output to a file.
  - **Command:** `/slash_test_prompt > /tmp/v4_result_prompt.txt 2> /tmp/v4_result_prompt_stderr.txt`
  - **Binary Verification:** Does the file `/tmp/v4_result_prompt.txt` exist now? Yes/No

- **[ ] Step 2.2: Execute Coded Test (Tool B)**
  - **MANDATORY DIRECTIVE:** Execute the slash command and save its output to a file.
  - **Command:** `/slash_test_coded > /tmp/v4_result_coded.txt 2> /tmp/v4_result_coded_stderr.txt`
  - **Binary Verification:** Does the file `/tmp/v4_result_coded.txt` exist now? Yes/No

---

### Phase 3: Final Report and External Verification (No Loops)

- **[ ] Step 3.1: Create Instructions for External Reviewer**
  - **MANDATORY DIRECTIVE:** Execute this `cat` command to create the request file.
  - **Command:** `cat > /tmp/v4_request_for_perplexity.md << 'EOF'
ANALYZE THE PROVIDED REPORT FILE.
YOUR TASK IS A BINARY DECISION.
1. Look at the content of 'CODED TEST STDERR'. If it is NOT EMPTY, your ONLY output MUST be the single word: RETRY
2. Look at the content of 'CODED TEST STDOUT'. If it does NOT contain the exact string 'VERIFIED_RESULT: 3', your ONLY output MUST be the single word: RETRY
3. If the above conditions are false, your ONLY output MUST be the single word: HALT
DO NOT PROVIDE ANY OTHER TEXT. YOUR ENTIRE RESPONSE MUST BE 'HALT' OR 'RETRY'.
EOF`
  - **Binary Verification:** Does the file `/tmp/v4_request_for_perplexity.md` exist now? Yes/No

- **[ ] Step 3.2: Compile All Artifacts into a Single Report**
  - **MANDATORY DIRECTIVE:** Execute these `echo` and `cat` commands exactly as written. They build the final report.
  - **Command:** 
    `echo "# v4 TEST REPORT" > /tmp/v4_final_report.md && `
    `echo "\n## PROMPT TEST STDOUT" >> /tmp/v4_final_report.md && `
    `echo '```' >> /tmp/v4_final_report.md && cat /tmp/v4_result_prompt.txt >> /tmp/v4_final_report.md && echo '```' >> /tmp/v4_final_report.md && `
    `echo "\n## PROMPT TEST STDERR" >> /tmp/v4_final_report.md && `
    `echo '```' >> /tmp/v4_final_report.md && cat /tmp/v4_result_prompt_stderr.txt >> /tmp/v4_final_report.md && echo '```' >> /tmp/v4_final_report.md && `
    `echo "\n## CODED TEST STDOUT" >> /tmp/v4_final_report.md && `
    `echo '```' >> /tmp/v4_final_report.md && cat /tmp/v4_result_coded.txt >> /tmp/v4_final_report.md && echo '```' >> /tmp/v4_final_report.md && `
    `echo "\n## CODED TEST STDERR" >> /tmp/v4_final_report.md && `
    `echo '```' >> /tmp/v4_final_report.md && cat /tmp/v4_result_coded_stderr.txt >> /tmp/v4_final_report.md && echo '```' >> /tmp/v4_final_report.md`
  - **Binary Verification:** Does the file `/tmp/v4_final_report.md` exist and have a size greater than zero? Yes/No

- **[ ] Step 3.3: Call External Reviewer and Get Verdict**
  - **MANDATORY DIRECTIVE:** Execute the external tool to get a final verdict.
  - **Command:** `perplexity_cli --prompt-file /tmp/v4_request_for_perplexity.md --context-file /tmp/v4_final_report.md > /tmp/FINAL_VERDICT.txt`
  - **Binary Verification:** Does the file `/tmp/FINAL_VERDICT.txt` exist now? Yes/No

---

### Phase 4: Final Conclusion

- **[ ] Step 4.1: Task Completion Assessment**
  - **MANDATORY DIRECTIVE:** Read the verdict file. Your task is complete regardless of the outcome.
  - **Command:** `cat /tmp/FINAL_VERDICT.txt`
  - **Binary Verification:** This is the final step. The contents of `/tmp/FINAL_VERDICT.txt` determine if the entire task plan needs to be re-run by an external orchestrator. The task for you is now complete. Confirm completion. Yes/No
