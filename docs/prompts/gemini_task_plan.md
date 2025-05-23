# Gemini Task Plan Generation

## CORE Goal

Create a comprehensive, actionable task plan for implementing new features in our LiteLLM-based project by leveraging collaborative research between Claude (primary agent), human expertise, Ask-Perplexity (research tool), and Gemini (task plan specialist). The process should maximize the strengths of each participant to produce high-quality, implementation-ready task plans that follow our strict NO MOCKING requirement.

## Setup and Analysis
1. Change directory to project root
2. Activate virtual environment
3. Set PYTHONPATH from project's .env file
4. **Repository Research** (adapt based on feature):
   - Create `@repos` directory if needed
   - Clone relevant repositories for the specific feature
   - Examples for CLI/LLM features:
     - https://github.com/simonw/llm-gemini.git
     - https://github.com/simonw/files-to-prompt.git
     - https://github.com/simonw/llm.git
   - For other features, ask human for relevant repos
5. **Repository Analysis**:
   - Analyze cloned repositories for patterns relevant to the feature
   - Focus on architecture, plugin systems, CLI design, etc.
   - Document key findings for research enrichment
6. **Project Integration Analysis**:
   - Review our project's architecture (`@src/llm_call/core/`)
   - Identify where new features will integrate
   - Check for existing patterns to follow
   - Note potential conflicts or dependencies

## Discussion and Task Planning

### Phase 1: Initial Research (Claude-led)
1. **Repository Analysis:** Analyze the cloned repositories (from Setup phase) to understand:
   - Architecture patterns and design decisions
   - Key features that could benefit our project
   - Implementation approaches for CLI commands
   - Plugin/extension mechanisms

2. **Current State Analysis:** Review our existing codebase to identify:
   - Integration points for new features
   - Existing patterns to follow (e.g., typer usage)
   - Potential conflicts or challenges
   - Areas for improvement

### Phase 2: Research Enrichment (Multi-tool Collaboration)
1. **Enrich with Perplexity:** Use the ask-perplexity MCP tool to:
   - Research current best practices (2025) for the feature domain
   - Find production examples on GitHub
   - Identify common pitfalls and solutions
   - Discover performance optimization techniques
   
   Example queries:
   ```
   perplexity_ask: "Python CLI plugin architecture best practices 2025"
   perplexity_ask: "LiteLLM integration patterns for CLI applications"
   ```

2. **Validate with Gemini:** Run `llm -m gemini-2.5-flash-preview-05-20` to:
   - Validate architectural decisions
   - Get alternative implementation approaches
   - Review task structure and completeness
   - Ensure alignment with template requirements
   
   Example query:
   ```bash
   llm -m gemini-2.5-flash-preview-05-20 "Review this implementation approach for [feature]. 
   Are there better patterns for [specific challenge]? Consider production scalability."
   ```

3. **Synthesize Findings:** Combine insights from all sources:
   - Claude's code analysis and understanding
   - Perplexity's current best practices
   - Gemini's architectural recommendations
   - Human's domain expertise and requirements

### Phase 3: Task Plan Creation (Gemini-led with Claude support)
1. **Human Consultation:** Ask clarifying questions about:
   - Priority of features
   - Specific requirements or constraints
   - Integration preferences
   - Performance expectations

2. **Generate Task Plan:** Use Gemini (gemini-2.5-pro-preview-05-06 for complex tasks) to create:
   - Detailed implementation tasks following `@docs/TASK_LIST_TEMPLATE_GUIDE.md`
   - Research requirements for each sub-task
   - Verification methods with real tests (NO MOCKING)
   - Clear acceptance criteria
   
   Template for Gemini query:
   ```bash
   llm -m gemini-2.5-pro-preview-05-06 << 'EOF'
   Create a comprehensive task plan for [feature description].
   
   Context:
   - [Current architecture summary]
   - [Integration requirements]
   - [Research findings]
   
   Requirements:
   - Follow template in docs/TASK_LIST_TEMPLATE_GUIDE.md exactly
   - Include 5-6 detailed sub-tasks
   - MANDATORY research process for each task
   - Real validation only (NO MOCKING)
   - Usage examples and version control plan
   
   Focus on:
   - [Specific technical challenges]
   - [Integration points]
   - [Performance requirements]
   EOF
   ```

3. **Review and Refine:** 
   - Claude reviews the generated plan for technical accuracy
   - Human provides feedback on priorities and requirements
   - Iterate if needed using Gemini for adjustments

### Phase 4: Documentation and Execution
1. **Save Task Plan:** Store in `@docs/tasks/` with naming convention:
   - Format: `00N_FEATURE_NAME_CAPS.md`
   - Example: `009_LLM_CLI_SLASH_COMMANDS.md`
   - Increment N based on existing tasks

2. **Final Human Review:** Present the complete plan to human for:
   - Priority confirmation
   - Resource allocation
   - Timeline expectations
   - Any final adjustments

3. **Begin Implementation:** Start executing the task plan:
   - Follow the sub-tasks in order
   - Create verification reports as specified
   - Iterate on incomplete tasks until 100% complete
   - Update progress tracking in the task document

## Collaboration Best Practices

### Claude's Role (Primary Agent)
- Lead the technical analysis and implementation
- Coordinate between different tools and participants
- Ensure code quality and architectural consistency
- Execute the implementation tasks

### Human's Role (Domain Expert)
- Provide requirements and constraints
- Clarify business/technical priorities
- Review and approve task plans
- Make critical decisions on trade-offs

### Ask-Perplexity's Role (Research Specialist)
- Find current best practices and patterns
- Locate production code examples
- Research specific technical challenges
- Provide external validation of approaches

### Gemini's Role (Task Plan Specialist)
- Structure comprehensive task plans
- Ensure template compliance
- Generate detailed implementation steps
- Provide alternative perspectives

## Example Workflow

```bash
# 1. Claude analyzes repos and current code
cd /project/root && source .venv/bin/activate
export PYTHONPATH=/project/root/src
git clone https://github.com/simonw/llm.git repos/llm
# ... analyze code ...

# 2. Claude uses Perplexity for research
perplexity_ask: "CLI plugin architecture Python 2025 best practices"

# 3. Claude consults Gemini for validation
llm -m gemini-2.5-flash-preview-05-20 "Is this plugin architecture scalable?"

# 4. Human provides requirements clarification
# "We need plugins to be hot-reloadable"

# 5. Claude uses Gemini to generate task plan
llm -m gemini-2.5-pro-preview-05-06 < task_plan_prompt.txt

# 6. Save and execute
# Save to docs/tasks/010_PLUGIN_HOT_RELOAD.md
# Begin implementation following the plan
```

## Key Decision Points (Human Input Required)

Throughout the process, pause for human input at these critical points:

1. **Feature Scope Confirmation** (Before Phase 1)
   - "Is this the correct scope for the feature?"
   - "Are there any constraints I should know about?"

2. **Repository Selection** (During Setup)
   - "Are these the right repos to analyze?"
   - "Do you know of other relevant examples?"

3. **Architecture Validation** (After Phase 1)
   - "Does this architectural approach align with your vision?"
   - "Are there any patterns you want to avoid?"

4. **Priority Clarification** (Before Phase 3)
   - "Which aspects are most critical?"
   - "What's the acceptable timeline?"

5. **Task Plan Review** (After Gemini generation)
   - "Does this plan meet your requirements?"
   - "Should we adjust the complexity/scope?"

## Adapting the Process for Different Features

This workflow is flexible and should be adapted based on the feature type:

### For CLI/Tool Features:
- Focus on user experience and command design
- Research similar CLI tools (like simonw's tools)
- Emphasize plugin architecture if extensibility needed

### For API/Integration Features:
- Analyze existing integration patterns
- Research API best practices and standards
- Focus on error handling and reliability

### For Performance/Optimization Features:
- Heavy emphasis on benchmarking in research
- Find proven optimization patterns
- Include performance metrics in all tasks

### For Validation/Testing Features:
- Research testing frameworks and patterns
- Ensure NO MOCKING requirement is emphasized
- Focus on real-world test scenarios

## Common Pitfalls to Avoid

1. **Over-engineering**: Keep solutions as simple as possible
2. **Ignoring existing patterns**: Always check how similar features are implemented
3. **Skipping research**: Don't assume - always verify with Perplexity/Gemini
4. **Mocking in tests**: Remember our NO MOCKING requirement
5. **Poor task granularity**: Tasks should be neither too large nor too small
6. **Not iterating**: If Gemini's first plan isn't perfect, iterate!

## Success Criteria

A successful task plan will have:
1. Clear, measurable objectives
2. Comprehensive research requirements
3. Detailed implementation steps
4. Real validation methods (no mocking)
5. Integration with existing architecture
6. Performance considerations
7. Complete documentation
8. Version control strategy
9. Progress tracking mechanism
10. 100% completion requirement