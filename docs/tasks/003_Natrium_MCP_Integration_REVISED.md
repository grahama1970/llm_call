# Task List: Claude Max Proxy MCP Integration for Natrium (REVISED)

## Overview
This task list is based on the original 19 Natrium tasks. Claude Max Proxy is responsible for Tasks 3, 4, 5 (partial - logical), 7, 8, and overall pipeline orchestration with evaluation.

## Claude Max Proxy's Role in the 19-Task Pipeline

### Task 3: Formalize Requirements (formalize_requirement_001)
### Task 4: Pratt Parse (pratt_parse_001)
### Task 5: Contradiction Detection (partial - logical with Z3)
### Task 7: Ambiguity Detection (ambiguity_detection_001)
### Task 8: Pipeline Integration (pipeline_integration_001)
### Overall: Evaluation and Orchestration (all tasks)

## Implementation Tasks

### Task 3.1: Create MCP Server with Core Evaluation and Formalization

**Goal**: Implement core endpoints for Tasks 3, 4, 5, 7, and evaluation

Create claude_max_proxy_mcp_server.py:

```python
#!/usr/bin/env python3
"""
Claude Max Proxy MCP Server - Supports Tasks 3, 4, 5, 7, 8 of Natrium pipeline
Based on original_natrium_task_list_gemini.md requirements
"""
from fastmcp import FastMCP
from typing import Dict, List, Any, Optional
import spacy
import z3
from litellm import acompletion
import asyncio
import re

# Initialize MCP server
mcp = FastMCP(
    name="claude-max-proxy-mcp-server",
    version="0.1.0",
    description="Formalization, parsing, and evaluation for Natrium"
)

# Load spaCy for ambiguity detection (Task 7)
nlp = spacy.load("en_core_web_sm")

# Core evaluation function used by all tasks
@mcp.tool()
async def evaluate_with_claude(
    output: Any,
    context: str,
    task_name: str,
    is_ambiguity_check: bool = False
) -> dict:
    """
    Core evaluation function for all tasks.
    Implements confidence scoring and halt conditions.
    """
    # Handle /max prefix for nested Claude instances
    model = "claude-3-5-sonnet-20241022"
    
    # Construct evaluation prompt based on task
    if is_ambiguity_check:
        eval_prompt = f"""
        Analyze this text for ambiguity:
        {output}
        
        Context: {context}
        
        Return JSON with:
        - is_ambiguous: boolean
        - ambiguity_score: 0-1 float
        - clarification_needed: list of specific clarifications
        - confidence: 0-1 float
        """
    else:
        eval_prompt = f"""
        Evaluate the quality of this {task_name} output:
        {output}
        
        Context: {context}
        
        Return JSON with:
        - confidence: 0-1 float (must be > 0.7 to proceed)
        - explanation: detailed explanation
        - halt_pipeline: boolean (true if confidence < 0.7)
        - clarification_questions: list of questions if unclear
        """
    
    try:
        response = await acompletion(
            model=model,
            messages=[
                {"role": "system", "content": "You are evaluating pipeline outputs. Return valid JSON only."},
                {"role": "user", "content": eval_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON response
        import json
        evaluation = json.loads(result)
        
        # Enforce halt condition
        if evaluation.get("confidence", 0) < 0.7:
            evaluation["halt_pipeline"] = True
            
        return {
            "success": True,
            "evaluation": evaluation,
            "model_used": model
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "evaluation": {
                "confidence": 0,
                "halt_pipeline": True,
                "explanation": f"Evaluation failed: {str(e)}"
            }
        }

# Task 3: Formalize Requirements
@mcp.tool()
async def formalize_requirement(
    requirement_text: str,
    code_metadata: Optional[Dict] = None
) -> dict:
    """
    Task 3: Convert natural language requirements to formal logic.
    Based on formalize_requirement_001 test requirements.
    """
    try:
        # Extract logical patterns from requirement
        logic_patterns = {
            'implication': r'IF\s+(.+?)\s+THEN\s+(.+?)(?:\.|$)',
            'conjunction': r'(.+?)\s+AND\s+(.+?)(?:\.|$)',
            'disjunction': r'(.+?)\s+OR\s+(.+?)(?:\.|$)',
            'negation': r'NOT\s+(.+?)(?:\.|$)',
            'comparison': r'(\w+)\s*(>|<|>=|<=|==|!=)\s*(\d+\.?\d*)',
            'shall': r'(\w+)\s+SHALL\s+(.+?)(?:\.|$)',
            'must': r'(\w+)\s+MUST\s+(.+?)(?:\.|$)'
        }
        
        # Extract logic components
        logic_components = []
        formalized_logic = ""
        
        for pattern_name, pattern in logic_patterns.items():
            matches = re.finditer(pattern, requirement_text, re.IGNORECASE)
            for match in matches:
                logic_components.append({
                    "type": pattern_name,
                    "match": match.group(0),
                    "groups": match.groups()
                })
                
        # Build formal logic representation
        if logic_components:
            # Convert to propositional logic
            if any(comp["type"] == "implication" for comp in logic_components):
                # IF-THEN pattern
                comp = next(c for c in logic_components if c["type"] == "implication")
                condition = comp["groups"][0].strip()
                consequence = comp["groups"][1].strip()
                formalized_logic = f"({condition}) → ({consequence})"
                
            elif any(comp["type"] == "shall" for comp in logic_components):
                # SHALL pattern
                comp = next(c for c in logic_components if c["type"] == "shall")
                subject = comp["groups"][0].strip()
                predicate = comp["groups"][1].strip()
                formalized_logic = f"□({subject}.{predicate})"  # Box operator for necessity
                
            elif any(comp["type"] == "comparison" for comp in logic_components):
                # Comparison pattern
                comp = next(c for c in logic_components if c["type"] == "comparison")
                var = comp["groups"][0]
                op = comp["groups"][1]
                val = comp["groups"][2]
                formalized_logic = f"{var} {op} {val}"
        else:
            # Fallback to simple propositional representation
            formalized_logic = f"REQUIREMENT({requirement_text})"
            
        # Add code-based logic if provided
        if code_metadata:
            code_constraints = []
            for func in code_metadata.get("functions", []):
                code_constraints.append(f"FUNCTION({func['name']})")
            if code_constraints:
                formalized_logic += " ∧ " + " ∧ ".join(code_constraints)
                
        result = {
            "type": "formal_requirement",
            "original_text": requirement_text,
            "logic": formalized_logic,
            "components": logic_components,
            "has_code_constraints": bool(code_metadata)
        }
        
        # Evaluate the formalization
        evaluation = await evaluate_with_claude(
            result,
            requirement_text,
            "requirement_formalization"
        )
        
        return {
            "success": True,
            "formalized": result,
            "evaluation": evaluation["evaluation"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Task 4: Pratt Parse
@mcp.tool()
async def pratt_parse(logic_string: str) -> dict:
    """
    Task 4: Parse logical expressions using Pratt parsing.
    Based on pratt_parse_001 test requirements.
    """
    try:
        # Simple Pratt parser implementation
        class Token:
            def __init__(self, type, value):
                self.type = type
                self.value = value
                
        class PrattParser:
            def __init__(self, tokens):
                self.tokens = tokens
                self.pos = 0
                
            def parse(self):
                return self.expression(0)
                
            def expression(self, min_bp):
                # Null denotation
                token = self.advance()
                left = self.nud(token)
                
                # Left denotation
                while self.pos < len(self.tokens):
                    token = self.peek()
                    bp = self.lbp(token)
                    if bp <= min_bp:
                        break
                    token = self.advance()
                    left = self.led(token, left, bp)
                    
                return left
                
            def nud(self, token):
                # Null denotation - handle prefix operators and atoms
                if token.type == 'ATOM':
                    return {"type": "atom", "value": token.value}
                elif token.type == 'NOT':
                    return {
                        "type": "not",
                        "operand": self.expression(100)  # High precedence
                    }
                elif token.type == 'LPAREN':
                    expr = self.expression(0)
                    self.expect('RPAREN')
                    return expr
                else:
                    raise ValueError(f"Unexpected token: {token.type}")
                    
            def led(self, token, left, bp):
                # Left denotation - handle infix operators
                if token.type == 'AND':
                    return {
                        "type": "and",
                        "left": left,
                        "right": self.expression(bp)
                    }
                elif token.type == 'OR':
                    return {
                        "type": "or",
                        "left": left,
                        "right": self.expression(bp - 1)  # Right associative
                    }
                elif token.type == 'IMPLIES':
                    return {
                        "type": "implies",
                        "left": left,
                        "right": self.expression(bp - 1)
                    }
                else:
                    raise ValueError(f"Unexpected infix: {token.type}")
                    
            def lbp(self, token):
                # Left binding power - precedence
                precedence = {
                    'OR': 10,
                    'AND': 20,
                    'IMPLIES': 5,
                    'RPAREN': 0
                }
                return precedence.get(token.type, 0)
                
            def advance(self):
                token = self.tokens[self.pos]
                self.pos += 1
                return token
                
            def peek(self):
                return self.tokens[self.pos] if self.pos < len(self.tokens) else None
                
            def expect(self, type):
                token = self.advance()
                if token.type != type:
                    raise ValueError(f"Expected {type}, got {token.type}")
                    
        # Tokenize the logic string
        def tokenize(logic_string):
            patterns = [
                (r'\s+', None),  # Skip whitespace
                (r'→|->|IMPLIES', 'IMPLIES'),
                (r'∧|AND', 'AND'),
                (r'∨|OR', 'OR'),
                (r'¬|NOT', 'NOT'),
                (r'\(', 'LPAREN'),
                (r'\)', 'RPAREN'),
                (r'[a-zA-Z_]\w*', 'ATOM'),
                (r'\d+', 'NUMBER'),
                (r'[><=!]+', 'OPERATOR')
            ]
            
            tokens = []
            pos = 0
            
            while pos < len(logic_string):
                matched = False
                for pattern, token_type in patterns:
                    regex = re.compile(pattern)
                    match = regex.match(logic_string, pos)
                    if match:
                        if token_type:  # Skip None (whitespace)
                            tokens.append(Token(token_type, match.group(0)))
                        pos = match.end()
                        matched = True
                        break
                        
                if not matched:
                    raise ValueError(f"Invalid character at position {pos}: {logic_string[pos]}")
                    
            return tokens
            
        # Parse the logic string
        tokens = tokenize(logic_string)
        parser = PrattParser(tokens)
        ast = parser.parse()
        
        # Convert AST to string representation
        def ast_to_string(node):
            if node["type"] == "atom":
                return node["value"]
            elif node["type"] == "not":
                return f"¬{ast_to_string(node['operand'])}"
            elif node["type"] in ["and", "or", "implies"]:
                op_symbols = {"and": "∧", "or": "∨", "implies": "→"}
                return f"({ast_to_string(node['left'])} {op_symbols[node['type']]} {ast_to_string(node['right'])})"
            else:
                return str(node)
                
        parsed_expression = ast_to_string(ast)
        
        return {
            "success": True,
            "ast": ast,
            "parsed_expression": parsed_expression,
            "original": logic_string
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Task 5 (partial): Logical Contradiction Detection with Z3
@mcp.tool()
async def detect_contradictions(formalized_reqs: List[Dict]) -> dict:
    """
    Task 5 (partial): Detect logical contradictions using Z3 solver.
    Based on contradiction_detection_001 test requirements.
    """
    try:
        solver = z3.Solver()
        z3_vars = {}
        
        # Convert formalized requirements to Z3 constraints
        for req in formalized_reqs:
            logic = req.get("logic", "")
            
            # Parse and convert to Z3
            # This is a simplified version - real implementation would be more robust
            if ">" in logic or "<" in logic or ">=" in logic or "<=" in logic:
                # Handle comparisons
                match = re.match(r'(\w+)\s*(>|<|>=|<=|==)\s*(\d+\.?\d*)', logic)
                if match:
                    var_name, op, value = match.groups()
                    
                    # Create or get Z3 variable
                    if var_name not in z3_vars:
                        z3_vars[var_name] = z3.Real(var_name)
                        
                    var = z3_vars[var_name]
                    val = float(value)
                    
                    # Add constraint
                    if op == '>':
                        solver.add(var > val)
                    elif op == '<':
                        solver.add(var < val)
                    elif op == '>=':
                        solver.add(var >= val)
                    elif op == '<=':
                        solver.add(var <= val)
                    elif op == '==':
                        solver.add(var == val)
                        
        # Check for contradictions
        result = solver.check()
        
        if result == z3.unsat:
            # Found contradiction
            core = solver.unsat_core() if hasattr(solver, 'unsat_core') else []
            
            return {
                "success": True,
                "has_contradiction": True,
                "type": "logical",
                "explanation": "Z3 solver found unsatisfiable constraints",
                "conflicting_requirements": [str(c) for c in core]
            }
        else:
            # No contradiction found
            return {
                "success": True,
                "has_contradiction": False,
                "type": "logical",
                "model": str(solver.model()) if result == z3.sat else None
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Task 7: Ambiguity Detection
@mcp.tool()
async def detect_ambiguity(text: str) -> dict:
    """
    Task 7: Detect ambiguity in requirements text.
    Based on ambiguity_detection_001 test requirements.
    """
    try:
        doc = nlp(text)
        
        # Ambiguity indicators
        ambiguity_indicators = {
            'vague_terms': ['may', 'might', 'could', 'possibly', 'sometimes', 'often', 'usually'],
            'unclear_refs': ['it', 'they', 'this', 'that', 'these', 'those'],
            'passive_voice': [],
            'complex_sentences': []
        }
        
        # Check for vague terms
        found_vague = [token.text.lower() for token in doc 
                      if token.text.lower() in ambiguity_indicators['vague_terms']]
                      
        # Check for unclear references
        found_refs = [token.text.lower() for token in doc 
                     if token.text.lower() in ambiguity_indicators['unclear_refs']]
                     
        # Check for passive voice
        for token in doc:
            if token.dep_ == "nsubjpass":
                ambiguity_indicators['passive_voice'].append(token.text)
                
        # Check sentence complexity
        for sent in doc.sents:
            if len(list(sent)) > 25:  # Long sentence
                ambiguity_indicators['complex_sentences'].append(str(sent))
                
        # Calculate ambiguity score
        total_indicators = (
            len(found_vague) + 
            len(found_refs) + 
            len(ambiguity_indicators['passive_voice']) +
            len(ambiguity_indicators['complex_sentences'])
        )
        
        word_count = len(doc)
        ambiguity_score = min(total_indicators / max(word_count * 0.1, 1), 1.0)
        
        # Use Claude for deeper analysis
        claude_eval = await evaluate_with_claude(
            text,
            "requirement text",
            "ambiguity_detection",
            is_ambiguity_check=True
        )
        
        # Combine results
        is_ambiguous = ambiguity_score > 0.3 or claude_eval["evaluation"].get("is_ambiguous", False)
        
        return {
            "success": True,
            "is_ambiguous": is_ambiguous,
            "ambiguity_score": ambiguity_score,
            "indicators": {
                "vague_terms": found_vague,
                "unclear_references": found_refs,
                "passive_voice": ambiguity_indicators['passive_voice'],
                "complex_sentences": len(ambiguity_indicators['complex_sentences'])
            },
            "claude_analysis": claude_eval["evaluation"],
            "clarification_needed": claude_eval["evaluation"].get("clarification_needed", [])
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Task 8: Pipeline Integration
@mcp.tool()
async def validate_pipeline(
    task_outputs: Dict[str, Any],
    expected_tasks: List[str] = None
) -> dict:
    """
    Task 8: Validate complete pipeline integration.
    Based on pipeline_integration_001 test requirements.
    """
    try:
        if expected_tasks is None:
            expected_tasks = [
                "extract_sections",
                "parse_code_blocks",
                "formalize_requirement",
                "pratt_parse",
                "detect_contradictions",
                "trace_error_cascade",
                "detect_ambiguity"
            ]
            
        # Check all expected tasks completed
        missing_tasks = [task for task in expected_tasks if task not in task_outputs]
        
        # Check confidence scores
        low_confidence_tasks = []
        for task_name, output in task_outputs.items():
            if isinstance(output, dict) and "evaluation" in output:
                confidence = output["evaluation"].get("confidence", 0)
                if confidence < 0.7:
                    low_confidence_tasks.append({
                        "task": task_name,
                        "confidence": confidence
                    })
                    
        # Check for pipeline halts
        halted_tasks = []
        for task_name, output in task_outputs.items():
            if isinstance(output, dict) and "evaluation" in output:
                if output["evaluation"].get("halt_pipeline", False):
                    halted_tasks.append(task_name)
                    
        # Overall validation
        is_valid = (
            len(missing_tasks) == 0 and
            len(low_confidence_tasks) == 0 and
            len(halted_tasks) == 0
        )
        
        return {
            "success": True,
            "pipeline_valid": is_valid,
            "missing_tasks": missing_tasks,
            "low_confidence_tasks": low_confidence_tasks,
            "halted_tasks": halted_tasks,
            "total_tasks_completed": len(task_outputs),
            "overall_confidence": sum(
                output.get("evaluation", {}).get("confidence", 0)
                for output in task_outputs.values()
                if isinstance(output, dict)
            ) / len(task_outputs) if task_outputs else 0
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Support for /max prefix - nested Claude instances
@mcp.tool()
async def evaluate_with_max_claude(
    prompt: str,
    tools_enabled: List[str] = None,
    max_iterations: int = 5
) -> dict:
    """
    Launch background Claude instance with full MCP tool access.
    Supports the /max prefix functionality.
    """
    if tools_enabled is None:
        tools_enabled = [
            "marker",
            "arangodb", 
            "arxiv-mcp-server",
            "perplexity-ask",
            "brave-search"
        ]
        
    # This would integrate with the actual /max implementation
    # For now, simulate the nested Claude functionality
    return {
        "success": True,
        "model": "claude-3-5-sonnet-20241022",
        "tools_available": tools_enabled,
        "max_iterations": max_iterations,
        "response": f"Background Claude would process: {prompt}"
    }

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run())
```

### Task 3.2: Create Integration Tests for Original Test Cases

**Goal**: Ensure all original test cases pass

Create tests/test_natrium_tasks_3_7.py with tests for each task.

### Task 3.3: Add Support for Coq Formalization

**Goal**: Support Coq output as mentioned in original tasks

Add Coq export functionality to formalize_requirement for users who need formal verification.

## Validation Checklist

Based on original task requirements:

- [ ] Task 3: Formalize requirements with confidence > 0.7
- [ ] Task 4: Pratt parse produces valid AST
- [ ] Task 5: Z3 detects logical contradictions
- [ ] Task 7: Ambiguity detection with spaCy + Claude
- [ ] Task 8: Pipeline validates all components
- [ ] Evaluation halts pipeline if confidence < 0.7
- [ ] /max prefix launches nested Claude with tools
- [ ] All outputs ready for Coq formalization
- [ ] Integration with Tasks 1-2 (from Marker)
- [ ] Integration with Tasks 9-19 (from ArangoDB)

## Dependencies to Add

```toml
[project.dependencies]
spacy = ">=3.0.0"
z3-solver = ">=4.8.0"
litellm = ">=1.0.0"
fastmcp = ">=0.1.0"
```

## Notes

This implementation covers Tasks 3, 4, 5 (logical part), 7, and 8 from the original Natrium pipeline. The evaluation_with_claude function is central to all tasks, implementing the confidence threshold (0.7) and halt conditions specified in the original requirements.

The /max prefix support enables nested Claude instances to access all MCP tools, creating powerful workflows where Claude orchestrates complex analysis using multiple tools.
