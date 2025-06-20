# TASK POLLING VERIFICATION TEST

## PURPOSE (READ THIS FIRST)
Test sequential task execution with background Claude Code verification and polling.
Verify that task polling workflow prevents race conditions and ensures proper task completion before proceeding.

**VERIFICATION GOAL:** Prove that /claude-poll slash command can orchestrate sequential tasks that wait for background Claude Code instances to complete verification.

## CRITICAL LIMITATIONS
Claude Code CANNOT write proper tests. We will use:
- Real data operations (NO MOCKS)
- Background Claude Code instances for verification
- JSON status file polling between tasks
- Forced acknowledgment of failures

## TASKS (SEQUENTIAL - MUST WAIT FOR EACH TO COMPLETE)

### Task 0: Setup Logging
- [ ] Initialize loguru logging to `task_execution.log`
- [ ] Log: "🚀 SEQUENTIAL TASK EXECUTION STARTED"

### Task 1: Create Simple Function with Output
- [ ] Log: "📝 TASK 1 STARTED: Create simple function"
- [ ] Write `simple_add.py` with function that adds two numbers
- [ ] Function must write results to `add_results.txt`
- [ ] Include usage function with `if __name__ == "__main__":` that executes and writes output
- [ ] Log: "✅ TASK 1 COMPLETED: Function created and executed"

### Task 2: Launch Background Claude Code Verification
- [ ] Log: "🔬 TASK 2 STARTED: Launch background verification"
- [ ] Create initial JSON status file `verification_status.json` with status "in-progress"
- [ ] Launch Claude Code background instance (non-interactive) with exact prompt:

**Background Claude Prompt:**
```bash
claude -p "IMPORTANT: Import logging first: from verification_logger import logger
Log: logger.info('🔬 BACKGROUND CLAUDE VERIFICATION STARTED')
Then: Analyze simple_add.py and add_results.txt. Run: python simple_add.py
Log each step with timestamps. Update verification_status.json with this exact format:
{
  \"datetime\": \"2025-06-18T14:30:15.123Z\",
  \"critique\": \"your analysis of code quality and execution\",
  \"status\": \"pass\" or \"fail\",
  \"stdout\": \"output from python simple_add.py\",
  \"stderr\": \"any error messages\"
}
Use Python: import json; data={...}; json.dump(data, open('verification_status.json','w'), indent=2)
Log completion: logger.info('🔬 BACKGROUND VERIFICATION COMPLETE: [status]')" --max-turns 2 &
```

**Requirements:**
- **MUST USE LOGGING**: Import verification_logger and log all steps with timestamps
- Analyze `simple_add.py` code quality
- Read and verify `add_results.txt` output  
- Run the code and capture stdout/stderr
- Status "pass" if code runs correctly, "fail" if issues
- Write JSON file immediately using json.dump()
- **Log file**: `/home/graham/workspace/experiments/llm_call/task_execution.log`

### Task 3: Poll for Verification Completion
- [ ] Log: "🔄 TASK 3 STARTED: Polling for verification completion"
- [ ] Use `/claude-poll` slash command to poll `verification_status.json`
- [ ] Wait until status field equals "pass"
- [ ] MUST NOT proceed until polling completes successfully
- [ ] Document polling duration and iterations
- [ ] Log: "✅ TASK 3 COMPLETED: Verification polling successful"

### Task 4: Answer Simple Question (Only After Verification Passes)
- [ ] Log: "❓ TASK 4 STARTED: Answer question (verification passed)"
- [ ] Answer: "What is the capital of France?"
- [ ] Write answer to `final_answer.txt`
- [ ] ONLY execute this after Task 3 polling confirms "pass" status
- [ ] Log: "🎉 TASK 4 COMPLETED: Sequential execution finished"

## VERIFICATION CRITERIA
- [ ] All tasks execute in sequence (no parallel execution)
- [ ] Task 2 verification runs in background without blocking
- [ ] Task 3 polling prevents Task 4 from starting prematurely
- [ ] Final output files contain expected content:
  - `add_results.txt`: Contains addition results
  - `verification_status.json`: Contains "pass" status with critique
  - `final_answer.txt`: Contains "Paris"

## SUCCESS INDICATORS
- [ ] Sequential execution maintained
- [ ] Background verification completes without manual intervention
- [ ] Polling mechanism works correctly
- [ ] JSON status file updates properly
- [ ] All output files created with correct content

## THAT'S IT. NO ADDITIONAL COMPLEXITY.
This is a proof-of-concept for task polling workflows, not a comprehensive testing framework.