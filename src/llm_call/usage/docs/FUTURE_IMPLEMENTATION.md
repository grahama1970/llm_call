# Future Implementation: Multi-AI Consensus Verification

## Overview

Once we have working usage functions for Gemini, Ollama, and Claude Code, we will implement a multi-AI consensus system for automated verification.

## Core Concept

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Gemini    │     │   Ollama    │     │ Claude Code │
│   Judge     │     │   Judge     │     │   Judge     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Consensus   │
                    │   Engine     │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼────┐              ┌────▼────┐
         │   All   │              │ Disagree │
         │  Agree  │              │          │
         └────┬────┘              └────┬────┘
              │                         │
       ┌──────▼──────┐          ┌──────▼──────┐
       │Auto-Approve │          │Human Review │
       └─────────────┘          └─────────────┘
```

## Implementation Plan

### Phase 1: Individual AI Judge Functions
Create usage functions for each AI model that can judge test results:
- `usage_AI_JUDGE_gemini.py` - Uses Gemini to evaluate JSON results
- `usage_AI_JUDGE_ollama.py` - Uses Ollama to evaluate JSON results  
- `usage_AI_JUDGE_claude.py` - Uses Claude to evaluate JSON results

### Phase 2: Consensus Engine
Create a consensus system that:
1. Sends test results JSON to all three AI judges
2. Collects their verdicts
3. Determines consensus or disagreement
4. Routes to appropriate action

### Phase 3: Integration
Modify existing usage functions to:
1. Run the test
2. Send results to consensus engine
3. Display consensus results
4. Only flag for human review if AIs disagree

## Judge Function Template

```python
async def judge_results(test_results_json: dict) -> dict:
    """
    Have an AI model judge test results.
    
    Returns:
        {
            "verdict": "PASS" | "FAIL" | "UNCLEAR",
            "confidence": 0.0-1.0,
            "reasoning": "Detailed explanation",
            "concerns": ["list", "of", "concerns"]
        }
    """
    prompt = f"""
    Analyze these test results and determine if the test passed or failed.
    
    Test Details:
    - Test ID: {test_results_json['test_id']}
    - Expected: {test_results_json['expected']}
    - Results: {test_results_json['results']}
    
    Consider:
    1. Did all methods return similar results?
    2. Do the results match the expected output?
    3. Are there any concerning discrepancies?
    
    Respond with a JSON verdict.
    """
    
    # Call the specific AI model
    response = await llm_call.ask(
        prompt=prompt,
        model=MODEL_NAME,  # gemini-1.5-pro, llama2, claude-3-opus
        response_format={"type": "json_object"}
    )
    
    return json.loads(response)
```

## Consensus Logic

```python
def determine_consensus(verdicts: list[dict]) -> dict:
    """
    Analyze multiple AI verdicts to determine consensus.
    """
    verdict_counts = Counter([v['verdict'] for v in verdicts])
    
    # All agree
    if len(verdict_counts) == 1:
        return {
            "consensus": True,
            "final_verdict": verdicts[0]['verdict'],
            "confidence": "HIGH",
            "action": "AUTO_APPROVE" if verdicts[0]['verdict'] == "PASS" else "AUTO_REJECT"
        }
    
    # Majority agree
    if verdict_counts.most_common(1)[0][1] >= 2:
        return {
            "consensus": False,
            "final_verdict": "REVIEW",
            "confidence": "MEDIUM",
            "action": "HUMAN_REVIEW",
            "ai_verdicts": verdicts
        }
    
    # No agreement
    return {
        "consensus": False,
        "final_verdict": "REVIEW", 
        "confidence": "LOW",
        "action": "HUMAN_REVIEW",
        "ai_verdicts": verdicts
    }
```

## Benefits

1. **Reduced Human Workload**: Only review when AIs disagree
2. **Higher Confidence**: Multiple independent verifications
3. **Catch Edge Cases**: Different AIs may notice different issues
4. **Auditability**: Full record of all AI judgments
5. **Scalability**: Can add more AI judges as needed

## Configuration

```python
# config/consensus_settings.py
CONSENSUS_CONFIG = {
    "judges": [
        {"name": "gemini", "model": "vertex_ai/gemini-1.5-pro", "weight": 1.0},
        {"name": "ollama", "model": "ollama/llama2", "weight": 1.0},
        {"name": "claude", "model": "max/opus", "weight": 1.0}
    ],
    "minimum_agreement": 3,  # All must agree for auto-approval
    "confidence_threshold": 0.8,
    "timeout_seconds": 30
}
```

## Future Enhancements

1. **Weighted Voting**: Give certain AIs more weight based on accuracy
2. **Specialized Judges**: Use different AIs for different test types
3. **Learning System**: Track which AI is most accurate over time
4. **Explanation Synthesis**: Combine all AI explanations into one
5. **Confidence Calibration**: Adjust thresholds based on test criticality

## Key Principle

The multi-AI consensus system maintains the core principle from LESSONS_LEARNED.md:
> "The goal is to **augment human verification, not replace it.**"

We're not replacing human judgment - we're being smarter about when to request it.