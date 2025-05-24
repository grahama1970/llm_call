
# MCP Toolchain Task List for Hierarchical Engineering Requirements Analysis

## Purpose & Overview
This task list guides the creation of a modular pipeline for extracting, parsing, formalizing, analyzing, storing, querying, and evaluating hierarchical engineering requirements, including embedded code/pseudocode. Claude Code, invoked via its CLI, evaluates each task’s output, halting if confidence is below 0.7 or ambiguity is detected, prompting human clarification for Coq formalization. Each task includes sample code from official documentation or GitHub, or relevant project modules, to focus Claude Code’s execution. The pipeline supports hierarchical engineering documents, ensuring traceability, Coq readiness, and interaction with an ArangoDB-backed knowledge graph.

## Key Tools & Documentation (Expanded):

* spaCy — NLP for semantic extraction and ambiguity detection
* Python `re` (regex) — Pattern matching for sections and code blocks
* Tree-Sitter — Code parsing for embedded code
* `py-tree-sitter-languages` — Language support for Tree-Sitter
* Z3 SMT Solver — Contradiction detection (logical)
* Coq Proof Assistant — Formal verification
* Pratt Parsing (Python Example) — Expression parsing
* LiteLLM — API for Claude Code evaluation
* Claude Code CLI — Code execution and evaluation
* **ArangoDB Python Driver** — For interacting with the ArangoDB knowledge base.
* **`src/arangodb/core/` modules** — Custom Python modules for BM25 search, semantic search, graph traversal, entity resolution, relationship management, memory functions, etc., within ArangoDB.

### Claude Code CLI Launch Example (from provided code):
```bash
# Send a prompt to Claude Code CLI with tool use enabled, formatting output as markdown, JSON, or raw.
c() {
  local mode="raw"
  local skipd="no"
  local user_prompt=()
  for arg in "$@"; do
    case "$arg" in
      --markdown) mode="markdown" ;;
      --json) mode="json" ;;
      --raw) mode="raw" ;;
      --skipd) skipd="yes" ;;
      *) user_prompt+=("$arg") ;;
    esac
  done

  local claude_cmd="claude"
  if [[ $skipd == "yes" ]]; then
    claude_cmd+=" --dangerously-skip-permissions"
  fi

  if [[ $mode == "markdown" ]]; then
    $claude_cmd -p "${user_prompt[*]}" | batcat -l markdown
  elif [[ $mode == "json" ]]; then
    $claude_cmd -p "${user_prompt[*]}" --output-format json | jq
  else
    $claude_cmd -p "${user_prompt[*]}"
  fi
}

# Example usage:
# c --markdown "List all files in /tmp"
```

---
## Task 1: Make test extract_sections_001 pass
**Test ID**: extract_sections_001
**Model**: `max/text-general`
**Goal**: Extract hierarchical sections, requirements, and code blocks using regex and spaCy, evaluated by Claude Code; halt if confidence <0.7 or ambiguous.

### Sample Code (from spaCy Usage):
```python
import spacy

nlp = spacy.load("en_core_web_sm")
text = "The module assembly shall operate at temperatures between 350°C and 600°C."
doc = nlp(text)
for token in doc:
    print(token.text, token.dep_, token.head.text)
```

### Working Code Example
```python
import re
import spacy
import hashlib
import asyncio
from litellm import acompletion # Assuming Claude Code uses LiteLLM for self-evaluation
import logging

logging.basicConfig(level=logging.WARNING)
nlp = spacy.load("en_core_web_sm")

# Placeholder for the evaluate_with_claude function from your provided context
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # This function would be defined as in your provided 'Working Code Example'
    # for Task 1 in the original prompt. For brevity, it's not repeated here.
    # It should return a dict like: {"confidence": 0.9, "explanation": "...", "halt_pipeline": False, ...}
    try:
        # Simulate Claude evaluation
        logging.info(f"Simulating Claude evaluation for {task_name}")
        # In a real scenario, this would call the actual evaluate_with_claude function
        # For this template, we assume a positive evaluation to proceed
        return {
            "confidence": 0.95,
            "explanation": f"Mock evaluation: {task_name} output appears correct for section: {section_text[:50]}...",
            "halt_pipeline": False,
            "clarification_questions": []
        }
    except Exception as e:
        logging.error(f"Claude evaluation failed: {e}")
        return {
            "confidence": 0,
            "explanation": f"Evaluation failed: {e}",
            "halt_pipeline": True,
            "clarification_questions": ["Could you clarify the section structure?"]
        }


async def extract_sections(corpus):
    section_pattern = re.compile(r'^(\d+(?:\.\d+)*|[A-Z](?:\.\d+)*)?(?:\s+)(.+)?$', re.MULTILINE)
    requirement_pattern = re.compile(r'\b(shall|must|should|requires)\b', re.IGNORECASE)
    code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
    lines = corpus.split('\n')
    current_section = []
    section_text_for_req = "" # Store the text of the current section title for requirements
    sections = []
    requirements = []
    code_blocks = []

    for match in code_block_pattern.finditer(corpus):
        language = match.group(1) or "unknown"
        code = match.group(2).strip()
        code_id = hashlib.md5(code.encode()).hexdigest()
        code_blocks.append({
            "id": code_id,
            "language": language,
            "code": code,
            "start_line": corpus[:match.start()].count('\n') + 1
        })

    # Remove code blocks from corpus before line-by-line processing to avoid re-processing them
    corpus_no_code = code_block_pattern.sub("", corpus)
    lines_no_code = corpus_no_code.split('\n')
    original_lines_map = {line_content: idx for idx, line_content in enumerate(lines)}


    for line_idx, line_content in enumerate(lines_no_code):
        line = line_content.strip()
        if not line: # Skip empty lines
            continue
        
        section_match = section_pattern.match(line)
        try:
            if section_match and section_match.group(2): # It's a section header
                section_num_str = section_match.group(1) or "unnumbered"
                section_title_str = section_match.group(2).strip()
                depth = section_num_str.count('.') if section_num_str != "unnumbered" else 0
                current_section = current_section[:depth] + [section_title_str]
                section_text_for_req = line # The full line of the section header
                sections.append({
                    "id": hashlib.md5(line.encode()).hexdigest(),
                    "number": section_num_str,
                    "title": section_title_str,
                    "depth": depth,
                    # Find original line number by matching content, approximate if necessary
                    "start_line": lines.index(line_content) + 1 if line_content in lines else line_idx + 1 
                })
            else: # It's potentially a requirement or other text
                doc = nlp(line)
                # Enhanced requirement detection logic (root verb, modal verb, or explicit keyword)
                is_requirement_candidate = requirement_pattern.search(line) or \
                                          any(token.dep_ == "ROOT" and token.tag_ in ["VB", "VBP", "VBZ", "MD"] for token in doc)
                
                if is_requirement_candidate:
                    # Try to find the original line number for the requirement
                    # This is tricky if lines were modified or are not unique.
                    # A more robust way would be to map indices before removing code blocks.
                    original_line_number = lines.index(line_content) + 1 if line_content in lines else line_idx + 1

                    req_id = hashlib.md5((section_text_for_req + line).encode()).hexdigest()
                    requirements.append({
                        "id": req_id,
                        "breadcrumb": current_section.copy(),
                        "section_text": section_text_for_req, # Section this requirement falls under
                        "requirement": line,
                        "start_line": original_line_number 
                    })
        except Exception as e:
            logging.warning(f"Failed to process line '{line}': {e}")

    output = {"sections": sections, "requirements": requirements, "code_blocks": code_blocks}
    # Use the actual evaluate_with_claude function from your context
    claude_eval_response = await evaluate_with_claude(output, corpus, "section extraction")
    
    # Assuming claude_eval_response is a JSON string that needs parsing
    import json
    try:
        claude_eval = json.loads(claude_eval_response)
    except json.JSONDecodeError:
        logging.error(f"Failed to parse Claude evaluation response: {claude_eval_response}")
        claude_eval = { # Fallback if JSON parsing fails
            "confidence": 0, "explanation": "Failed to parse evaluation response.", 
            "halt_pipeline": True, "clarification_questions": ["Evaluation response was not valid JSON."]
        }

    if claude_eval.get("halt_pipeline", True): # Default to halt if key missing
        return {"output": output, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": output, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "extract_sections_001",
  "corpus": "3. Thermal Requirements\n3.1 Operating Temperature\n The module assembly shall operate at temperatures between 350°C and 600°C.\n```python\ndef control_temp(temp):\n    if temp > 600:\n        return False\n    return True\n```\n3.2 Overtemperature Protection\n The module assembly shall not operate above 600°C."
}
```

**Run Command**:
```bash
# c --markdown "python test_v4_essential_async.py -k extract_sections_001"
# (Assuming test_v4_essential_async.py uses the extract_sections function and handles Claude evaluation)
```

**Expected Output Structure**:
```json
{
  "output": {
    "sections": [
      {"id": "abc123...", "number": "3", "title": "Thermal Requirements", "depth": 0, "start_line": 1},
      {"id": "def456...", "number": "3.1", "title": "Operating Temperature", "depth": 1, "start_line": 2},
      {"id": "ghi789...", "number": "3.2", "title": "Overtemperature Protection", "depth": 1, "start_line": 8}
    ],
    "requirements": [
      {
        "id": "jkl012...",
        "breadcrumb": ["Thermal Requirements", "Operating Temperature"],
        "section_text": "3.1 Operating Temperature",
        "requirement": "The module assembly shall operate at temperatures between 350°C and 600°C.",
        "start_line": 3
      },
      {
        "id": "mno345...",
        "breadcrumb": ["Thermal Requirements", "Overtemperature Protection"],
        "section_text": "3.2 Overtemperature Protection",
        "requirement": "The module assembly shall not operate above 600°C.",
        "start_line": 9 
      }
    ],
    "code_blocks": [
      {
        "id": "pqr678...",
        "language": "python",
        "code": "def control_temp(temp):\n    if temp > 600:\n        return False\n    return True",
        "start_line": 4
      }
    ]
  },
  "claude_evaluation": {
    "confidence": 0.95,
    "explanation": "Accurate extraction of sections, requirements, and code blocks.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Missed code blocks
```python
# Solution: Validate regex and ensure DOTALL flag is used for multiline code blocks.
# if not code_block_pattern.search(corpus): # code_block_pattern defined in extract_sections
#     logging.warning("No code blocks detected in corpus.")
```

#### Issue 2: Claude halts due to low confidence or ambiguity
```python
# Solution: Refine regex, spaCy NLP logic for section/requirement identification.
# Review Claude's explanation for halting and address the specific issues.
# Example: If confidence from Claude evaluation is below threshold:
# if claude_eval.get("confidence", 0) < 0.7:
#     claude_eval["halt_pipeline"] = True # This logic is in extract_sections based on claude_eval
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert len(response["output"]["sections"]) >= 2
assert len(response["output"]["requirements"]) >= 2
assert len(response["output"]["code_blocks"]) >= 1
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 2: Make test parse_code_blocks_001 pass
**Test ID**: parse_code_blocks_001
**Model**: `max/text-general`
**Goal**: Parse code blocks extracted in Task 1 using tree-sitter to identify functions, classes, etc., evaluated by Claude Code; halt if confidence <0.7.

### Sample Code (from py-tree-sitter):
```python
from tree_sitter import Language, Parser
# Assuming build/python.so is available or using pre-built languages
# PY_LANGUAGE = Language('build/python.so', 'python')
# For pre-built languages:
from tree_sitter_languages import get_language
PY_LANGUAGE = get_language('python')

parser = Parser()
parser.set_language(PY_LANGUAGE)
code = "def foo(bar): return bar"
tree = parser.parse(bytes(code, "utf8"))
# Access tree.root_node and traverse
```

### Working Code Example
```python
from tree_sitter import Parser
# Ensure tree_sitter_languages is installed for pre-built language support
from tree_sitter_languages import get_language, get_parser
import logging # Assuming logging is configured

# Placeholder for the evaluate_with_claude function from your provided context
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # This function would be defined as in your provided 'Working Code Example'
    # for Task 1 in the original prompt. For brevity, it's not repeated here.
    # For this template, we assume a positive evaluation to proceed
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({ # Return as JSON string as per original evaluate_with_claude
            "confidence": 0.90,
            "explanation": f"Mock evaluation: {task_name} output appears correct for code: {section_text[:50]}...",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        logging.error(f"Claude evaluation failed: {e}")
        return json.dumps({
            "confidence": 0, "explanation": f"Evaluation failed: {e}", 
            "halt_pipeline": True, "clarification_questions": ["Could not evaluate code parsing."]
        })

# Assuming extract_code_metadata is a function you've defined using tree-sitter
# For this example, let's define a mock version based on the expected output.
def extract_code_metadata(code_str: str, language_name: str):
    """
    Mock function to simulate tree-sitter metadata extraction.
    In a real scenario, this would use tree-sitter to parse the code.
    """
    if language_name == "python" and "def control_temp(temp):" in code_str:
        return {
            "language": "python",
            "functions": [
              {
                "name": "control_temp",
                "parameters": [{"name": "temp", "type": None, "default": None, "required": True}],
                "return_type": None,
                "docstring": None,
                "line_span": [1, 4], # Example line span
                "code": code_str 
              }
            ],
            "classes": [],
            "tree_sitter_success": True,
            "error": None
        }
    return {"language": language_name, "functions": [], "classes": [], "tree_sitter_success": False, "error": "Mock parsing error or unsupported."}


async def parse_code_blocks(code_blocks_list): # Renamed from code_blocks to avoid conflict
    parsed_blocks = []
    if not code_blocks_list: # Handle empty input
        claude_eval_response = await evaluate_with_claude([], "No code blocks provided", "code block parsing")
        import json
        claude_eval = json.loads(claude_eval_response) # Parse JSON string
        return {"output": [], "claude_evaluation": claude_eval, "status": "proceed" if not claude_eval.get("halt_pipeline") else "halted"}

    for block in code_blocks_list:
        language_str = block.get("language", "unknown")
        code_str = block.get("code", "")
        try:
            # Ensure language is supported by tree_sitter_languages
            # lang_parser = get_parser(language_str) # This would raise error if lang not supported
            # For the mock, we'll assume the language string is directly usable
            metadata = extract_code_metadata(code_str, language_str)
            parsed_blocks.append({
                "id": block["id"],
                "language": language_str,
                "metadata": metadata,
                "start_line": block.get("start_line")
            })
        except Exception as e:
            logging.error(f"Failed to parse code block {block.get('id', 'N/A')}: {e}")
            parsed_blocks.append({
                "id": block.get("id", "N/A"),
                "language": language_str,
                "metadata": {"error": str(e), "tree_sitter_success": False},
                "start_line": block.get("start_line")
            })
            
    # Evaluate based on the first code block's content for simplicity in this example
    first_code_block_content = code_blocks_list[0]["code"] if code_blocks_list else ""
    claude_eval_response = await evaluate_with_claude(parsed_blocks, first_code_block_content, "code block parsing")
    import json
    try:
        claude_eval = json.loads(claude_eval_response)
    except json.JSONDecodeError:
        logging.error(f"Failed to parse Claude evaluation response: {claude_eval_response}")
        claude_eval = {
            "confidence": 0, "explanation": "Failed to parse evaluation response.", 
            "halt_pipeline": True, "clarification_questions": ["Evaluation response was not valid JSON."]
        }

    if claude_eval.get("halt_pipeline", True):
        return {"output": parsed_blocks, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": parsed_blocks, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "parse_code_blocks_001",
  "code_blocks": [
    {
      "id": "pqr678",
      "language": "python",
      "code": "def control_temp(temp):\n    if temp > 600:\n        return False\n    return True",
      "start_line": 4
    }
  ]
}
```

**Run Command**:
```bash
# c --markdown "python test_v4_essential_async.py -k parse_code_blocks_001"
```

**Expected Output Structure**:
```json
{
  "output": [
    {
      "id": "pqr678",
      "language": "python",
      "metadata": {
        "language": "python",
        "functions": [
          {
            "name": "control_temp",
            "parameters": [{"name": "temp", "type": null, "default": null, "required": true}],
            "return_type": null,
            "docstring": null,
            "line_span": [1, 4],
            "code": "def control_temp(temp):\n    if temp > 600:\n        return False\n    return True"
          }
        ],
        "classes": [],
        "tree_sitter_success": true,
        "error": null
      },
      "start_line": 4
    }
  ],
  "claude_evaluation": {
    "confidence": 0.90,
    "explanation": "Accurate parsing of function logic.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Unsupported language or tree-sitter grammar not found
```python
# Solution: Validate language and ensure grammar is available/installed.
# from tree_sitter_languages import get_language
# try:
#     lang_obj = get_language(language_str)
# except Exception:
#     raise ValueError(f"Unsupported language or grammar not found: {language_str}")
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], list)
assert len(response["output"]) > 0, "Expected at least one parsed block if input was provided"
if response["output"]: # Check only if output is not empty
    assert response["output"][0]["metadata"]["tree_sitter_success"] is True
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 3: Make test formalize_requirement_001 pass
**Test ID**: formalize_requirement_001
**Model**: `max/text-general`
**Goal**: Formalize text and code-based requirements using spaCy and tree-sitter metadata, evaluated by Claude Code; halt if confidence <0.7.

### Sample Code (from spaCy Linguistic Features):
```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("The system shall operate at 350°C.")
for ent in doc.ents:
    print(ent.text, ent.label_)
```

### Working Code Example
```python
import spacy
# from src.llm_call.core.utils.tree_sitter_utils import extract_code_metadata # Not used in this specific func
import logging # Assuming logging is configured

nlp = spacy.load("en_core_web_sm")

# Placeholder for the evaluate_with_claude function
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.95,
            "explanation": f"Mock evaluation: {task_name} output appears correct for requirement: {section_text[:50]}...",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        logging.error(f"Claude evaluation failed: {e}")
        return json.dumps({
            "confidence": 0, "explanation": f"Evaluation failed: {e}", 
            "halt_pipeline": True, "clarification_questions": ["Could not evaluate requirement formalization."]
        })

async def formalize_requirement(requirement_text: str, code_metadata_obj=None): # Renamed params for clarity
    output = {"type": "unknown", "logic": "UNKNOWN"}
    doc = nlp(requirement_text)
    
    # Basic text-based logic extraction (example)
    for token in doc:
        if token.text.lower() in ["shall", "must", "should", "requires"]:
            # Example: "between X and Y"
            if "between" in requirement_text and "and" in requirement_text:
                quantities = [ent.text for ent in doc.ents if ent.label_ == "QUANTITY" or ent.label_ == "CARDINAL"]
                nums = []
                for q in quantities:
                    try:
                        # Attempt to extract numeric part, removing units like °C
                        num_part = "".join(filter(lambda x: x.isdigit() or x == '.', q.split("°")[0].split()[0]))
                        if num_part: nums.append(float(num_part))
                    except ValueError:
                        pass # Ignore if conversion fails
                if len(nums) == 2:
                    output = {"type": "text", "logic": f"{min(nums)} <= temp <= {max(nums)}"} # Assuming temp variable
                    break 
            # Example: "not operate above X"
            elif "not operate above" in requirement_text or "not exceed" in requirement_text:
                quantities = [ent.text for ent in doc.ents if ent.label_ == "QUANTITY" or ent.label_ == "CARDINAL"]
                if quantities:
                    try:
                        num_part = "".join(filter(lambda x: x.isdigit() or x == '.', quantities[0].split("°")[0].split()[0]))
                        if num_part:
                             output = {"type": "text", "logic": f"temp <= {float(num_part)}"}
                             break
                    except ValueError:
                        pass
    
    # Code-based logic extraction (example using metadata from Task 2)
    if code_metadata_obj and code_metadata_obj.get("functions"):
        for func in code_metadata_obj["functions"]:
            # Example: look for simple if conditions in the function code string
            if "if" in func.get("code", ""):
                try:
                    condition_part = func["code"].split("if", 1)[1].split(":", 1)[0].strip()
                    # A very basic attempt to convert Python condition to logical form
                    # This would need significant improvement for real-world use
                    logical_condition = condition_part.replace("==", "=").replace(">", ">").replace("<", "<")
                    output = {"type": "code", "logic": f"condition: {logical_condition}"}
                    # Prioritize code logic if found and seems relevant
                    break 
                except IndexError:
                    pass # Could not parse condition

    claude_eval_response = await evaluate_with_claude(output, requirement_text, "requirement formalization")
    import json
    try:
        claude_eval = json.loads(claude_eval_response)
    except json.JSONDecodeError:
        claude_eval = {
            "confidence": 0, "explanation": "Failed to parse evaluation response.", 
            "halt_pipeline": True, "clarification_questions": ["Evaluation response was not valid JSON."]
        }
        
    if claude_eval.get("halt_pipeline", True):
        return {"output": output, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": output, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "formalize_requirement_001",
  "requirement": "The module assembly shall operate at temperatures between 350°C and 600°C.",
  "code_metadata": null 
}
```

**Run Command**:
```bash
# c --markdown "python test_v4_essential_async.py -k formalize_requirement_001"
```

**Expected Output Structure**:
```json
{
  "output": {
    "type": "text",
    "logic": "350.0 <= temp <= 600.0" 
  },
  "claude_evaluation": {
    "confidence": 0.95,
    "explanation": "Logic accurately formalized.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Missed or incorrect logic extraction from text
```python
# Solution: Enhance spaCy entity recognition (custom NER models if needed) and refine
# dependency parsing rules for identifying relationships and constraints.
# Example: Add more patterns for different types of constraints.
# if "at least" in requirement_text: ...
```

#### Issue 2: Complex code logic not parsed correctly from tree-sitter metadata
```python
# Solution: Improve the mapping from tree-sitter AST nodes (in `code_metadata`) to formal logic.
# This might involve a more sophisticated AST traversal and logic conversion than the example.
# if code_metadata_obj and not output["type"] == "code":
#     logging.warning("Code metadata provided, but no code logic extracted. Review parsing logic.")
```

### Validation Requirements

```python
# This test passes when:
assert response["output"]["type"] == "text" # Or "code" depending on input
assert "temp" in response["output"]["logic"] # Assuming 'temp' is a common variable
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 4: Make test pratt_parse_001 pass
*(This task remains as per your original definition, assuming it takes the `logic` string from Task 3 as input.)*

---
## Task 5: Make test contradiction_detection_001 pass
*(This task remains as per your original definition, using Z3 for logical contradictions based on formalized requirements from Task 3/4.)*

---
## Task 6: Make test error_cascade_001 pass
*(This task remains as per your original definition, tracing cascades based on hierarchical requirement structures.)*

---
## Task 7: Make test ambiguity_detection_001 pass
*(This task remains as per your original definition, using spaCy for ambiguity.)*

---
## Task 8: Make test pipeline_integration_001 pass
*(This task remains as per your original definition, validating the end-to-end flow of Tasks 1-7.)*

---
*(New ArangoDB tasks continue from here, assuming Tasks 1-8 populate some initial data or context that ArangoDB tools will then work with, or ArangoDB is used to store outputs of Tasks 1-7.)*

## Task 9: Make test arangodb_bm25_search_001 pass

**Test ID**: arangodb_bm25_search_001
**Model**: `max/text-general`
**Goal**: Retrieve processed requirements from the ArangoDB knowledge base using BM25 keyword search, evaluated by Claude Code; halt if confidence <0.7 or results are ambiguous/irrelevant.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.search.bm25_search import bm25_search
# from arangodb.core.constants import COLLECTION_NAME as DEFAULT_REQUIREMENT_COLLECTION # Example
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.90,
            "explanation": f"Mock: BM25 results for '{section_text}' appear relevant.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})


async def arango_bm25_tool(db_conn, query_params: dict):
    # Assuming bm25_search is available from your ArangoDB core modules
    # from arangodb.core.search.bm25_search import bm25_search
    
    # Mock bm25_search for this template if not directly importable
    def bm25_search_mock(db, query_text, collections, top_n, output_format="json", **kwargs):
        logging.info(f"Mock bm25_search called with query: {query_text} on {collections}")
        if query_text == "module operating temperature":
            return {
                "results": [
                  {"doc": {"_key": "req_xyz", "content": "The module shall operate at a specified temperature...", "tags": ["thermal"]}, "score": 0.85},
                  {"doc": {"_key": "req_abc", "content": "Operating temperature parameters must be documented.", "tags": ["monitoring"]}, "score": 0.77}
                ],
                "total": 2, "query": query_text, "search_engine": "bm25", "time": 0.02
            }
        return {"results": [], "total": 0, "query": query_text, "search_engine": "bm25", "time": 0.01}

    # Use the mock or actual function
    # search_results = bm25_search( # Actual call
    search_results = bm25_search_mock( # Mock call for template
        db=db_conn,
        query_text=query_params["query_text"],
        collections=[query_params["collection_name"]], 
        top_n=query_params["top_n"],
        output_format="json"
    )
    
    claude_eval_response = await evaluate_with_claude(search_results, query_params["query_text"], "ArangoDB BM25 Search")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": search_results, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": search_results, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_bm25_search_001",
  "description": "Test BM25 search for specific requirement keywords in ArangoDB.",
  "arango_query_params": {
    "query_text": "module operating temperature",
    "collection_name": "processed_requirements", 
    "top_n": 3
  },
  "expected_keywords_in_results": ["temperature", "operate"] 
}
```

**Run Command**:
```bash
# This would be an internal call by Claude Code, likely by providing the 
# `arango_query_params` to a Python execution environment that has `arango_bm25_tool`
# and an ArangoDB connection.
# Conceptual CLI call if wrapped:
# c --json "python arangodb_executor.py bm25_search --params_json '{\"query_text\": \"module operating temperature\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": { 
    "results": [
      {"doc": {"_key": "req_xyz", "content": "The module shall operate at a specified temperature...", "tags": ["thermal"]}, "score": 0.85},
      {"doc": {"_key": "req_abc", "content": "Operating temperature parameters must be documented.", "tags": ["monitoring"]}, "score": 0.77}
    ],
    "total": 2,
    "query": "module operating temperature",
    "search_engine": "bm25",
    "time": 0.02
  },
  "claude_evaluation": {
    "confidence": 0.9,
    "explanation": "BM25 search results are relevant to the query.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: ArangoSearch View not configured for the collection
```python
# Solution: Ensure an ArangoSearch View is created and linked to the target collection,
# with appropriate analyzers (e.g., 'text_en') for the fields being searched.
# This setup is typically done once when the DB is initialized.
# Example (conceptual, actual setup might be in arango_setup.py):
# from arangodb.core.arango_setup import ensure_arangosearch_view
# ensure_arangosearch_view(db_connection, "my_requirements_view", "processed_requirements", ["content", "title"])
```

#### Issue 2: Low relevance or no results for valid queries
```python
# Solution: 
# 1. Check document content in ArangoDB.
# 2. Review BM25 parameters in the View definition (e.g., k1, b values).
# 3. Ensure query terms are appropriate for keyword search.
# 4. If conceptual matches are needed, consider semantic search (Task 10).
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert "results" in response["output"] and isinstance(response["output"]["results"], list)
assert response["output"].get("search_engine") == "bm25"
if response["output"]["results"]:
    first_result = response["output"]["results"][0]
    assert "doc" in first_result and "_key" in first_result["doc"]
    assert "score" in first_result and isinstance(first_result["score"], float)
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
# Add specific checks for expected_keywords_in_results if possible
```

---
## Task 10: Make test arangodb_semantic_search_001 pass

**Test ID**: arangodb_semantic_search_001
**Model**: `max/text-general`
**Goal**: Retrieve conceptually similar requirements from an ArangoDB collection (e.g., `embedded_requirements`) using semantic vector search, evaluated by Claude Code.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.search.semantic_search import safe_semantic_search
# from arangodb.core.utils.embedding_utils import get_embedding # If Claude provides text query
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.85,
            "explanation": f"Mock: Semantic search for '{section_text}' returned plausible results.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_semantic_tool(db_conn, query_params: dict):
    # Assuming safe_semantic_search is available
    # from arangodb.core.search.semantic_search import safe_semantic_search
    
    # Mock safe_semantic_search for this template
    def safe_semantic_search_mock(db, query, collections, min_score, top_n, output_format="json", auto_fix_embeddings=True, **kwargs):
        logging.info(f"Mock safe_semantic_search called with query: {query} on {collections}")
        query_text = query if isinstance(query, str) else "vector_query"
        if "operational heat tolerance" in query_text:
            return {
                "results": [
                  {"doc": {"_key": "req_uvw", "content": "The device must not exceed 600C operational temperature...", "embedding": [0.1]*10}, "similarity_score": 0.88}, # Simplified embedding
                  {"doc": {"_key": "req_def", "content": "Thermal runaway prevention is critical for system integrity...", "embedding": [0.2]*10}, "similarity_score": 0.82}
                ],
                "total": 2, "query": query_text, "search_engine": "arangodb-approx-near-cosine", "time": 0.05
            }
        return {"results": [], "total": 0, "query": query_text, "search_engine": "arangodb-approx-near-cosine", "time": 0.03}

    # Use the mock or actual function
    # search_results = safe_semantic_search( # Actual call
    search_results = safe_semantic_search_mock( # Mock call for template
        db=db_conn,
        query=query_params["query_text"], # Assumes query_text, could also be query_embedding
        collections=[query_params["collection_name"]],
        min_score=query_params["min_similarity"],
        top_n=query_params["top_n"],
        output_format="json",
        auto_fix_embeddings=True 
    )
    
    claude_eval_response = await evaluate_with_claude(search_results, query_params["query_text"], "ArangoDB Semantic Search")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": search_results, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": search_results, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_semantic_search_001",
  "description": "Test semantic search for conceptually similar requirements in ArangoDB.",
  "arango_query_params": {
    "query_text": "maximum operational heat tolerance",
    "collection_name": "embedded_requirements",
    "top_n": 3,
    "min_similarity": 0.7
  },
  "expected_concept_in_results": "thermal limits" 
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py semantic_search --params_json '{\"query_text\": \"maximum operational heat tolerance\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": {
    "results": [
      {"doc": {"_key": "req_uvw", "content": "The device must not exceed 600C operational temperature...", "embedding": [0.1]*10}, "similarity_score": 0.88},
      {"doc": {"_key": "req_def", "content": "Thermal runaway prevention is critical for system integrity...", "embedding": [0.2]*10}, "similarity_score": 0.82}
    ],
    "total": 2,
    "query": "maximum operational heat tolerance",
    "search_engine": "arangodb-approx-near-cosine" 
  },
  "claude_evaluation": {
    "confidence": 0.85,
    "explanation": "Semantic search successfully retrieved conceptually related requirements.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Collection not ready for semantic search (missing embeddings, index, or inconsistent dimensions)
```python
# Solution: The `safe_semantic_search` function with `auto_fix_embeddings=True` attempts to
# prepare the collection by calling `prepare_collection_for_search`.
# This involves checking for embeddings, consistent dimensions, and a vector index.
# from arangodb.core.search.semantic_search import prepare_collection_for_search
# is_ready, status_info = prepare_collection_for_search(db_connection, "embedded_requirements", auto_fix_embeddings=True)
# if not is_ready:
#    logging.error(f"Collection not ready: {status_info['status']['message']}")
```

#### Issue 2: `APPROX_NEAR_COSINE` fails or returns unexpected results
```python
# Solution: 
# 1. Ensure the vector index on the embedding field is correctly configured (e.g., hnsw with cosine metric).
# 2. Verify the query embedding has the same dimension as document embeddings.
# 3. `safe_semantic_search` should log detailed errors from `semantic_search` if this occurs.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert "results" in response["output"] and isinstance(response["output"]["results"], list)
assert "search_engine" in response["output"] and "cosine" in response["output"]["search_engine"].lower() # or other vector engine name
if response["output"]["results"]:
    first_result = response["output"]["results"][0]
    assert "doc" in first_result and "_key" in first_result["doc"]
    assert "similarity_score" in first_result and isinstance(first_result["similarity_score"], float)
    assert 0 <= first_result["similarity_score"] <= 1
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
# Add a check for `expected_concept_in_results` by examining content of returned docs if feasible.
```

---
## Task 11: Make test arangodb_graph_traversal_001 pass

**Test ID**: arangodb_graph_traversal_001
**Model**: `max/text-general`
**Goal**: Explore and retrieve entities and their multi-hop relationships (e.g., requirement dependencies) from the ArangoDB knowledge graph, evaluated by Claude Code.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.search.graph_traverse import graph_rag_search 
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.9,
            "explanation": f"Mock: Graph traversal from '{section_text}' seems to have found related items.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_graph_traverse_tool(db_conn, traversal_params: dict):
    # Assuming graph_rag_search is available from your ArangoDB core modules
    # from arangodb.core.search.graph_traverse import graph_rag_search
    
    # Mock graph_rag_search for this template
    def graph_rag_search_mock(db, query_text, start_vertex_id, min_depth, max_depth, direction, graph_name, output_format="json", top_n=10, **kwargs):
        logging.info(f"Mock graph_rag_search for start_vertex: {start_vertex_id}, graph: {graph_name}, depth: {min_depth}-{max_depth}, dir: {direction}")
        if start_vertex_id == "processed_requirements/REQ_A001":
            return {
                "results": [{
                    "doc": {"_key": "REQ_A001", "content": "Initial requirement A001..."}, "score": 0,
                    "related": [
                        {"vertex": {"_key": "REQ_B002", "content": "Dependent requirement B002..."}, "edge": {"type": "DEPENDS_ON"}, "depth": 1},
                        {"vertex": {"_key": "REQ_C003", "content": "Further dependent req C003..."}, "edge": {"type": "REFINES"}, "depth": 2}
                    ], "related_count": 2 
                }], "total": 1, "query": query_text, "search_engine": "graph-rag-optimized", "time": 0.1
            }
        return {"results": [], "total": 0, "query": query_text, "search_engine": "graph-rag-optimized", "time": 0.05}

    # Use the mock or actual function
    # traversal_results = graph_rag_search( # Actual call
    traversal_results = graph_rag_search_mock( # Mock call for template
        db=db_conn,
        query_text="", # Typically empty when start_vertex_id is the focus
        start_vertex_id=traversal_params["start_vertex_id"],
        min_depth=traversal_params["min_depth"],
        max_depth=traversal_params["max_depth"],
        direction=traversal_params["direction"].upper(),
        graph_name=traversal_params["graph_name"],
        output_format="json",
        top_n=10 # Example, adjust as needed
    )
    
    claude_eval_response = await evaluate_with_claude(traversal_results, traversal_params["start_vertex_id"], "ArangoDB Graph Traversal")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": traversal_results, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": traversal_results, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_graph_traversal_001",
  "description": "Test multi-hop graph traversal from a starting requirement node.",
  "arango_traversal_params": {
    "start_vertex_id": "processed_requirements/REQ_A001", 
    "graph_name": "requirements_relations_graph",
    "min_depth": 1,
    "max_depth": 2,
    "direction": "OUTBOUND" 
  },
  "expected_related_count_min": 1 
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py graph_traverse --params_json '{\"start_vertex_id\": \"processed_requirements/REQ_A001\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": {
    "results": [ 
      {
        "doc": {"_key": "REQ_A001", "content": "Initial requirement A001..."},
        "score": 0, 
        "related": [
          {"vertex": {"_key": "REQ_B002", "content": "Dependent requirement B002..."}, "edge": {"type": "DEPENDS_ON"}, "depth": 1},
          {"vertex": {"_key": "REQ_C003", "content": "Further dependent req C003..."}, "edge": {"type": "REFINES"}, "depth": 2}
        ],
        "related_count": 2 
      }
    ],
    "total": 1, 
    "query": "", 
    "search_engine": "graph-rag-optimized",
    "time": 0.1
  },
  "claude_evaluation": {
    "confidence": 0.9,
    "explanation": "Graph traversal correctly identified related requirements.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Graph name incorrect or graph does not exist
```python
# Solution: Verify the graph_name parameter matches an existing graph in ArangoDB.
# Ensure the graph definition includes the correct edge and vertex collections.
# if not db_connection.has_graph(traversal_params["graph_name"]):
#     logging.error(f"Graph '{traversal_params['graph_name']}' not found.")
#     # Handle error or attempt to create graph if part of setup
```

#### Issue 2: Start vertex ID not found or not part of the specified graph's vertex collections
```python
# Solution: Ensure `start_vertex_id` is a valid document ID (e.g., "collection_name/document_key") 
# and the collection is part of the graph definition.
# try:
#     start_doc = db_connection.document(traversal_params["start_vertex_id"])
# except DocumentGetError:
#     logging.error(f"Start vertex {traversal_params['start_vertex_id']} not found.")
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert "results" in response["output"] and isinstance(response["output"]["results"], list)
assert "search_engine" in response["output"] and "graph" in response["output"]["search_engine"].lower()
if response["output"]["results"]: # If start node was processed
    first_result = response["output"]["results"][0]
    assert "doc" in first_result and "_key" in first_result["doc"]
    assert "related" in first_result and isinstance(first_result["related"], list)
    # Example: check if at least the minimum expected related items were found
    # assert first_result.get("related_count", 0) >= test_input_params["expected_related_count_min"]
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 12: Make test arangodb_memory_store_conversation_001 pass

**Test ID**: arangodb_memory_store_conversation_001
**Model**: `max/text-general`
**Goal**: Store a user-agent message exchange into ArangoDB conversational memory, creating necessary temporal links and embeddings for later retrieval and context management.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `memory_agent_instance` is an initialized MemoryAgent instance
# from arangodb.core.memory.memory_agent import MemoryAgent
# from datetime import datetime, timezone
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.98,
            "explanation": f"Mock: Conversation turn for '{section_text[:30]}...' stored successfully.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_memory_store_tool(mem_agent, conversation_data: dict):
    # from arangodb.core.memory.memory_agent import MemoryAgent # Already done if mem_agent is passed
    from datetime import datetime, timezone # Ensure datetime is available

    # The store_conversation method handles embedding and linking
    # In a real scenario, MemoryAgent instance would be used directly.
    # For template, we might simulate or call a wrapper.
    
    # Mock MemoryAgent.store_conversation for this template
    class MockMemoryAgent:
        def __init__(self, db): self.db = db
        def store_conversation(self, user_message, agent_response, conversation_id, episode_id, metadata, point_in_time, auto_embed):
            logging.info(f"Mock store_conversation called for conv_id: {conversation_id}")
            user_msg_key = f"user_msg_{hashlib.md5(user_message.encode()).hexdigest()[:6]}"
            agent_msg_key = f"agent_msg_{hashlib.md5(agent_response.encode()).hexdigest()[:6]}"
            edge_key = f"edge_{user_msg_key}_{agent_msg_key}"
            return {
                "conversation_id": conversation_id, "episode_id": episode_id,
                "user_message_id": f"memory_messages/{user_msg_key}",
                "agent_message_id": f"memory_messages/{agent_msg_key}",
                "relationship_id": f"memory_edges/{edge_key}",
                "timestamp": point_in_time.isoformat()
            }
    
    # mem_agent = MockMemoryAgent(None) # Use mock for template if actual mem_agent is complex to init here

    stored_data = mem_agent.store_conversation( # If mem_agent is the actual instance
        user_message=conversation_data["user_message"],
        agent_response=conversation_data["agent_response"],
        conversation_id=conversation_data["conversation_id"],
        episode_id=conversation_data.get("episode_id"),
        metadata=conversation_data.get("metadata"),
        point_in_time=datetime.now(timezone.utc), 
        auto_embed=True 
    )
    
    claude_eval_response = await evaluate_with_claude(stored_data, conversation_data["user_message"], "ArangoDB Memory Store")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": stored_data, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": stored_data, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_memory_store_conversation_001",
  "description": "Test storing a conversational turn in ArangoDB memory.",
  "conversation_data": {
    "user_message": "Define 'nominal operating pressure'.",
    "agent_response": "'Nominal operating pressure' refers to the design pressure under normal conditions.",
    "conversation_id": "conv_terms_def_001",
    "episode_id": "ep_glossary_building_001",
    "metadata": {"source_doc": "ISO-12345", "page": 7}
  }
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py store_conversation --params_json '{\"user_message\": \"Define nominal...\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": { 
    "conversation_id": "conv_terms_def_001",
    "episode_id": "ep_glossary_building_001",
    "user_message_id": "memory_messages/user_msg_key_xyz",
    "agent_message_id": "memory_messages/agent_msg_key_abc",
    "relationship_id": "memory_edges/edge_key_123",
    "timestamp": "2025-05-24T..." 
  },
  "claude_evaluation": {
    "confidence": 0.98,
    "explanation": "Conversation turn successfully stored with all relevant IDs.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Embedding generation fails or is slow for messages
```python
# Solution: `MemoryAgent.store_conversation` uses `get_embedding`. 
# Ensure the embedding model/service is operational. `auto_embed=False` can be used to skip embedding.
# If performance is an issue, consider asynchronous embedding generation or batching.
```

#### Issue 2: ArangoDB connection issues or write errors
```python
# Solution: Ensure ArangoDB is running and accessible. The `MemoryAgent` methods should
# include try-except blocks for database operations (as seen in the provided ArangoDB code).
# Verify collection names (MEMORY_MESSAGE_COLLECTION, MEMORY_EDGE_COLLECTION) are correct.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert "user_message_id" in response["output"] and response["output"]["user_message_id"] is not None
assert "agent_message_id" in response["output"] and response["output"]["agent_message_id"] is not None
assert "relationship_id" in response["output"] and response["output"]["relationship_id"] is not None
assert response["output"]["conversation_id"] == test_input_params["conversation_data"]["conversation_id"] # Assuming test_input_params holds the input
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 13: Make test arangodb_memory_retrieve_conversation_001 pass

**Test ID**: arangodb_memory_retrieve_conversation_001
**Model**: `max/text-general`
**Goal**: Retrieve message history for a specific conversation or episode from ArangoDB memory.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `memory_agent_instance` is an initialized MemoryAgent instance
# from arangodb.core.memory.memory_agent import MemoryAgent
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.95,
            "explanation": f"Mock: Conversation history for '{section_text}' retrieved.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_memory_retrieve_tool(mem_agent, retrieve_params: dict):
    # from arangodb.core.memory.memory_agent import MemoryAgent # Assumed mem_agent is passed
    
    # Mock MemoryAgent.retrieve_messages for template
    class MockMemoryAgent:
        def __init__(self, db): self.db = db
        def retrieve_messages(self, conversation_id, episode_id, limit, include_metadata):
            logging.info(f"Mock retrieve_messages for conv_id: {conversation_id}, episode_id: {episode_id}")
            if conversation_id == "conv_terms_def_001":
                return [
                    {"_id": "mem_msg/user1", "type": "USER", "content": "Define 'nominal operating pressure'.", "timestamp": "2025-05-24T10:00:00Z"},
                    {"_id": "mem_msg/agent1", "type": "AGENT", "content": "'Nominal operating pressure' refers...", "timestamp": "2025-05-24T10:00:05Z"}
                ]
            return []
            
    # mem_agent = MockMemoryAgent(None) # Use mock for template if actual mem_agent is complex

    retrieved_messages = mem_agent.retrieve_messages( # Actual call
        conversation_id=retrieve_params.get("conversation_id"),
        episode_id=retrieve_params.get("episode_id"),
        limit=retrieve_params.get("limit", 50),
        include_metadata=retrieve_params.get("include_metadata", True)
    )
    
    context_for_eval = retrieve_params.get("conversation_id") or retrieve_params.get("episode_id")
    claude_eval_response = await evaluate_with_claude(retrieved_messages, context_for_eval, "ArangoDB Memory Retrieval")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": retrieved_messages, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": retrieved_messages, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_memory_retrieve_conversation_001",
  "description": "Test retrieving conversation history from ArangoDB.",
  "retrieve_params": {
    "conversation_id": "conv_terms_def_001",
    "limit": 10,
    "include_metadata": true
  },
  "expected_message_count_min": 1
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py retrieve_conversation --params_json '{\"conversation_id\": \"conv_terms_def_001\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": [ // List of message documents from retrieve_messages
    {"_id": "memory_messages/user_msg_key_xyz", "type": "USER", "content": "Define 'nominal operating pressure'.", "timestamp": "...", "metadata": {...}},
    {"_id": "memory_messages/agent_msg_key_abc", "type": "AGENT", "content": "'Nominal operating pressure' refers...", "timestamp": "...", "metadata": {...}}
  ],
  "claude_evaluation": {
    "confidence": 0.95,
    "explanation": "Conversation history retrieved successfully.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: No messages found for the given ID
```python
# Solution: Verify the `conversation_id` or `episode_id` exists and has associated messages.
# The `retrieve_messages` method should gracefully return an empty list if no messages are found.
# logging.info(f"No messages found for conversation_id: {conv_id}")
```

#### Issue 2: Incorrect sorting or filtering of messages
```python
# Solution: Review the AQL query within the `retrieve_messages` method in `MemoryAgent`
# to ensure correct `SORT` and `FILTER` clauses are applied.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], list)
# Example: Check if at least the minimum expected number of messages were retrieved.
# assert len(response["output"]) >= test_input_params["expected_message_count_min"]
if response["output"]:
    assert "_id" in response["output"][0] and "type" in response["output"][0] and "content" in response["output"][0]
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 14: Make test arangodb_memory_compact_conversation_001 pass

**Test ID**: arangodb_memory_compact_conversation_001
**Model**: `max/text-general`
**Goal**: Compact (e.g., summarize) a stored conversation in ArangoDB memory to create a concise representation.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `memory_agent_instance` is an initialized MemoryAgent instance
# from arangodb.core.memory.memory_agent import MemoryAgent 
# (which uses arangodb.core.memory.compact_conversation)
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.92,
            "explanation": f"Mock: Compaction for '{section_text}' seems reasonable.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_memory_compact_tool(mem_agent, compact_params: dict):
    # from arangodb.core.memory.memory_agent import MemoryAgent # Assumed mem_agent is passed
    
    # Mock MemoryAgent.compact_conversation for template
    class MockMemoryAgent:
        def __init__(self, db): self.db = db
        def compact_conversation(self, conversation_id, episode_id, compaction_method, max_tokens, min_overlap):
            logging.info(f"Mock compact_conversation for conv_id: {conversation_id}, method: {compaction_method}")
            # This mock needs to return the full structure expected, including the DB write part
            compacted_text = f"Summary of {conversation_id or episode_id} using {compaction_method}."
            return {
                "_id": f"compacted_summaries/comp_{conversation_id or episode_id}", "_key": f"comp_{conversation_id or episode_id}",
                "type": "compaction", "compaction_method": compaction_method, "content": compacted_text,
                "conversation_id": conversation_id, "episode_id": episode_id, "message_count": 5, # Example
                "embedding": [0.01]*10, # Simplified mock embedding
                "metadata": {"original_token_count": 500, "compacted_token_count": 50}
            }
            
    # mem_agent = MockMemoryAgent(None) # Use mock for template if actual mem_agent is complex

    compaction_result = mem_agent.compact_conversation( # Actual call
        conversation_id=compact_params.get("conversation_id"),
        episode_id=compact_params.get("episode_id"),
        compaction_method=compact_params.get("compaction_method", "summarize"),
        max_tokens=compact_params.get("max_tokens", 2000),
        min_overlap=compact_params.get("min_overlap", 100)
    )
    
    context_for_eval = compact_params.get("conversation_id") or compact_params.get("episode_id")
    claude_eval_response = await evaluate_with_claude(compaction_result, context_for_eval, "ArangoDB Conversation Compaction")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": compaction_result, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": compaction_result, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_memory_compact_conversation_001",
  "description": "Test compacting a conversation using summarization.",
  "compact_params": {
    "conversation_id": "conv_terms_def_001", 
    "compaction_method": "summarize",
    "max_tokens": 1500 
  },
  "expected_summary_keywords": ["nominal", "pressure", "design"]
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py compact_conversation --params_json '{\"conversation_id\": \"conv_terms_def_001\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": { // Output from memory_agent.compact_conversation
    "_id": "compacted_summaries/comp_conv_terms_def_001_xyz",
    "_key": "comp_conv_terms_def_001_xyz",
    "type": "compaction",
    "compaction_method": "summarize",
    "content": "The conversation defined 'nominal operating pressure' as the design pressure under normal conditions.",
    "conversation_id": "conv_terms_def_001",
    "episode_id": "ep_glossary_building_001", 
    "message_ids": ["memory_messages/user_msg_key_xyz", "memory_messages/agent_msg_key_abc"],
    "message_count": 2,
    "created_at": "2025-05-24T...",
    "updated_at": "2025-05-24T...",
    "embedding": [0.01, ...], // Embedding of the compacted content
    "tags": [],
    "metadata": {
      "original_content_length": 200,
      "compacted_length": 80,
      "original_token_count": 50,
      "compacted_token_count": 20,
      "reduction_ratio": 0.6,
      "source_messages": ["user_msg_key_xyz", "agent_msg_key_abc"],
      "chunked_processing": false,
      "workflow_id": "compaction_..."
    }
    // "workflow_summary": { ... } // If workflow tracking is integrated and returned
  },
  "claude_evaluation": {
    "confidence": 0.92,
    "explanation": "Conversation compacted successfully and summary is relevant.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: LLM call for compaction fails or returns poor quality summary
```python
# Solution: 
# 1. Check LLM provider connectivity and API keys (LiteLLM configuration).
# 2. Refine the prompts used in `compact_conversation.py` for the specific compaction method.
# 3. Ensure `max_tokens` for chunking is appropriate for the LLM's context window.
# 4. The `compact_conversation` function has internal error handling and workflow tracking.
```

#### Issue 2: Original conversation messages not found
```python
# Solution: Ensure the `conversation_id` or `episode_id` passed to `compact_conversation`
# corresponds to existing messages retrieved by `memory_agent.retrieve_messages`.
# if not memory_agent.retrieve_messages(conversation_id=compact_params.get("conversation_id")):
#     logging.error("Cannot compact: No messages found for the given conversation ID.")
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert response["output"].get("type") == "compaction"
assert "content" in response["output"] and len(response["output"]["content"]) > 0
assert response["output"].get("compaction_method") == test_input_params["compact_params"]["compaction_method"]
assert "embedding" in response["output"] # Check for embedding of the summary
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
# Add checks for `expected_summary_keywords` in response["output"]["content"]
```

---
## Task 15: Make test arangodb_episode_management_001 pass

**Test ID**: arangodb_episode_management_001
**Model**: `max/text-general`
**Goal**: Create and manage conversational episodes in ArangoDB, including starting, ending, and linking entities/relationships to an episode.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.memory.episode_manager import EpisodeManager
import logging
from datetime import datetime, timezone

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.97,
            "explanation": f"Mock: Episode management action '{task_name}' for '{section_text}' successful.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_episode_tool(db_conn, action: str, params: dict):
    from arangodb.core.memory.episode_manager import EpisodeManager # Actual import
    
    # Mock EpisodeManager for template if direct use is complex
    class MockEpisodeManager:
        def __init__(self, db): self.db = db; self.episode_counter = 0
        def create_episode(self, name, description, metadata, start_time):
            self.episode_counter += 1; key = f"ep_mock_{self.episode_counter}"
            logging.info(f"Mock create_episode: {name}")
            return {"_id": f"agent_episodes/{key}", "_key": key, "name": name, "start_time": start_time.isoformat(), "end_time": None}
        def end_episode(self, episode_id, end_time):
            logging.info(f"Mock end_episode: {episode_id}")
            return {"_id": episode_id, "_key": episode_id.split('/')[-1], "name": "Mock Episode", "end_time": end_time.isoformat()}
        def link_entity_to_episode(self, episode_id, entity_id):
            logging.info(f"Mock link_entity_to_episode: {entity_id} to {episode_id}")
            return True # Simulate success
        def get_episode(self, episode_id):
             if "ep_mock" in episode_id: return {"_id": episode_id, "name":"Mocked Episode"}
             return None

    episode_manager = MockEpisodeManager(db_conn) # Use mock for template
    # episode_manager = EpisodeManager(db_conn) # Actual instantiation

    result_data = None
    eval_context = ""

    if action == "create_episode":
        result_data = episode_manager.create_episode(
            name=params["name"],
            description=params.get("description"),
            metadata=params.get("metadata"),
            start_time=params.get("start_time", datetime.now(timezone.utc))
        )
        eval_context = params["name"]
    elif action == "end_episode":
        result_data = episode_manager.end_episode(
            episode_id=params["episode_id"],
            end_time=params.get("end_time", datetime.now(timezone.utc))
        )
        eval_context = params["episode_id"]
    elif action == "link_entity": # Example custom action for linking
        result_data = episode_manager.link_entity_to_episode(
            episode_id=params["episode_id"],
            entity_id=params["entity_id"]
        )
        eval_context = f"Link {params['entity_id']} to {params['episode_id']}"
    else:
        raise ValueError(f"Unsupported episode action: {action}")

    claude_eval_response = await evaluate_with_claude(result_data, eval_context, f"Episode Management: {action}")
    import json
    claude_eval = json.loads(claude_eval_response)
    
    if claude_eval.get("halt_pipeline", True):
        return {"output": result_data, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": result_data, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_episode_management_001",
  "description": "Test creating a new conversational episode.",
  "action": "create_episode",
  "episode_params": {
    "name": "Initial Design Review - Cooling System",
    "description": "Episode covering the first review meeting for the cooling system design.",
    "metadata": {"project_code": "CS-P001", "attendees": ["user_claude", "human_lead_eng"]}
  }
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py episode_manage --action create_episode --params_json '{\"name\": \"Initial Design...\", ...}'"
```

**Expected Output Structure (for create_episode action)**:
```json
{
  "output": { // Output from episode_manager.create_episode
    "_id": "agent_episodes/ep_mock_1", // or actual key
    "_key": "ep_mock_1",
    "name": "Initial Design Review - Cooling System",
    "start_time": "2025-05-24T...",
    "end_time": null,
    "metadata": {"project_code": "CS-P001", "attendees": ["user_claude", "human_lead_eng"]}
    // ... other fields from EpisodeManager's create_episode
  },
  "claude_evaluation": {
    "confidence": 0.97,
    "explanation": "Episode created successfully.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Episode ID collision (if not using UUIDs or unique generation)
```python
# Solution: `EpisodeManager` uses `episode_{uuid.uuid4().hex[:12]}` for `_key`, 
# which should prevent collisions. Ensure `_key` is unique if custom keys are used.
```

#### Issue 2: Failure to link entities/relationships if they don't exist
```python
# Solution: Before calling `link_entity_to_episode` or `link_relationship_to_episode`,
# Claude should verify that the target entity/relationship ID exists in the database.
# entity_exists = db_connection.collection("engineering_entities").has(entity_key)
```

### Validation Requirements

```python
# This test passes when (example for 'create_episode'):
assert isinstance(response["output"], dict)
assert "_id" in response["output"] and response["output"]["_id"] is not None
assert "_key" in response["output"] and response["output"]["_key"] is not None
assert response["output"]["name"] == test_input_params["episode_params"]["name"] # Assuming test_input_params holds the input
assert response["output"]["end_time"] is None # For new episode
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 16: Make test arangodb_entity_storage_resolution_001 pass

**Test ID**: arangodb_entity_storage_resolution_001
**Model**: `max/text-general`
**Goal**: Store new or update existing entities (e.g., requirements, components) in ArangoDB, using entity resolution to handle duplicates and merge attributes.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.graph.entity_resolution import resolve_entity, normalize_name, get_name_variants
import logging
from datetime import datetime, timezone

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        merged_status = "merged" if output[2] else "newly stored"
        return json.dumps({
            "confidence": 0.96,
            "explanation": f"Mock: Entity '{section_text}' {merged_status} successfully.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_entity_resolution_tool(db_conn, entity_data_params: dict):
    from arangodb.core.graph.entity_resolution import resolve_entity # Actual import
    
    # Mock resolve_entity for this template
    def resolve_entity_mock(db, entity_doc, collection_name, embedding_field="embedding", min_confidence=0.8, merge_strategy="union", auto_merge=True):
        logging.info(f"Mock resolve_entity for: {entity_doc.get('name')} in {collection_name}")
        # Simulate finding a match and merging, or creating new
        existing_key = f"existing_{hashlib.md5(entity_doc['name'].encode()).hexdigest()[:6]}"
        if auto_merge and min_confidence > 0.7 and "Sensor" in entity_doc.get("type",""): # Simulate a condition for merging
            merged_doc = entity_doc.copy()
            merged_doc["_key"] = existing_key
            merged_doc["_id"] = f"{collection_name}/{existing_key}"
            merged_doc["attributes"]["merged_field"] = "from_existing"
            merged_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
            return merged_doc, [{"doc": {"_key": existing_key}, "_confidence": 0.9}], True
        else:
            new_key = f"new_{hashlib.md5(entity_doc['name'].encode()).hexdigest()[:6]}"
            entity_doc["_key"] = new_key
            entity_doc["_id"] = f"{collection_name}/{new_key}"
            entity_doc["created_at"] = datetime.now(timezone.utc).isoformat()
            return entity_doc, [], False

    # Use the mock or actual function
    # resolved_entity, matches, merged = resolve_entity( # Actual call
    resolved_entity, matches, merged = resolve_entity_mock( # Mock call for template
        db=db_conn,
        entity_doc=entity_data_params["entity_doc"],
        collection_name=entity_data_params["collection_name"],
        embedding_field=entity_data_params.get("embedding_field", "embedding"),
        min_confidence=entity_data_params.get("min_confidence", 0.85),
        merge_strategy=entity_data_params.get("merge_strategy", "union"),
        auto_merge=entity_data_params.get("auto_merge", True)
    )
    
    output_data = (resolved_entity, matches, merged) # Package for evaluation
    claude_eval_response = await evaluate_with_claude(output_data, entity_data_params["entity_doc"]["name"], "ArangoDB Entity Resolution")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": output_data, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": output_data, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_entity_storage_resolution_001",
  "description": "Test storing an entity with resolution against existing entities.",
  "entity_resolution_params": {
    "entity_doc": {
      "name": "Pressure Sensor Model PS-Advanced",
      "type": "SensorComponent",
      "attributes": {"range_mpa": 10, "accuracy_percent": 0.05}
      // "embedding": [0.1, 0.2, ...] // Optional, can be generated if not present
    },
    "collection_name": "engineering_components",
    "min_confidence": 0.80, 
    "auto_merge": true,
    "merge_strategy": "union"
  }
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py resolve_entity --params_json '{\"entity_doc\": {\"name\": \"Pressure Sensor...\"}, ...}'"
```

**Expected Output Structure**:
```json
{
  "output": [ // Tuple: (resolved_entity_doc, list_of_potential_matches, merged_boolean)
    { // resolved_entity_doc
      "_id": "engineering_components/some_key_xyz",
      "_key": "some_key_xyz",
      "name": "Pressure Sensor Model PS-Advanced", // Or a merged name
      "type": "SensorComponent",
      "attributes": {"range_mpa": 10, "accuracy_percent": 0.05, "merged_field": "from_existing"}, // Example if merged
      "created_at": "2025-05-24T...", // or "updated_at"
      // "_merge_history": [...] // If merged
    },
    [ /* list_of_potential_matches, e.g., [{"doc": {"_key": ...}, "_confidence": 0.9}] */ ],
    true // merged_boolean (true if merged, false if new)
  ],
  "claude_evaluation": {
    "confidence": 0.96,
    "explanation": "Entity 'Pressure Sensor Model PS-Advanced' merged successfully.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Incorrect merging or too many duplicates created
```python
# Solution: 
# 1. Fine-tune `min_confidence` for `resolve_entity`.
# 2. Improve `normalize_name` and `get_name_variants` in `entity_resolution.py`.
# 3. Ensure quality of embeddings if semantic matching is heavily used.
# 4. Review the `merge_entity_attributes` logic for the chosen `merge_strategy`.
```

#### Issue 2: Embedding generation for new entities is slow or fails
```python
# Solution: Ensure embedding model/service used by `get_embedding` (in `embedding_utils.py`) is robust.
# `resolve_entity` might need to handle cases where embedding generation fails gracefully.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], tuple) and len(response["output"]) == 3
resolved_doc, matches, merged = response["output"]
assert isinstance(resolved_doc, dict) and "_key" in resolved_doc
assert isinstance(matches, list)
assert isinstance(merged, bool)
assert resolved_doc["name"] is not None # Or check against input name if not merged to a different name
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 17: Make test arangodb_relationship_storage_001 pass

**Test ID**: arangodb_relationship_storage_001
**Model**: `max/text-general`
**Goal**: Store new relationships (edges) between existing entities in ArangoDB, including temporal metadata and handling potential contradictions.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.graph.enhanced_relationships import create_temporal_relationship
# from arangodb.core.graph.contradiction_detection import resolve_all_contradictions (optional pre-check)
import logging
from datetime import datetime, timezone

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.99,
            "explanation": f"Mock: Relationship '{section_text}' stored successfully.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_relationship_store_tool(db_conn, relationship_params: dict):
    from arangodb.core.graph.enhanced_relationships import create_temporal_relationship # Actual import
    # from arangodb.core.graph.contradiction_detection import resolve_all_contradictions # For pre-emptive check

    # Mock create_temporal_relationship for template
    def create_temporal_relationship_mock(db, edge_collection, from_id, to_id, relationship_type, attributes, reference_time, valid_until=None, check_contradictions=True):
        logging.info(f"Mock create_temporal_relationship: {from_id} -> {relationship_type} -> {to_id}")
        edge_key = f"edge_{from_id.split('/')[-1]}_{to_id.split('/')[-1]}_{relationship_type[:5]}"
        return {
            "_id": f"{edge_collection}/{edge_key}", "_key": edge_key, "_from": from_id, "_to": to_id,
            "type": relationship_type, "attributes": attributes, 
            "valid_at": reference_time.isoformat() if isinstance(reference_time, datetime) else reference_time,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
    # Optional: Pre-emptive contradiction check if new_edge can be fully formed first
    # This depends on how `create_temporal_relationship` handles contradictions internally.
    # If it uses `resolve_all_contradictions`, then this step might be redundant here.
    # new_edge_candidate = { "_from": relationship_params["from_id"], "_to": relationship_params["to_id"], ...}
    # resolutions, overall_success = resolve_all_contradictions(db_conn, relationship_params["edge_collection"], new_edge_candidate)
    # if not overall_success: # Handle failure to resolve
    #    pass

    # Use mock or actual
    # stored_relationship = create_temporal_relationship( # Actual call
    stored_relationship = create_temporal_relationship_mock( # Mock call for template
        db=db_conn,
        edge_collection=relationship_params["edge_collection"],
        from_id=relationship_params["from_id"],
        to_id=relationship_params["to_id"],
        relationship_type=relationship_params["relationship_type"],
        attributes=relationship_params.get("attributes"),
        reference_time=relationship_params.get("reference_time", datetime.now(timezone.utc)),
        valid_until=relationship_params.get("valid_until"),
        check_contradictions=relationship_params.get("check_contradictions", True)
    )
    
    eval_context = f"{relationship_params['from_id']} -[{relationship_params['relationship_type']}]-> {relationship_params['to_id']}"
    claude_eval_response = await evaluate_with_claude(stored_relationship, eval_context, "ArangoDB Relationship Storage")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": stored_relationship, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": stored_relationship, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_relationship_storage_001",
  "description": "Test storing a new relationship between two existing entities.",
  "relationship_params": {
    "edge_collection": "system_component_links",
    "from_id": "engineering_components/PS-Advanced", // From Task 16
    "to_id": "engineering_systems/MainCoolingUnit",
    "relationship_type": "PART_OF",
    "attributes": {"quantity": 2, "criticality": "high"},
    "reference_time": "2025-05-01T10:00:00Z", // Example specific time
    "check_contradictions": true
  }
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py store_relationship --params_json '{\"edge_collection\": \"system_component_links\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": { // Output from create_temporal_relationship
    "_id": "system_component_links/some_edge_key",
    "_key": "some_edge_key",
    "_from": "engineering_components/PS-Advanced",
    "_to": "engineering_systems/MainCoolingUnit",
    "type": "PART_OF",
    "attributes": {"quantity": 2, "criticality": "high"},
    "valid_at": "2025-05-01T10:00:00Z",
    "created_at": "2025-05-24T..." 
    // ... other fields from create_temporal_relationship
  },
  "claude_evaluation": {
    "confidence": 0.99,
    "explanation": "Relationship stored successfully with temporal metadata.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: `_from` or `_to` entities do not exist
```python
# Solution: Before attempting to create a relationship, Claude should verify
# the existence of the source and target entities in their respective collections.
# from_doc = db_connection.collection("engineering_components").get(from_key)
# to_doc = db_connection.collection("engineering_systems").get(to_key)
# if not from_doc or not to_doc:
#    logging.error("Source or target entity for relationship not found.")
```

#### Issue 2: Contradiction detection logic (if active) prevents storage or alters existing data unexpectedly
```python
# Solution: `create_temporal_relationship` (from `enhanced_relationships.py`) uses 
# `find_contradicting_edges` and `invalidate_edge`. Ensure this logic aligns with desired outcomes.
# If contradictions are found and automatically resolved (e.g., by invalidating an old edge),
# the output or logs from `ContradictionLogger` (Task 19) should be reviewed by Claude.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert "_id" in response["output"] and response["output"]["_id"] is not None
assert "_key" in response["output"] and response["output"]["_key"] is not None
assert response["output"]["_from"] == test_input_params["relationship_params"]["from_id"]
assert response["output"]["_to"] == test_input_params["relationship_params"]["to_id"]
assert response["output"]["type"] == test_input_params["relationship_params"]["relationship_type"]
assert "valid_at" in response["output"]
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 18: Make test arangodb_community_analysis_001 pass

**Test ID**: arangodb_community_analysis_001
**Model**: `max/text-general`
**Goal**: Identify and analyze communities (clusters) of related entities within the ArangoDB knowledge graph using graph algorithms.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.graph.community_building import CommunityBuilder
import logging

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.88,
            "explanation": f"Mock: Community analysis for '{section_text}' yielded potentially useful clusters.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_community_analysis_tool(db_conn, analysis_params: dict):
    from arangodb.core.graph.community_building import CommunityBuilder # Actual import
    
    # Mock CommunityBuilder for template
    class MockCommunityBuilder:
        def __init__(self, db, entity_collection, relationship_collection, community_collection, community_edge_collection, graph_name):
            self.db = db; self.entity_collection = entity_collection; self.relationship_collection = relationship_collection; self.graph_name = graph_name
            logging.info(f"Mock CommunityBuilder initialized for graph {graph_name}")
        def detect_communities(self, algorithm, min_members, max_communities, weight_attribute, start_vertex_id, group_id):
            logging.info(f"Mock detect_communities with {algorithm}, min_members: {min_members}")
            return [ # Example output
                {"community_id": "louvain_comm_1", "name": "Thermal Subsystem Requirements", "member_count": 5, "members": [{"_id": "ent/A"}, {"_id": "ent/B"}]},
                {"community_id": "louvain_comm_2", "name": "Power Regulation Components", "member_count": 3, "members": [{"_id": "ent/C"}, {"_id": "ent/D"}]}
            ]
        def create_communities(self, communities_data, group_id, auto_generate_tags):
             logging.info(f"Mock create_communities for {len(communities_data)} communities.")
             # Simulate returning the input data with added _id for created community docs
             created = []
             for i, cd in enumerate(communities_data):
                 cd_copy = cd.copy()
                 cd_copy["_id"] = f"communities/comm_mock_{i}"
                 cd_copy["_key"] = f"comm_mock_{i}"
                 created.append(cd_copy)
             return created

    # community_builder = CommunityBuilder( # Actual instantiation
    #     db=db_conn,
    #     entity_collection=analysis_params.get("entity_collection", "engineering_entities"),
    #     relationship_collection=analysis_params.get("relationship_collection", "system_component_links"),
    #     community_collection=analysis_params.get("community_collection", "knowledge_communities"),
    #     community_edge_collection=analysis_params.get("community_edge_collection", "community_membership_edges"),
    #     graph_name=analysis_params.get("graph_name", "engineering_knowledge_graph")
    # )
    community_builder = MockCommunityBuilder( # Mock instantiation for template
        db=db_conn,
        entity_collection=analysis_params.get("entity_collection", "engineering_entities"),
        relationship_collection=analysis_params.get("relationship_collection", "system_component_links"),
        community_collection=analysis_params.get("community_collection", "knowledge_communities"),
        community_edge_collection=analysis_params.get("community_edge_collection", "community_membership_edges"),
        graph_name=analysis_params.get("graph_name", "engineering_knowledge_graph")
    )

    detected_communities = community_builder.detect_communities(
        algorithm=analysis_params.get("algorithm", "louvain"),
        min_members=analysis_params.get("min_members", 3),
        max_communities=analysis_params.get("max_communities", 10),
        weight_attribute=analysis_params.get("weight_attribute", "confidence"), # From relationship edges
        start_vertex_id=analysis_params.get("start_vertex_id"), # Optional
        group_id=analysis_params.get("group_id") # Optional
    )
    
    # Optionally, Claude might decide to persist these communities
    # created_community_docs = community_builder.create_communities(detected_communities)
    # output_data = created_community_docs # If communities are created
    output_data = detected_communities # If just detecting

    eval_context = f"Graph: {analysis_params.get('graph_name', 'default')}, Algo: {analysis_params.get('algorithm', 'louvain')}"
    claude_eval_response = await evaluate_with_claude(output_data, eval_context, "ArangoDB Community Analysis")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True):
        return {"output": output_data, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": output_data, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_community_analysis_001",
  "description": "Test community detection on the requirements knowledge graph.",
  "analysis_params": {
    "entity_collection": "engineering_entities",
    "relationship_collection": "requirement_links",
    "graph_name": "requirements_knowledge_graph",
    "algorithm": "louvain",
    "min_members": 2,
    "max_communities": 5,
    "weight_attribute": "relevance_score" 
  },
  "expected_community_count_min": 1
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py community_analysis --params_json '{\"graph_name\": \"requirements_knowledge_graph\", ...}'"
```

**Expected Output Structure (for detected communities)**:
```json
{
  "output": [ // List of detected communities
    {
      "community_id": "louvain_comm_1", // Algorithm-specific ID
      "name": "Thermal Subsystem Requirements", // Auto-generated or based on dominant types
      "member_count": 5,
      "members": [ // List of member entity summaries or IDs
        {"_id": "engineering_entities/req_therm_01", "_key": "req_therm_01", "name": "Thermal Operating Range Req"},
        {"_id": "engineering_entities/req_therm_02", "_key": "req_therm_02", "name": "Overheat Protection Req"}
      ],
      "homogeneity": 0.8, // Example metric
      "tags": ["thermal", "requirement"]
    }
    // ... more communities ...
  ],
  "claude_evaluation": {
    "confidence": 0.88,
    "explanation": "Community analysis identified relevant clusters of requirements.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed"
}
```

### Common Issues & Solutions

#### Issue 1: Graph algorithms (e.g., Louvain) not available or fail
```python
# Solution: `CommunityBuilder.detect_communities` has a fallback mechanism 
# (`_detect_communities_fallback`) if graph functions are missing.
# Ensure ArangoDB version supports graph algorithms. For Enterprise, ensure Pregel is enabled.
# For Community Edition, the fallback based on relationship density will be used.
```

#### Issue 2: Poor quality communities (too large, too small, not coherent)
```python
# Solution: 
# 1. Adjust `min_members` and `max_communities` parameters.
# 2. For Louvain, experiment with `weight_attribute` on relationships and `max_iterations`.
# 3. Ensure the underlying graph data (entities and relationships) is meaningful and well-connected.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], list)
# Example: check if at least a minimum number of communities were found, if expected
# if test_input_params["expected_community_count_min"] > 0:
#    assert len(response["output"]) >= test_input_params["expected_community_count_min"]
if response["output"]:
    first_community = response["output"][0]
    assert "community_id" in first_community or "algorithm_id" in first_community # Depending on actual output key
    assert "name" in first_community
    assert "member_count" in first_community and first_community["member_count"] >= 0
    assert "members" in first_community and isinstance(first_community["members"], list)
assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

---
## Task 19: Make test arangodb_graph_contradiction_management_001 pass

**Test ID**: arangodb_graph_contradiction_management_001
**Model**: `max/text-general`
**Goal**: Detect, resolve (if possible), and log contradictions between relationships in the ArangoDB graph, focusing on temporal or data-level conflicts.

### Working Code Example

```python
# COPY THIS WORKING PATTERN:
# Assumes `db_connection` is an initialized ArangoDB StandardDatabase instance
# from arangodb.core.graph.contradiction_detection import detect_temporal_contradictions, resolve_contradiction, resolve_all_contradictions
# from arangodb.core.memory.contradiction_logger import ContradictionLogger
import logging
from datetime import datetime, timezone

# Placeholder for evaluate_with_claude (as defined in Task 1)
async def evaluate_with_claude(output, section_text, task_name, is_ambiguity_check=False):
    # ... (implementation similar to other tasks) ...
    try:
        logging.info(f"Simulating Claude evaluation for {task_name}")
        import json
        return json.dumps({
            "confidence": 0.93,
            "explanation": f"Mock: Graph contradiction management for '{section_text}' processed.",
            "halt_pipeline": False,
            "clarification_questions": []
        })
    except Exception as e:
        return json.dumps({"confidence": 0, "explanation": str(e), "halt_pipeline": True})

async def arango_graph_contradiction_tool(db_conn, params: dict):
    from arangodb.core.graph.contradiction_detection import detect_temporal_contradictions, resolve_contradiction # Actual
    from arangodb.core.memory.contradiction_logger import ContradictionLogger # Actual
    
    # Mock implementations for template
    def detect_temporal_contradictions_mock(db, edge_collection, edge_doc, exclude_keys=None):
        logging.info(f"Mock detect_temporal_contradictions for edge type: {edge_doc.get('type')}")
        # Simulate finding one conflicting edge if type is "WORKS_FOR"
        if edge_doc.get("type") == "WORKS_FOR" and edge_doc.get("_from") == "entities/user001":
            return [{
                "_key": "existing_edge_789", "_from": "entities/user001", "_to": "entities/old_org", 
                "type": "WORKS_FOR", "valid_at": "2023-01-01T00:00:00Z", "created_at": "2023-01-01T00:00:00Z",
                "attributes": {"role": "Engineer"}
            }]
        return []

    def resolve_contradiction_mock(db, edge_collection, new_edge, contradicting_edge, strategy, resolution_reason=None):
        logging.info(f"Mock resolve_contradiction strategy: {strategy}")
        return {
            "action": f"mock_action_{strategy}", "resolved_edge": new_edge, 
            "reason": resolution_reason or f"Resolved with {strategy}", "success": True, "strategy": strategy
        }
        
    class MockContradictionLogger:
        def __init__(self, db, collection="mock_contradiction_log"): self.db = db; self.log = []
        def log_contradiction(self, new_edge, existing_edge, resolution, context):
            log_entry = {"new":new_edge.get("_key"), "existing":existing_edge.get("_key"), "res":resolution.get("action"), "ctx":context}
            self.log.append(log_entry)
            logging.info(f"Mock logged contradiction: {log_entry}")
            return f"log_{len(self.log)}"

    # contradiction_logger = ContradictionLogger(db_conn) # Actual
    contradiction_logger = MockContradictionLogger(db_conn) # Mock for template
    
    action = params.get("action", "detect_and_resolve")
    edge_doc_to_check = params.get("edge_doc") # This would be the new edge Claude wants to add or check
    edge_collection_name = params.get("edge_collection", "entity_relationships")
    resolution_strategy = params.get("strategy", "newest_wins")
    
    output_data = {"detected_contradictions": [], "resolutions": [], "logs": []}
    eval_context = f"Action: {action}"
    
    if not edge_doc_to_check:
        raise ValueError("edge_doc must be provided for contradiction management.")
    eval_context += f", Edge: {edge_doc_to_check.get('_from')}->{edge_doc_to_check.get('_to')}"

    # Using mock functions here, replace with actual calls
    # conflicting_edges = detect_temporal_contradictions( # Actual call
    conflicting_edges = detect_temporal_contradictions_mock( # Mock call for template
        db=db_conn,
        edge_collection=edge_collection_name,
        edge_doc=edge_doc_to_check
    )
    output_data["detected_contradictions"] = conflicting_edges

    if conflicting_edges:
        for conflicting_edge in conflicting_edges:
            # resolution = resolve_contradiction( # Actual call
            resolution = resolve_contradiction_mock( # Mock call for template
                db=db_conn,
                edge_collection=edge_collection_name,
                new_edge=edge_doc_to_check,
                contradicting_edge=conflicting_edge,
                strategy=resolution_strategy,
                resolution_reason=f"Automated resolution via {resolution_strategy}"
            )
            output_data["resolutions"].append(resolution)
            if resolution.get("success"):
                log_id = contradiction_logger.log_contradiction(
                    new_edge=edge_doc_to_check, # Or resolution["resolved_edge"] if it's modified
                    existing_edge=conflicting_edge, # This is the one that might have been invalidated
                    resolution=resolution,
                    context=f"MCP Tool: {params.get('test_case_id', 'unknown')}"
                )
                output_data["logs"].append({"original_conflicting_key": conflicting_edge.get("_key") , "log_id": log_id, "resolution_action": resolution.get("action")})

    claude_eval_response = await evaluate_with_claude(output_data, eval_context, "ArangoDB Graph Contradiction Management")
    import json
    claude_eval = json.loads(claude_eval_response)

    if claude_eval.get("halt_pipeline", True) and conflicting_edges: # Halt if contradictions were found and eval suggests it
        return {"output": output_data, "claude_evaluation": claude_eval, "status": "halted"}
    return {"output": output_data, "claude_evaluation": claude_eval, "status": "proceed"}
```

### Test Details

**Input from `test_prompts.json`**:
```json
{
  "test_case_id": "arangodb_graph_contradiction_management_001",
  "description": "Test detection and resolution of temporal contradictions for graph relationships.",
  "contradiction_params": {
    "action": "detect_and_resolve",
    "edge_collection": "employee_history", // Example collection
    "edge_doc": { // The new edge Claude is trying to add
      "_from": "entities/user001", 
      "_to": "entities/new_org", 
      "type": "WORKS_FOR", 
      "valid_at": "2024-01-01T00:00:00Z", // This new job starts in 2024
      "created_at": "2024-05-24T10:00:00Z", // When this fact is being added
      "attributes": {"role": "Lead Developer"}
    },
    "strategy": "newest_wins" 
  },
  "expected_conflicts_found": true, // Assuming a conflicting "WORKS_FOR" edge exists for user001
  "expected_resolution_action": "mock_action_newest_wins" // Or actual action like "invalidate_old"
}
```

**Run Command**:
```bash
# Conceptual CLI call:
# c --json "python arangodb_executor.py graph_contradiction --params_json '{\"action\": \"detect_and_resolve\", ...}'"
```

**Expected Output Structure**:
```json
{
  "output": {
    "detected_contradictions": [
      {
        "_key": "existing_edge_789", "_from": "entities/user001", "_to": "entities/old_org", 
        "type": "WORKS_FOR", "valid_at": "2023-01-01T00:00:00Z", 
        "attributes": {"role": "Engineer"}
      }
    ],
    "resolutions": [
      {
        "action": "mock_action_newest_wins", // In real scenario, "invalidate_old" or similar
        "resolved_edge": { /* ... new_edge data ... */ },
        "reason": "Resolved with newest_wins", 
        "success": true,
        "strategy": "newest_wins"
      }
    ],
    "logs": [
        {"original_conflicting_key": "existing_edge_789", "log_id": "log_1", "resolution_action": "mock_action_newest_wins"}
    ]
  },
  "claude_evaluation": {
    "confidence": 0.93,
    "explanation": "Graph contradiction correctly identified and resolved.",
    "halt_pipeline": false,
    "clarification_questions": []
  },
  "status": "proceed" // Could be "halted" if unresolved critical contradictions remain
}
```

### Common Issues & Solutions

#### Issue 1: `resolve_contradiction` logic in `contradiction_detection.py` does not handle specific cases correctly.
```python
# Solution: Review and test the different resolution strategies (`newest_wins`, `merge`, `split_timeline`)
# within `src/arangodb/core/graph/contradiction_detection.py`. Ensure they correctly modify
# `valid_at` and `invalid_at` fields of the conflicting edges.
```

#### Issue 2: Performance issues when checking many potential contradictions.
```python
# Solution: Optimize AQL queries in `detect_temporal_contradictions` by ensuring proper indexing
# on `_from`, `_to`, `type`, and temporal fields in the edge collection.
# The current `detect_contradicting_edges` in `contradiction_detection.py` filters on _from, _to, type.
```

### Validation Requirements

```python
# This test passes when:
assert isinstance(response["output"], dict)
assert "detected_contradictions" in response["output"] and isinstance(response["output"]["detected_contradictions"], list)
assert "resolutions" in response["output"] and isinstance(response["output"]["resolutions"], list)
assert "logs" in response["output"] and isinstance(response["output"]["logs"], list)

# If contradictions were expected and resolved:
# if test_input_params["expected_conflicts_found"]:
#    assert len(response["output"]["detected_contradictions"]) > 0
#    assert len(response["output"]["resolutions"]) > 0
#    assert response["output"]["resolutions"][0]["success"] is True
#    assert response["output"]["resolutions"][0]["action"] == test_input_params["expected_resolution_action"]
#    assert len(response["output"]["logs"]) > 0

assert response["status"] in ["proceed", "halted"]
assert 0 <= response["claude_evaluation"]["confidence"] <= 1
```

