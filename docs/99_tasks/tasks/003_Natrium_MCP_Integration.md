# Task List: LLM Call MCP Integration for Natrium

## Overview
This task list defines the necessary changes to make the LLM Call project easily available as an MCP tool for the Natrium orchestrator. This project is CRITICAL as it enables nested Claude instances with full MCP tool access.

## Core Principle: Enable Nested Claude Instances with Full MCP Access

The Natrium project needs LLM Call to launch background Claude instances that can access ALL MCP tools for research, validation, and complex workflows.

## Task 1: Ensure /max Model Prefix Support

**Goal**: Verify and document /max model prefix functionality

### Working Code Example

Update `evaluate_with_claude` endpoint to handle /max prefix:

```python
@mcp.tool()
async def evaluate_with_claude(
    model: str,
    prompt: str,
    tools_enabled: List[str] = None,
    task_name: str = "evaluation",
    max_iterations: int = 5,
    response_format: str = "json",
    allow_tool_chaining: bool = True,
    enable_reflection: bool = True
) -> dict:
    """
    Launch a background Claude instance with full MCP tool access.
    
    Args:
        model: Model name (use /max prefix for background instance)
        prompt: Task prompt for Claude
        tools_enabled: List of MCP tools to make available
        task_name: Name for tracking
        max_iterations: Max tool calls allowed
        response_format: Expected response format
        allow_tool_chaining: Allow using output of one tool as input to another
        enable_reflection: Allow Claude to reflect and retry
        
    Returns:
        Claude's response with tool usage details
    """
    if model.startswith("/max/"):
        # Launch background instance with full tool access
        actual_model = model.replace("/max/", "")
        
        # Configure MCP tools for background Claude
        mcp_config = {
            "tools": tools_enabled or [
                "arxiv-mcp-server",
                "perplexity-ask",
                "arangodb",
                "marker",
                "brave-search",
                "github",
                "desktop-commander",
                "ripgrep"
            ],
            "allow_chaining": allow_tool_chaining,
            "max_iterations": max_iterations
        }
        
        # Launch background Claude with tools
        response = await launch_claude_with_tools(
            model=actual_model,
            prompt=prompt,
            mcp_config=mcp_config,
            task_name=task_name
        )
        
        return {
            "success": True,
            "model_used": actual_model,
            "tools_available": mcp_config["tools"],
            "response": response,
            "iterations_used": response.get("tool_calls_count", 0)
        }
    else:
        # Regular Claude call without nested tools
        return await standard_claude_call(model, prompt)
```

## Task 2: Add Tool Usage Tracking

**Goal**: Track which tools background Claude uses

### Working Code Example

```python
class ToolUsageTracker:
    """Track MCP tool usage by background Claude instances"""
    
    def __init__(self):
        self.usage_stats = {}
        
    async def log_tool_call(self, task_name: str, tool_name: str, 
                           duration: float, success: bool):
        """Log a tool call"""
        if task_name not in self.usage_stats:
            self.usage_stats[task_name] = {}
            
        if tool_name not in self.usage_stats[task_name]:
            self.usage_stats[task_name][tool_name] = {
                "calls": 0,
                "successes": 0,
                "total_duration": 0
            }
            
        stats = self.usage_stats[task_name][tool_name]
        stats["calls"] += 1
        if success:
            stats["successes"] += 1
        stats["total_duration"] += duration
        
    def get_report(self, task_name: str) -> dict:
        """Get usage report for a task"""
        if task_name not in self.usage_stats:
            return {}
            
        report = {}
        for tool, stats in self.usage_stats[task_name].items():
            report[tool] = {
                "calls": stats["calls"],
                "success_rate": stats["successes"] / stats["calls"] if stats["calls"] > 0 else 0,
                "avg_duration": stats["total_duration"] / stats["calls"] if stats["calls"] > 0 else 0
            }
        return report
```

## Task 3: Add Natrium-Specific Validation Tasks

**Goal**: Pre-configured validation tasks for Natrium documents

### Working Code Example

```python
@mcp.tool()
async def validate_natrium_document(
    document_path: str,
    validation_type: str = "comprehensive"
) -> dict:
    """
    Validate a Natrium document using background Claude.
    
    Args:
        document_path: Path to document
        validation_type: Type of validation to perform
        
    Returns:
        Validation results with confidence scores
    """
    validation_prompts = {
        "comprehensive": """
        You have access to all MCP tools. Perform comprehensive validation:
        
        1. Use marker to extract the document structure
        2. Use arangodb to check for existing related requirements
        3. Use arxiv-mcp-server to verify technical claims
        4. Use perplexity-ask to check current standards
        
        Validate:
        - No contradictions between sections
        - All material specifications are valid
        - Safety requirements are complete
        - References are accurate
        
        Return detailed findings with confidence scores.
        """,
        
        "contradictions": """
        Focus on finding contradictions:
        
        1. Extract all requirements using marker
        2. Store in arangodb with relationships
        3. Query for conflicting requirements
        4. Research similar documents for comparison
        
        Return all contradictions found with severity ratings.
        """,
        
        "technical_accuracy": """
        Verify technical accuracy:
        
        1. Extract all technical specifications
        2. Use arxiv to find supporting research
        3. Use perplexity for current best practices
        4. Compare with industry standards
        
        Return accuracy assessment with citations.
        """
    }
    
    prompt = validation_prompts.get(validation_type, validation_prompts["comprehensive"])
    prompt = f"Document to validate: {document_path}\n\n{prompt}"
    
    result = await evaluate_with_claude(
        model="/max/claude-3-5-sonnet-20241022",
        prompt=prompt,
        task_name=f"natrium_validation_{validation_type}",
        max_iterations=10,
        response_format="json"
    )
    
    return result
```

## Task 4: Add Confidence Scoring

**Goal**: Provide confidence scores for Claude's outputs

### Working Code Example

```python
def calculate_confidence_score(response: dict) -> float:
    """
    Calculate confidence score based on tool usage and results.
    
    Factors:
    - Number of sources consulted
    - Consistency of findings
    - Tool call success rate
    """
    score = 0.5  # Base score
    
    # More sources = higher confidence
    sources_used = response.get("sources_consulted", 0)
    score += min(sources_used * 0.05, 0.2)
    
    # Successful tool calls increase confidence
    tool_success_rate = response.get("tool_success_rate", 0)
    score += tool_success_rate * 0.2
    
    # Consistency across sources
    if response.get("findings_consistent", False):
        score += 0.1
        
    # Clamp to [0, 1]
    return min(max(score, 0), 1)

@mcp.tool()
async def evaluate_with_confidence(
    prompt: str,
    model: str = "/max/claude-3-5-sonnet-20241022"
) -> dict:
    """Evaluate with confidence scoring"""
    
    result = await evaluate_with_claude(
        model=model,
        prompt=prompt,
        enable_reflection=True
    )
    
    confidence = calculate_confidence_score(result)
    
    return {
        **result,
        "confidence_score": confidence,
        "confidence_factors": {
            "sources_consulted": result.get("sources_consulted", 0),
            "tool_success_rate": result.get("tool_success_rate", 0),
            "findings_consistent": result.get("findings_consistent", False)
        }
    }
```

## Task 5: Add Workflow Templates

**Goal**: Pre-built workflows for common Natrium tasks

### Working Code Example

```python
NATRIUM_WORKFLOWS = {
    "research_contradiction": {
        "description": "Research-based contradiction injection",
        "model": "/max/claude-3-5-sonnet-20241022",
        "tools": ["arxiv-mcp-server", "perplexity-ask", "arangodb"],
        "prompt_template": """
        Research and inject sophisticated contradictions:
        
        1. Use arxiv to find papers about: {topic}
        2. Identify real-world failure modes or issues
        3. Query arangodb for related requirements
        4. Create contradictions based on actual problems
        
        Target document: {document_path}
        Severity: {severity}
        Count: {count}
        """
    },
    
    "fix_it_generation": {
        "description": "Generate fix-it tasks for other projects",
        "model": "/max/claude-3-5-sonnet-20241022",
        "tools": ["ripgrep", "github", "desktop-commander"],
        "prompt_template": """
        Analyze {project_name} and generate fix-it tasks:
        
        1. Use ripgrep to search for code patterns
        2. Check github for existing issues
        3. Read documentation with desktop-commander
        4. Generate specific, actionable fix-it tasks
        
        Focus areas: {focus_areas}
        """
    }
}

@mcp.tool()
async def execute_workflow(
    workflow_name: str,
    parameters: dict
) -> dict:
    """Execute a pre-defined Natrium workflow"""
    
    if workflow_name not in NATRIUM_WORKFLOWS:
        return {"error": f"Unknown workflow: {workflow_name}"}
        
    workflow = NATRIUM_WORKFLOWS[workflow_name]
    
    # Fill in prompt template
    prompt = workflow["prompt_template"].format(**parameters)
    
    # Execute with specified configuration
    result = await evaluate_with_claude(
        model=workflow["model"],
        prompt=prompt,
        tools_enabled=workflow["tools"],
        task_name=f"workflow_{workflow_name}",
        max_iterations=15
    )
    
    return result
```

## Task 6: Add Result Caching

**Goal**: Cache results for repeated queries

### Working Code Example

```python
from functools import lru_cache
import hashlib
import json

class ResultCache:
    """Cache for Claude evaluation results"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        
    def _generate_key(self, prompt: str, model: str, tools: List[str]) -> str:
        """Generate cache key"""
        content = f"{prompt}|{model}|{sorted(tools)}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    async def get_or_evaluate(
        self,
        prompt: str,
        model: str,
        tools: List[str],
        force_refresh: bool = False
    ) -> dict:
        """Get from cache or evaluate"""
        
        key = self._generate_key(prompt, model, tools)
        
        if not force_refresh and key in self.cache:
            return {
                **self.cache[key],
                "from_cache": True
            }
            
        # Evaluate
        result = await evaluate_with_claude(
            model=model,
            prompt=prompt,
            tools_enabled=tools
        )
        
        # Cache result
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest = min(self.cache.items(), key=lambda x: x[1].get("timestamp", 0))
            del self.cache[oldest[0]]
            
        self.cache[key] = {
            **result,
            "timestamp": time.time()
        }
        
        return {
            **result,
            "from_cache": False
        }
```

## Task 7: Add Error Recovery

**Goal**: Graceful handling of tool failures

### Working Code Example

```python
class ErrorRecovery:
    """Handle and recover from tool failures"""
    
    @staticmethod
    async def with_retry(
        func,
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ):
        """Execute with exponential backoff retry"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    await asyncio.sleep(wait_time)
                    
        raise last_error
        
    @staticmethod
    async def with_fallback(
        primary_func,
        fallback_func
    ):
        """Try primary, fall back on error"""
        try:
            return await primary_func()
        except Exception as e:
            logging.warning(f"Primary failed: {e}, using fallback")
            return await fallback_func()
```

## Validation Checklist

- [ ] /max prefix launches background Claude with tools
- [ ] All specified MCP tools are accessible
- [ ] Tool usage is tracked and reported
- [ ] Confidence scores are calculated correctly
- [ ] Workflows execute successfully
- [ ] Results are cached appropriately
- [ ] Errors are handled gracefully
- [ ] Integration with Natrium works

## Common Issues & Solutions

### Issue 1: Tools not available to background Claude
```python
# Solution: Ensure MCP tools are properly configured
tools_enabled = verify_tools_available(requested_tools)
if missing := set(requested_tools) - set(tools_enabled):
    logging.warning(f"Missing tools: {missing}")
```

### Issue 2: Background Claude timeouts
```python
# Solution: Increase timeout and add progress tracking
async def evaluate_with_progress(prompt: str, timeout: int = 300):
    task = asyncio.create_task(evaluate_with_claude(prompt))
    
    while not task.done():
        await asyncio.sleep(5)
        progress = get_task_progress(task)
        logging.info(f"Progress: {progress}")
        
    return await task
```

### Issue 3: Inconsistent responses
```python
# Solution: Add validation and retry logic
async def evaluate_with_validation(prompt: str):
    for attempt in range(3):
        result = await evaluate_with_claude(prompt)
        
        if validate_response_structure(result):
            return result
            
    raise ValueError("Failed to get valid response")
```
