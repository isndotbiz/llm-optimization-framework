# YAML-Based Workflow Automation for LLM Chaining and Multi-Step AI Tasks

## Table of Contents
1. [Overview](#overview)
2. [YAML Workflow File Structure and Schema](#yaml-workflow-file-structure-and-schema)
3. [Variable Passing Between Steps](#variable-passing-between-steps)
4. [Conditional Execution Patterns](#conditional-execution-patterns)
5. [User Confirmation and Intervention Points](#user-confirmation-and-intervention-points)
6. [Error Handling in Workflows](#error-handling-in-workflows)
7. [Workflow Execution State Management](#workflow-execution-state-management)
8. [Workflow Parser and Executor Architecture](#workflow-parser-and-executor-architecture)
9. [Practical Examples](#practical-examples)

---

## Overview

YAML-based workflow automation for LLMs enables declarative configuration of complex, multi-step AI tasks. This approach provides:

- **Modularity**: Break complex tasks into manageable steps
- **Transparency**: Track workflow state and debug issues
- **Reusability**: Share and version workflow configurations
- **Control**: Implement validation gates and conditional logic
- **Scalability**: Orchestrate multi-agent systems

### Key Concepts

**Prompt Chaining**: Decomposing complex tasks into sequential steps where each LLM invocation processes or builds upon the output of the previous one.

**State Management**: Explicitly tracking workflow state between steps, including contextual summaries, intermediate outputs, and execution status.

**Quality Gates**: Validation checkpoints between steps to ensure output meets specific criteria before proceeding.

---

## YAML Workflow File Structure and Schema

### 1. Semantic Kernel Schema (Microsoft)

Semantic Kernel provides a comprehensive YAML schema for prompt configuration.

```yaml
name: GenerateStory
template: |
  Tell a story about {{topic}} that is {{length}} sentences long.
template_format: handlebars
description: A function that generates a story about a topic.

input_variables:
  - name: topic
    description: The topic of the story.
    is_required: true
  - name: length
    description: The number of sentences in the story.
    is_required: true

output_variable:
  description: The generated story.

execution_settings:
  service1:
    model_id: gpt-4
    temperature: 0.6
  service2:
    model_id: gpt-3.5-turbo
    temperature: 0.4
  default:
    temperature: 0.5
```

**Key Properties:**
- `name`: Function identifier
- `template`: Prompt template with variable placeholders
- `template_format`: semantic-kernel, handlebars, liquid, or jinja2
- `input_variables`: Required and optional inputs with validation
- `execution_settings`: Model-specific configurations

### 2. Swarms Framework Schema

Swarms uses YAML or Markdown frontmatter for agent configuration.

```yaml
agents:
  - agent_name: "Financial-Analysis-Agent"
    system_prompt: "You are a financial analysis expert specializing in market trends and investment strategies."
    model_name: "gpt-4"
    max_loops: 1
    autosave: true
    dashboard: false
    verbose: true
    dynamic_temperature_enabled: true
    saved_state_path: "finance_agent.json"
    user_name: "pe_firm"
    retry_attempts: 1
    context_length: 200000
    task: "How can we allocate our portfolio to maximize returns while minimizing risk?"

  - agent_name: "Risk-Assessment-Agent"
    system_prompt: "You are a risk assessment specialist."
    model_name: "gpt-4"
    task: "Analyze the risk factors in the proposed portfolio allocation."

# Optional Swarm Configuration
swarm_architecture:
  name: "FinancialAnalysisSwarm"
  description: "Multi-agent system for comprehensive financial analysis"
  max_loops: 5
  swarm_type: "ConcurrentWorkflow"
```

**Alternative Markdown Format:**
```yaml
---
name: FinanceAdvisor
description: Expert financial advisor for investment and budgeting guidance
model_name: claude-sonnet-4-20250514
temperature: 0.7
max_loops: 1
system_prompt: |
  You are an expert financial advisor with deep knowledge of investment
  strategies, portfolio management, and risk assessment.
---
```

### 3. Multi-Step Workflow Schema

A comprehensive schema for sequential LLM workflows:

```yaml
workflow:
  name: "ContentCreationPipeline"
  version: "1.0"
  description: "End-to-end content creation with quality checks"

  variables:
    # Global workflow variables
    topic: ""
    target_audience: "technical professionals"
    word_count: 1000
    tone: "professional"

  steps:
    - id: "research"
      name: "Research Phase"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.3
      prompt: |
        Research the topic: {{topic}}
        Target audience: {{target_audience}}
        Provide 5 key points to cover.
      outputs:
        - name: "key_points"
          type: "list"
      validation:
        min_items: 5
        max_items: 5

    - id: "outline"
      name: "Create Outline"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.5
      depends_on: ["research"]
      prompt: |
        Based on these key points:
        {{steps.research.outputs.key_points}}

        Create a detailed outline for a {{word_count}} word article.
      outputs:
        - name: "outline"
          type: "string"
      validation:
        quality_gate: "outline_validator"

    - id: "draft"
      name: "Write Draft"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.7
      depends_on: ["outline"]
      prompt: |
        Write a {{word_count}} word article following this outline:
        {{steps.outline.outputs.outline}}

        Tone: {{tone}}
        Audience: {{target_audience}}
      outputs:
        - name: "draft_content"
          type: "string"
      validation:
        min_length: 800
        max_length: 1200

    - id: "quality_check"
      name: "Quality Assessment"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      depends_on: ["draft"]
      prompt: |
        Review this article draft and provide:
        1. Quality score (1-10)
        2. Issues found
        3. Improvement suggestions

        Draft:
        {{steps.draft.outputs.draft_content}}
      outputs:
        - name: "quality_score"
          type: "number"
        - name: "issues"
          type: "list"
        - name: "suggestions"
          type: "string"
      validation:
        min_quality_score: 7

    - id: "revision"
      name: "Revise Draft"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.6
      depends_on: ["quality_check"]
      condition: "{{steps.quality_check.outputs.quality_score < 9}}"
      prompt: |
        Revise this draft based on the following feedback:
        {{steps.quality_check.outputs.suggestions}}

        Original draft:
        {{steps.draft.outputs.draft_content}}
      outputs:
        - name: "final_content"
          type: "string"

    - id: "human_review"
      name: "Human Approval"
      type: "user_confirmation"
      depends_on: ["revision"]
      message: |
        Please review the final content:
        {{steps.revision.outputs.final_content}}

        Approve for publication?
      outputs:
        - name: "approved"
          type: "boolean"
```

### 4. txtai Workflow Configuration

txtai uses a nested YAML structure for workflow definition:

```yaml
workflow:
  research_pipeline:
    tasks:
      - action: search
        input: "{{query}}"
        output: "search_results"

      - action: summarize
        input: "{{search_results}}"
        params:
          max_length: 200
        output: "summary"

      - action: llm
        input: |
          Based on this summary:
          {{summary}}

          Generate a detailed report.
        model: "gpt-4"
        output: "report"
```

---

## Variable Passing Between Steps

### 1. Template Variable Substitution

Variables can be referenced using different template syntaxes:

**Handlebars Syntax:**
```yaml
prompt: "Analyze {{variable_name}} and provide insights."
```

**Jinja2 Syntax:**
```yaml
prompt: "Process {{ input_data }} using {{ method }}."
```

**Semantic Kernel Syntax:**
```yaml
prompt: "{{$input}} should be processed with {{$parameters.method}}"
```

### 2. Step Output References

Access previous step outputs:

```yaml
steps:
  - id: "step1"
    outputs:
      - name: "result"

  - id: "step2"
    prompt: "Use this data: {{steps.step1.outputs.result}}"
```

### 3. Nested Variable Access

For complex data structures:

```yaml
steps:
  - id: "analysis"
    outputs:
      - name: "metrics"
        type: "object"
        schema:
          accuracy: "number"
          precision: "number"

  - id: "report"
    prompt: "The accuracy was {{steps.analysis.outputs.metrics.accuracy}}"
```

### 4. Variable Scope

```yaml
workflow:
  # Global variables
  variables:
    global_var: "value"

  steps:
    - id: "step1"
      # Step-local variables
      variables:
        local_var: "local_value"
      prompt: "Use {{global_var}} and {{local_var}}"
```

### 5. Dynamic Variable Assignment

```yaml
steps:
  - id: "compute"
    type: "expression"
    expression: "{{steps.step1.outputs.value}} * 2"
    output: "doubled_value"

  - id: "use_computed"
    prompt: "The computed value is {{doubled_value}}"
```

### 6. Azure Logic Apps Variable Pattern

```yaml
steps:
  - id: "create_var"
    action: "Initialize Variable"
    params:
      name: "customerName"
      type: "String"
      value: ""

  - id: "set_var"
    action: "Set Variable"
    params:
      name: "customerName"
      value: "@{agentParameters('extractedName')}"

  - id: "use_var"
    action: "Send Email"
    params:
      to: "@{variables('customerName')}@example.com"
```

---

## Conditional Execution Patterns

### 1. Simple Conditions

```yaml
steps:
  - id: "check_quality"
    outputs:
      - name: "score"
        type: "number"

  - id: "revise"
    condition: "{{steps.check_quality.outputs.score < 8}}"
    prompt: "Revise the content to improve quality."

  - id: "publish"
    condition: "{{steps.check_quality.outputs.score >= 8}}"
    prompt: "Format for publication."
```

### 2. Complex Boolean Logic

```yaml
steps:
  - id: "advanced_check"
    condition: |
      {{steps.sentiment.outputs.score > 0.5 AND
        steps.quality.outputs.grade == 'A' AND
        steps.length.outputs.words >= 1000}}
```

### 3. Conditional Branches

```yaml
steps:
  - id: "route_decision"
    type: "llm_call"
    outputs:
      - name: "category"

  - id: "handle_technical"
    condition: "{{steps.route_decision.outputs.category == 'technical'}}"
    prompt: "Process technical query..."

  - id: "handle_sales"
    condition: "{{steps.route_decision.outputs.category == 'sales'}}"
    prompt: "Process sales inquiry..."

  - id: "handle_support"
    condition: "{{steps.route_decision.outputs.category == 'support'}}"
    prompt: "Process support ticket..."
```

### 4. Iterative Conditions (Loops)

```yaml
steps:
  - id: "improvement_loop"
    type: "llm_call"
    max_iterations: 3
    loop_condition: "{{outputs.quality_score < 9}}"
    prompt: |
      Current quality score: {{outputs.quality_score}}
      Improve the content: {{outputs.content}}
    outputs:
      - name: "quality_score"
      - name: "content"
```

### 5. State-Based Conditions

```yaml
workflow:
  state_machine:
    initial_state: "draft"

    states:
      draft:
        on_complete:
          - target: "review"
            condition: "{{word_count >= 1000}}"
          - target: "expand"
            condition: "{{word_count < 1000}}"

      review:
        on_complete:
          - target: "publish"
            condition: "{{approved == true}}"
          - target: "revise"
            condition: "{{approved == false}}"

      expand:
        on_complete:
          - target: "draft"
```

### 6. Multi-Agent Conditional Delegation

```yaml
steps:
  - id: "lead_scoring"
    outputs:
      - name: "lead_score"
      - name: "email_valid"

  - id: "delegate_to_sales"
    type: "agent_call"
    agent: "sales_agent"
    condition: |
      {{steps.lead_scoring.outputs.lead_score >= 70 AND
        steps.lead_scoring.outputs.email_valid == true}}
```

---

## User Confirmation and Intervention Points

### 1. Basic Approval Gate

```yaml
steps:
  - id: "generate_proposal"
    type: "llm_call"
    outputs:
      - name: "proposal_text"

  - id: "user_approval"
    type: "user_confirmation"
    message: |
      Please review the generated proposal:

      {{steps.generate_proposal.outputs.proposal_text}}

      Approve to continue?
    timeout: 3600  # 1 hour timeout
    default: "reject"
    outputs:
      - name: "approved"
        type: "boolean"

  - id: "send_proposal"
    condition: "{{steps.user_approval.outputs.approved == true}}"
    type: "action"
```

### 2. User Input Collection

```yaml
steps:
  - id: "initial_draft"
    type: "llm_call"
    outputs:
      - name: "draft"

  - id: "user_feedback"
    type: "user_input"
    prompt: |
      Draft:
      {{steps.initial_draft.outputs.draft}}

      What changes would you like?
    inputs:
      - name: "feedback"
        type: "text"
        required: true
      - name: "priority"
        type: "select"
        options: ["low", "medium", "high"]
        default: "medium"
    outputs:
      - name: "feedback"
      - name: "priority"

  - id: "revise_with_feedback"
    prompt: |
      Revise this draft based on user feedback:
      Draft: {{steps.initial_draft.outputs.draft}}
      Feedback: {{steps.user_feedback.outputs.feedback}}
      Priority: {{steps.user_feedback.outputs.priority}}
```

### 3. Human-in-the-Loop Pattern

```yaml
steps:
  - id: "auto_classify"
    type: "llm_call"
    outputs:
      - name: "category"
      - name: "confidence"

  - id: "human_verification"
    type: "user_confirmation"
    condition: "{{steps.auto_classify.outputs.confidence < 0.8}}"
    message: |
      AI classified this as: {{steps.auto_classify.outputs.category}}
      Confidence: {{steps.auto_classify.outputs.confidence}}

      Is this correct?
    options:
      - label: "Correct"
        value: true
      - label: "Incorrect - Let me specify"
        value: false
    outputs:
      - name: "verified"

  - id: "manual_classification"
    type: "user_input"
    condition: "{{steps.human_verification.outputs.verified == false}}"
    prompt: "Please specify the correct category:"
    inputs:
      - name: "correct_category"
```

### 4. Selective Review

```yaml
steps:
  - id: "process_batch"
    type: "llm_call"
    outputs:
      - name: "results"
        type: "array"

  - id: "flag_for_review"
    type: "filter"
    condition: "{{item.confidence < 0.7}}"
    input: "{{steps.process_batch.outputs.results}}"
    outputs:
      - name: "flagged_items"

  - id: "batch_review"
    type: "user_review_batch"
    items: "{{steps.flag_for_review.outputs.flagged_items}}"
    review_options:
      - "Approve"
      - "Reject"
      - "Modify"
    outputs:
      - name: "review_results"
```

### 5. Interactive Refinement

```yaml
steps:
  - id: "generate_initial"
    type: "llm_call"
    outputs:
      - name: "content"

  - id: "refinement_loop"
    type: "interactive_loop"
    max_iterations: 5
    steps:
      - id: "show_current"
        type: "user_display"
        content: "{{current_content}}"

      - id: "ask_satisfied"
        type: "user_confirmation"
        message: "Are you satisfied with this version?"
        outputs:
          - name: "satisfied"

      - id: "get_changes"
        type: "user_input"
        condition: "{{satisfied == false}}"
        prompt: "What would you like to change?"
        outputs:
          - name: "change_request"

      - id: "apply_changes"
        type: "llm_call"
        condition: "{{satisfied == false}}"
        prompt: |
          Apply these changes:
          {{change_request}}

          To this content:
          {{current_content}}
        outputs:
          - name: "current_content"

    exit_condition: "{{satisfied == true}}"
```

---

## Error Handling in Workflows

### 1. Retry Logic

```yaml
steps:
  - id: "api_call"
    type: "llm_call"
    error_handling:
      retry:
        max_attempts: 3
        backoff: "exponential"  # linear, exponential, or fixed
        initial_delay: 1000     # milliseconds
        max_delay: 10000
      retry_conditions:
        - "status_code == 429"  # Rate limit
        - "status_code == 503"  # Service unavailable
        - "timeout == true"
```

### 2. Fallback Steps

```yaml
steps:
  - id: "primary_analysis"
    type: "llm_call"
    model: "gpt-4"
    error_handling:
      on_error: "fallback_analysis"

  - id: "fallback_analysis"
    type: "llm_call"
    model: "gpt-3.5-turbo"
    prompt: "Perform simplified analysis..."
    error_handling:
      on_error: "default_response"

  - id: "default_response"
    type: "static_response"
    content: "Analysis unavailable at this time."
```

### 3. Error Validation Gates

```yaml
steps:
  - id: "generate_code"
    type: "llm_call"
    outputs:
      - name: "code"

  - id: "validate_syntax"
    type: "validation"
    validator: "python_syntax_checker"
    input: "{{steps.generate_code.outputs.code}}"
    outputs:
      - name: "is_valid"
      - name: "errors"

  - id: "fix_errors"
    type: "llm_call"
    condition: "{{steps.validate_syntax.outputs.is_valid == false}}"
    max_iterations: 3
    prompt: |
      Fix these syntax errors:
      {{steps.validate_syntax.outputs.errors}}

      In this code:
      {{steps.generate_code.outputs.code}}
    outputs:
      - name: "fixed_code"
    error_handling:
      on_max_iterations: "manual_review"
```

### 4. Global Error Handlers

```yaml
workflow:
  error_handling:
    global_handlers:
      - error_type: "LLMAPIError"
        handler: "log_and_retry"
        retry_count: 3

      - error_type: "ValidationError"
        handler: "human_intervention"
        notification:
          type: "email"
          recipient: "admin@example.com"

      - error_type: "TimeoutError"
        handler: "graceful_degradation"
        fallback_response: "Request timed out. Please try again."

    default_handler: "log_and_fail"
```

### 5. Compensation Actions

```yaml
steps:
  - id: "reserve_resources"
    type: "action"
    compensation: "release_resources"

  - id: "process_payment"
    type: "action"
    compensation: "refund_payment"

  - id: "send_confirmation"
    type: "action"
    error_handling:
      on_error: "compensate_all"  # Triggers all compensation actions

compensations:
  - id: "release_resources"
    action: "api_call"
    endpoint: "/resources/release"

  - id: "refund_payment"
    action: "api_call"
    endpoint: "/payments/refund"
```

### 6. Circuit Breaker Pattern

```yaml
workflow:
  circuit_breakers:
    external_api:
      failure_threshold: 5
      timeout: 30000  # 30 seconds
      reset_timeout: 60000  # 1 minute
      half_open_requests: 3

steps:
  - id: "call_external_api"
    type: "api_call"
    circuit_breaker: "external_api"
    error_handling:
      on_circuit_open: "use_cached_data"
```

---

## Workflow Execution State Management

### 1. State Persistence

```yaml
workflow:
  state_management:
    persistence:
      enabled: true
      storage: "database"  # database, file, redis, memory
      checkpoint_frequency: "after_each_step"
      retention_policy:
        days: 30
```

### 2. State Checkpoints

```yaml
steps:
  - id: "long_running_task"
    type: "llm_call"
    checkpoints:
      - after: "data_loaded"
      - after: "validation_complete"
      - before: "final_processing"

    state_data:
      - "intermediate_results"
      - "processing_metadata"
      - "elapsed_time"
```

### 3. Resume from Failure

```yaml
workflow:
  recovery:
    enabled: true
    resume_strategy: "from_last_checkpoint"  # from_start, from_failed_step, from_last_checkpoint

    on_resume:
      - action: "validate_state"
      - action: "notify_user"
        message: "Workflow resuming from {{last_checkpoint}}"
```

### 4. State Machine Definition

```yaml
workflow:
  type: "state_machine"

  states:
    INIT:
      entry_action: "initialize_variables"
      transitions:
        - to: "PROCESSING"
          trigger: "start"

    PROCESSING:
      entry_action: "begin_processing"
      on_state_action: "process_step"
      transitions:
        - to: "VALIDATION"
          condition: "{{processing_complete}}"
        - to: "ERROR"
          condition: "{{error_occurred}}"
      timeout: 300000  # 5 minutes
      on_timeout: "ERROR"

    VALIDATION:
      entry_action: "run_validation"
      transitions:
        - to: "COMPLETE"
          condition: "{{validation_passed}}"
        - to: "PROCESSING"
          condition: "{{needs_revision}}"
        - to: "HUMAN_REVIEW"
          condition: "{{confidence < 0.8}}"

    HUMAN_REVIEW:
      entry_action: "request_review"
      transitions:
        - to: "COMPLETE"
          trigger: "approved"
        - to: "PROCESSING"
          trigger: "revision_requested"

    COMPLETE:
      entry_action: "finalize_output"
      terminal: true

    ERROR:
      entry_action: "log_error"
      transitions:
        - to: "PROCESSING"
          trigger: "retry"
          max_retries: 3
        - to: "FAILED"
          condition: "{{retry_count >= 3}}"

    FAILED:
      entry_action: "cleanup_resources"
      terminal: true
```

### 5. Context Accumulation

```yaml
steps:
  - id: "step1"
    type: "llm_call"
    context_strategy: "append"  # append, replace, summarize
    outputs:
      - name: "result1"

  - id: "step2"
    type: "llm_call"
    context_strategy: "summarize"
    context_template: |
      Previous context summary: {{context_summary}}
      Latest result: {{steps.step1.outputs.result1}}
    outputs:
      - name: "result2"

  - id: "step3"
    type: "llm_call"
    context_strategy: "sliding_window"
    context_config:
      window_size: 3  # Keep last 3 steps
      max_tokens: 2000
```

### 6. Distributed State Synchronization

```yaml
workflow:
  distributed:
    enabled: true
    coordination: "redis"

    state_sync:
      mode: "optimistic"  # optimistic or pessimistic
      conflict_resolution: "last_write_wins"

    locks:
      - resource: "shared_data"
        timeout: 10000
        retry_delay: 1000
```

---

## Workflow Parser and Executor Architecture

### 1. Parser Implementation

```python
# workflow_parser.py

import yaml
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class StepType(Enum):
    LLM_CALL = "llm_call"
    USER_CONFIRMATION = "user_confirmation"
    USER_INPUT = "user_input"
    VALIDATION = "validation"
    ACTION = "action"
    EXPRESSION = "expression"

@dataclass
class WorkflowStep:
    id: str
    name: str
    type: StepType
    prompt: str = None
    model: str = None
    temperature: float = 0.7
    depends_on: List[str] = None
    condition: str = None
    outputs: List[Dict[str, Any]] = None
    validation: Dict[str, Any] = None
    error_handling: Dict[str, Any] = None
    variables: Dict[str, Any] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.outputs is None:
            self.outputs = []
        if self.variables is None:
            self.variables = {}

@dataclass
class Workflow:
    name: str
    version: str
    description: str
    variables: Dict[str, Any]
    steps: List[WorkflowStep]
    error_handling: Dict[str, Any] = None
    state_management: Dict[str, Any] = None

class WorkflowParser:
    """Parse YAML workflow definitions into structured objects."""

    def __init__(self):
        self.workflows = {}

    def parse_file(self, filepath: str) -> Workflow:
        """Load and parse a YAML workflow file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        return self.parse_dict(data)

    def parse_dict(self, data: Dict[str, Any]) -> Workflow:
        """Parse a workflow dictionary."""
        workflow_data = data.get('workflow', {})

        workflow = Workflow(
            name=workflow_data.get('name'),
            version=workflow_data.get('version', '1.0'),
            description=workflow_data.get('description', ''),
            variables=workflow_data.get('variables', {}),
            steps=self._parse_steps(workflow_data.get('steps', [])),
            error_handling=workflow_data.get('error_handling'),
            state_management=workflow_data.get('state_management')
        )

        return workflow

    def _parse_steps(self, steps_data: List[Dict]) -> List[WorkflowStep]:
        """Parse workflow steps."""
        steps = []

        for step_data in steps_data:
            step = WorkflowStep(
                id=step_data.get('id'),
                name=step_data.get('name'),
                type=StepType(step_data.get('type', 'llm_call')),
                prompt=step_data.get('prompt'),
                model=step_data.get('model'),
                temperature=step_data.get('temperature', 0.7),
                depends_on=step_data.get('depends_on', []),
                condition=step_data.get('condition'),
                outputs=step_data.get('outputs', []),
                validation=step_data.get('validation'),
                error_handling=step_data.get('error_handling'),
                variables=step_data.get('variables', {})
            )
            steps.append(step)

        return steps

    def validate_workflow(self, workflow: Workflow) -> List[str]:
        """Validate workflow for common issues."""
        errors = []

        # Check for duplicate step IDs
        step_ids = [step.id for step in workflow.steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step IDs found")

        # Validate dependencies
        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step {step.id} depends on non-existent step {dep}")

        # Check for circular dependencies
        if self._has_circular_deps(workflow.steps):
            errors.append("Circular dependencies detected")

        return errors

    def _has_circular_deps(self, steps: List[WorkflowStep]) -> bool:
        """Detect circular dependencies using DFS."""
        graph = {step.id: step.depends_on for step in steps}
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for step in steps:
            if step.id not in visited:
                if has_cycle(step.id):
                    return True

        return False
```

### 2. Variable Substitution Engine

```python
# variable_substitution.py

import re
from typing import Dict, Any
from jinja2 import Environment, Template

class VariableSubstitution:
    """Handle variable substitution in workflow templates."""

    def __init__(self):
        self.jinja_env = Environment()
        self.context = {}

    def set_context(self, context: Dict[str, Any]):
        """Set the variable context."""
        self.context = context

    def substitute(self, template_str: str, additional_context: Dict = None) -> str:
        """Perform variable substitution."""
        # Merge contexts
        full_context = {**self.context}
        if additional_context:
            full_context.update(additional_context)

        # Handle different template formats
        if '{{' in template_str and '}}' in template_str:
            # Jinja2/Handlebars style
            template = self.jinja_env.from_string(template_str)
            return template.render(**full_context)
        elif '${' in template_str and '}' in template_str:
            # Shell-style substitution
            return self._substitute_shell_style(template_str, full_context)
        else:
            return template_str

    def _substitute_shell_style(self, template_str: str, context: Dict) -> str:
        """Handle ${variable} style substitution."""
        def replacer(match):
            var_name = match.group(1)
            return str(self._get_nested_value(context, var_name))

        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replacer, template_str)

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    def evaluate_condition(self, condition: str, context: Dict = None) -> bool:
        """Evaluate a conditional expression."""
        full_context = {**self.context}
        if context:
            full_context.update(context)

        # Substitute variables first
        substituted = self.substitute(condition, full_context)

        # Convert to Python expression
        python_expr = self._convert_to_python(substituted)

        try:
            # Safely evaluate
            return bool(eval(python_expr, {"__builtins__": {}}, full_context))
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False

    def _convert_to_python(self, expr: str) -> str:
        """Convert workflow expression to Python."""
        # Replace AND/OR with Python equivalents
        expr = expr.replace(' AND ', ' and ')
        expr = expr.replace(' OR ', ' or ')
        expr = expr.replace(' NOT ', ' not ')
        return expr
```

### 3. Workflow Executor

```python
# workflow_executor.py

import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class StepResult:
    """Result of a workflow step execution."""
    def __init__(self, step_id: str):
        self.step_id = step_id
        self.status = ExecutionStatus.PENDING
        self.outputs = {}
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.duration_ms = None

class WorkflowExecutor:
    """Execute parsed workflows with state management."""

    def __init__(self, llm_client, state_store=None):
        self.llm_client = llm_client
        self.state_store = state_store or InMemoryStateStore()
        self.variable_sub = VariableSubstitution()
        self.execution_id = None

    async def execute(self, workflow: Workflow, initial_vars: Dict = None) -> Dict[str, Any]:
        """Execute a workflow."""
        self.execution_id = self._generate_execution_id()

        # Initialize state
        state = WorkflowState(
            workflow_name=workflow.name,
            execution_id=self.execution_id,
            variables={**workflow.variables, **(initial_vars or {})},
            step_results={}
        )

        # Set up variable context
        self.variable_sub.set_context({
            'variables': state.variables,
            'steps': {}
        })

        try:
            # Execute steps in order
            for step in workflow.steps:
                # Check dependencies
                if not await self._dependencies_met(step, state):
                    continue

                # Check condition
                if step.condition and not self._evaluate_condition(step.condition, state):
                    continue

                # Execute step
                result = await self._execute_step(step, state)
                state.step_results[step.id] = result

                # Update context
                self.variable_sub.context['steps'][step.id] = {
                    'outputs': result.outputs
                }

                # Save checkpoint
                await self.state_store.save_state(self.execution_id, state)

                # Check for errors
                if result.status == ExecutionStatus.FAILED:
                    if not await self._handle_step_error(step, result, state):
                        raise WorkflowExecutionError(f"Step {step.id} failed: {result.error}")

            return {
                'status': 'completed',
                'execution_id': self.execution_id,
                'results': state.step_results,
                'final_variables': state.variables
            }

        except Exception as e:
            await self._handle_workflow_error(workflow, state, e)
            raise

    async def _execute_step(self, step: WorkflowStep, state: WorkflowState) -> StepResult:
        """Execute a single workflow step."""
        result = StepResult(step.id)
        result.started_at = datetime.now()
        result.status = ExecutionStatus.RUNNING

        try:
            if step.type == StepType.LLM_CALL:
                result = await self._execute_llm_call(step, state, result)
            elif step.type == StepType.USER_CONFIRMATION:
                result = await self._execute_user_confirmation(step, state, result)
            elif step.type == StepType.VALIDATION:
                result = await self._execute_validation(step, state, result)
            elif step.type == StepType.EXPRESSION:
                result = await self._execute_expression(step, state, result)
            else:
                raise ValueError(f"Unknown step type: {step.type}")

            result.status = ExecutionStatus.COMPLETED

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)

        finally:
            result.completed_at = datetime.now()
            result.duration_ms = (result.completed_at - result.started_at).total_seconds() * 1000

        return result

    async def _execute_llm_call(self, step: WorkflowStep, state: WorkflowState, result: StepResult) -> StepResult:
        """Execute an LLM call step."""
        # Substitute variables in prompt
        prompt = self.variable_sub.substitute(step.prompt)

        # Call LLM
        response = await self.llm_client.complete(
            prompt=prompt,
            model=step.model,
            temperature=step.temperature
        )

        # Extract outputs
        for output_def in step.outputs:
            output_name = output_def.get('name')
            # Parse output based on type
            output_value = self._extract_output(response, output_def)
            result.outputs[output_name] = output_value

        # Validate outputs
        if step.validation:
            self._validate_outputs(result.outputs, step.validation)

        return result

    async def _execute_user_confirmation(self, step: WorkflowStep, state: WorkflowState, result: StepResult) -> StepResult:
        """Execute a user confirmation step."""
        message = self.variable_sub.substitute(step.prompt or step.get('message', ''))

        # This would integrate with your UI layer
        approved = await self._request_user_confirmation(message)

        result.outputs['approved'] = approved
        return result

    async def _execute_validation(self, step: WorkflowStep, state: WorkflowState, result: StepResult) -> StepResult:
        """Execute a validation step."""
        validator_name = step.validation.get('validator')
        input_value = self.variable_sub.substitute(step.get('input', ''))

        # Run validator
        is_valid, errors = await self._run_validator(validator_name, input_value)

        result.outputs['is_valid'] = is_valid
        result.outputs['errors'] = errors
        return result

    async def _execute_expression(self, step: WorkflowStep, state: WorkflowState, result: StepResult) -> StepResult:
        """Execute an expression evaluation step."""
        expression = step.get('expression', '')
        evaluated = self.variable_sub.substitute(expression)

        # Safely evaluate
        value = eval(evaluated, {"__builtins__": {}}, self.variable_sub.context)

        output_name = step.outputs[0].get('name') if step.outputs else 'result'
        result.outputs[output_name] = value
        return result

    def _evaluate_condition(self, condition: str, state: WorkflowState) -> bool:
        """Evaluate a step condition."""
        context = {
            'variables': state.variables,
            'steps': {
                step_id: {'outputs': result.outputs}
                for step_id, result in state.step_results.items()
            }
        }
        return self.variable_sub.evaluate_condition(condition, context)

    async def _dependencies_met(self, step: WorkflowStep, state: WorkflowState) -> bool:
        """Check if all step dependencies are met."""
        for dep_id in step.depends_on:
            if dep_id not in state.step_results:
                return False
            if state.step_results[dep_id].status != ExecutionStatus.COMPLETED:
                return False
        return True

    def _generate_execution_id(self) -> str:
        """Generate unique execution ID."""
        import uuid
        return str(uuid.uuid4())

class WorkflowState:
    """Represents the current state of workflow execution."""
    def __init__(self, workflow_name: str, execution_id: str, variables: Dict, step_results: Dict):
        self.workflow_name = workflow_name
        self.execution_id = execution_id
        self.variables = variables
        self.step_results = step_results
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class InMemoryStateStore:
    """Simple in-memory state storage."""
    def __init__(self):
        self.states = {}

    async def save_state(self, execution_id: str, state: WorkflowState):
        """Save workflow state."""
        state.updated_at = datetime.now()
        self.states[execution_id] = state

    async def load_state(self, execution_id: str) -> Optional[WorkflowState]:
        """Load workflow state."""
        return self.states.get(execution_id)

    async def delete_state(self, execution_id: str):
        """Delete workflow state."""
        if execution_id in self.states:
            del self.states[execution_id]

class WorkflowExecutionError(Exception):
    """Workflow execution error."""
    pass
```

### 4. LLM Client Integration

```python
# llm_client.py

from typing import Dict, Any, Optional
import openai
from anthropic import Anthropic

class LLMClient:
    """Unified interface for multiple LLM providers."""

    def __init__(self, default_provider="openai"):
        self.default_provider = default_provider
        self.openai_client = openai.OpenAI()
        self.anthropic_client = Anthropic()

    async def complete(self,
                      prompt: str,
                      model: str = None,
                      temperature: float = 0.7,
                      max_tokens: int = 2000,
                      provider: str = None) -> str:
        """Call LLM for text completion."""
        provider = provider or self._detect_provider(model) or self.default_provider

        if provider == "openai":
            return await self._openai_complete(prompt, model, temperature, max_tokens)
        elif provider == "anthropic":
            return await self._anthropic_complete(prompt, model, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _openai_complete(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """OpenAI completion."""
        response = self.openai_client.chat.completions.create(
            model=model or "gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def _anthropic_complete(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Anthropic completion."""
        response = self.anthropic_client.messages.create(
            model=model or "claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _detect_provider(self, model: str) -> Optional[str]:
        """Detect provider from model name."""
        if not model:
            return None

        if model.startswith("gpt-") or model.startswith("text-"):
            return "openai"
        elif model.startswith("claude-"):
            return "anthropic"

        return None
```

---

## Practical Examples

### Example 1: Research Paper Summarization Pipeline

```yaml
workflow:
  name: "ResearchPaperSummarization"
  version: "1.0"
  description: "Multi-step workflow to summarize research papers"

  variables:
    paper_url: ""
    target_length: 500
    technical_level: "intermediate"

  steps:
    - id: "extract_text"
      name: "Extract Paper Content"
      type: "action"
      action: "fetch_pdf_text"
      params:
        url: "{{paper_url}}"
      outputs:
        - name: "paper_text"
          type: "string"
      error_handling:
        retry:
          max_attempts: 3

    - id: "identify_sections"
      name: "Identify Paper Sections"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      depends_on: ["extract_text"]
      prompt: |
        Analyze this research paper and identify the main sections:
        - Abstract
        - Introduction
        - Methodology
        - Results
        - Conclusion

        Paper text:
        {{steps.extract_text.outputs.paper_text}}

        Return as JSON: {"sections": {"abstract": "...", "introduction": "...", ...}}
      outputs:
        - name: "sections"
          type: "object"

    - id: "summarize_abstract"
      name: "Summarize Abstract"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.3
      depends_on: ["identify_sections"]
      prompt: |
        Summarize this abstract in 2-3 sentences:
        {{steps.identify_sections.outputs.sections.abstract}}
      outputs:
        - name: "abstract_summary"

    - id: "summarize_methodology"
      name: "Summarize Methodology"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.3
      depends_on: ["identify_sections"]
      prompt: |
        Explain the methodology used in this research in simple terms:
        {{steps.identify_sections.outputs.sections.methodology}}

        Target audience: {{technical_level}}
      outputs:
        - name: "methodology_summary"

    - id: "summarize_results"
      name: "Summarize Results"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.3
      depends_on: ["identify_sections"]
      prompt: |
        Summarize the key findings from this results section:
        {{steps.identify_sections.outputs.sections.results}}
      outputs:
        - name: "results_summary"

    - id: "generate_final_summary"
      name: "Generate Final Summary"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.5
      depends_on: ["summarize_abstract", "summarize_methodology", "summarize_results"]
      prompt: |
        Create a comprehensive summary of this research paper combining:

        Abstract: {{steps.summarize_abstract.outputs.abstract_summary}}
        Methodology: {{steps.summarize_methodology.outputs.methodology_summary}}
        Results: {{steps.summarize_results.outputs.results_summary}}

        Target length: {{target_length}} words
        Technical level: {{technical_level}}

        Include:
        1. Main research question
        2. Approach used
        3. Key findings
        4. Significance of results
      outputs:
        - name: "final_summary"
      validation:
        min_length: 400
        max_length: 600

    - id: "quality_check"
      name: "Quality Check"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.1
      depends_on: ["generate_final_summary"]
      prompt: |
        Evaluate this research summary for:
        1. Accuracy (1-10)
        2. Clarity (1-10)
        3. Completeness (1-10)

        Summary:
        {{steps.generate_final_summary.outputs.final_summary}}

        Original paper abstract:
        {{steps.identify_sections.outputs.sections.abstract}}

        Return JSON: {"accuracy": X, "clarity": Y, "completeness": Z, "overall": avg}
      outputs:
        - name: "quality_scores"
          type: "object"

    - id: "human_review"
      name: "Expert Review"
      type: "user_confirmation"
      depends_on: ["quality_check"]
      condition: "{{steps.quality_check.outputs.quality_scores.overall < 8}}"
      message: |
        The automated quality check scored this summary {{steps.quality_check.outputs.quality_scores.overall}}/10.

        Summary:
        {{steps.generate_final_summary.outputs.final_summary}}

        Please review and approve or request revision.
      outputs:
        - name: "approved"
```

### Example 2: Customer Support Ticket Routing

```yaml
workflow:
  name: "SupportTicketRouting"
  version: "1.0"
  description: "Intelligent routing of customer support tickets"

  variables:
    ticket_content: ""
    customer_tier: "standard"
    urgency_threshold: 7

  steps:
    - id: "classify_issue"
      name: "Classify Issue Type"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      prompt: |
        Classify this support ticket into one of these categories:
        - technical
        - billing
        - account
        - feature_request
        - bug_report

        Ticket: {{ticket_content}}

        Return JSON: {"category": "...", "confidence": 0.XX}
      outputs:
        - name: "category"
        - name: "confidence"
          type: "number"

    - id: "assess_urgency"
      name: "Assess Urgency"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.1
      depends_on: ["classify_issue"]
      prompt: |
        Rate the urgency of this ticket from 1-10:

        Category: {{steps.classify_issue.outputs.category}}
        Content: {{ticket_content}}
        Customer tier: {{customer_tier}}

        Consider:
        - Revenue impact
        - Service disruption
        - Customer sentiment

        Return JSON: {"urgency_score": X, "reasoning": "..."}
      outputs:
        - name: "urgency_score"
          type: "number"
        - name: "reasoning"

    - id: "extract_details"
      name: "Extract Key Details"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      depends_on: ["classify_issue"]
      prompt: |
        Extract structured information from this ticket:

        {{ticket_content}}

        Extract:
        - Product/service mentioned
        - Error messages (if any)
        - Steps to reproduce (if applicable)
        - Customer sentiment (positive/neutral/negative)

        Return as JSON
      outputs:
        - name: "ticket_details"
          type: "object"

    - id: "check_knowledge_base"
      name: "Search Knowledge Base"
      type: "action"
      action: "search_kb"
      depends_on: ["extract_details"]
      params:
        query: "{{steps.classify_issue.outputs.category}} {{steps.extract_details.outputs.ticket_details.product}}"
        limit: 3
      outputs:
        - name: "kb_results"
          type: "array"

    - id: "generate_suggested_response"
      name: "Generate Suggested Response"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.6
      depends_on: ["extract_details", "check_knowledge_base"]
      condition: "{{steps.classify_issue.outputs.confidence > 0.8}}"
      prompt: |
        Generate a helpful response to this support ticket:

        Ticket: {{ticket_content}}
        Category: {{steps.classify_issue.outputs.category}}
        Details: {{steps.extract_details.outputs.ticket_details}}

        Related KB articles:
        {{steps.check_knowledge_base.outputs.kb_results}}

        Tone: Professional and empathetic
        Customer tier: {{customer_tier}}
      outputs:
        - name: "suggested_response"

    - id: "route_to_specialist"
      name: "Route to Specialist"
      type: "action"
      action: "assign_ticket"
      depends_on: ["classify_issue", "assess_urgency"]
      condition: "{{steps.assess_urgency.outputs.urgency_score >= urgency_threshold}}"
      params:
        department: "{{steps.classify_issue.outputs.category}}"
        priority: "high"
        agent: "specialist"
      outputs:
        - name: "assignment_id"

    - id: "route_to_general"
      name: "Route to General Queue"
      type: "action"
      action: "assign_ticket"
      depends_on: ["classify_issue", "assess_urgency"]
      condition: "{{steps.assess_urgency.outputs.urgency_score < urgency_threshold}}"
      params:
        department: "{{steps.classify_issue.outputs.category}}"
        priority: "normal"
        queue: "general"
        suggested_response: "{{steps.generate_suggested_response.outputs.suggested_response}}"
      outputs:
        - name: "assignment_id"
```

### Example 3: Content Generation with Iterative Refinement

```yaml
workflow:
  name: "BlogPostGeneration"
  version: "1.0"
  description: "Generate and refine blog post with quality checks"

  variables:
    topic: ""
    target_keywords: []
    word_count: 1500
    max_refinement_iterations: 3

  steps:
    - id: "keyword_research"
      name: "Research Related Keywords"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.7
      prompt: |
        Given this topic: {{topic}}
        And target keywords: {{target_keywords}}

        Suggest 10 additional related keywords and semantic variations
        that would improve SEO and content relevance.

        Return as JSON array: ["keyword1", "keyword2", ...]
      outputs:
        - name: "additional_keywords"
          type: "array"

    - id: "create_outline"
      name: "Create Content Outline"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.6
      depends_on: ["keyword_research"]
      prompt: |
        Create a detailed outline for a blog post about: {{topic}}

        Requirements:
        - Target length: {{word_count}} words
        - Include these keywords naturally: {{target_keywords}}
        - Related terms to incorporate: {{steps.keyword_research.outputs.additional_keywords}}

        Structure:
        1. Compelling introduction with hook
        2. 3-5 main sections with subpoints
        3. Conclusion with call-to-action

        For each section, specify:
        - Main point
        - Supporting details
        - Target word count
      outputs:
        - name: "outline"

    - id: "user_approve_outline"
      name: "Approve Outline"
      type: "user_confirmation"
      depends_on: ["create_outline"]
      message: |
        Review this content outline:

        {{steps.create_outline.outputs.outline}}

        Approve to continue with drafting?
      outputs:
        - name: "outline_approved"

    - id: "revise_outline"
      name: "Revise Outline"
      type: "user_input"
      depends_on: ["user_approve_outline"]
      condition: "{{steps.user_approve_outline.outputs.outline_approved == false}}"
      prompt: "What changes would you like to the outline?"
      inputs:
        - name: "outline_feedback"
      outputs:
        - name: "outline_feedback"

    - id: "write_draft"
      name: "Write Initial Draft"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.7
      depends_on: ["user_approve_outline"]
      condition: "{{steps.user_approve_outline.outputs.outline_approved == true}}"
      prompt: |
        Write a complete blog post following this outline:

        {{steps.create_outline.outputs.outline}}

        Requirements:
        - Engaging and informative tone
        - Natural keyword integration: {{target_keywords}}
        - Target length: {{word_count}} words
        - Include examples and actionable insights
        - Write compelling introduction and conclusion
      outputs:
        - name: "draft_content"
      validation:
        min_length: 1200

    - id: "analyze_draft"
      name: "Analyze Draft Quality"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      depends_on: ["write_draft"]
      prompt: |
        Analyze this blog post draft:

        {{steps.write_draft.outputs.draft_content}}

        Evaluate:
        1. Readability (1-10)
        2. Keyword optimization (1-10)
        3. Structure and flow (1-10)
        4. Engagement (1-10)
        5. Completeness (1-10)

        Identify:
        - Missing elements
        - Areas needing improvement
        - Sections that could be expanded
        - Any awkward phrasing

        Return JSON: {
          "scores": {...},
          "overall_quality": X,
          "issues": [...],
          "suggestions": [...]
        }
      outputs:
        - name: "quality_analysis"
          type: "object"

    - id: "refinement_loop"
      name: "Iterative Refinement"
      type: "loop"
      depends_on: ["analyze_draft"]
      max_iterations: "{{max_refinement_iterations}}"
      exit_condition: "{{current_iteration.outputs.quality_analysis.overall_quality >= 8}}"

      steps:
        - id: "refine_content"
          type: "llm_call"
          model: "gpt-4"
          temperature: 0.6
          prompt: |
            Improve this blog post draft based on this feedback:

            Current draft:
            {{current_content}}

            Quality score: {{current_quality}}/10

            Issues identified:
            {{current_issues}}

            Suggestions:
            {{current_suggestions}}

            Make targeted improvements while maintaining the core message and structure.
          outputs:
            - name: "refined_content"

        - id: "reanalyze"
          type: "llm_call"
          model: "gpt-4"
          temperature: 0.2
          depends_on: ["refine_content"]
          prompt: |
            Re-evaluate this improved draft:

            {{steps.refine_content.outputs.refined_content}}

            Compare to previous version and rate improvement.
            Return quality analysis in same JSON format.
          outputs:
            - name: "quality_analysis"
              type: "object"

    - id: "seo_optimization"
      name: "SEO Optimization"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.4
      depends_on: ["refinement_loop"]
      prompt: |
        Optimize this blog post for SEO without changing the core content:

        {{steps.refinement_loop.outputs.final_content}}

        Target keywords: {{target_keywords}}

        Add/improve:
        - Meta description (150-160 chars)
        - SEO title (55-60 chars)
        - Heading tags (H2, H3)
        - Internal link suggestions
        - Image alt text suggestions

        Return as JSON with optimized content and metadata
      outputs:
        - name: "seo_optimized_content"
          type: "object"

    - id: "final_review"
      name: "Final Human Review"
      type: "user_confirmation"
      depends_on: ["seo_optimization"]
      message: |
        Final blog post ready for review:

        Title: {{steps.seo_optimization.outputs.seo_optimized_content.title}}
        Meta: {{steps.seo_optimization.outputs.seo_optimized_content.meta_description}}
        Quality Score: {{steps.refinement_loop.outputs.quality_analysis.overall_quality}}/10

        {{steps.seo_optimization.outputs.seo_optimized_content.content}}

        Approve for publication?
      outputs:
        - name: "approved_for_publication"

    - id: "publish"
      name: "Publish Post"
      type: "action"
      action: "publish_blog_post"
      depends_on: ["final_review"]
      condition: "{{steps.final_review.outputs.approved_for_publication == true}}"
      params:
        content: "{{steps.seo_optimization.outputs.seo_optimized_content}}"
      outputs:
        - name: "published_url"
```

### Example 4: Code Review and Documentation Workflow

```yaml
workflow:
  name: "CodeReviewDocumentation"
  version: "1.0"
  description: "Automated code review with documentation generation"

  variables:
    repo_url: ""
    branch: "main"
    file_patterns: ["*.py", "*.js", "*.java"]
    review_depth: "thorough"

  steps:
    - id: "fetch_code"
      name: "Fetch Code Changes"
      type: "action"
      action: "git_diff"
      params:
        repo: "{{repo_url}}"
        branch: "{{branch}}"
        patterns: "{{file_patterns}}"
      outputs:
        - name: "changed_files"
          type: "array"

    - id: "analyze_changes"
      name: "Analyze Code Changes"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      depends_on: ["fetch_code"]
      prompt: |
        Analyze these code changes:

        {{steps.fetch_code.outputs.changed_files}}

        Categorize changes as:
        - New features
        - Bug fixes
        - Refactoring
        - Performance improvements
        - Breaking changes

        Return JSON with categorized changes
      outputs:
        - name: "change_analysis"
          type: "object"

    - id: "security_review"
      name: "Security Analysis"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.1
      depends_on: ["fetch_code"]
      prompt: |
        Review code for security vulnerabilities:

        {{steps.fetch_code.outputs.changed_files}}

        Check for:
        - SQL injection risks
        - XSS vulnerabilities
        - Authentication issues
        - Data exposure
        - Unsafe dependencies

        Rate severity: critical, high, medium, low

        Return JSON: {
          "vulnerabilities": [
            {"type": "...", "severity": "...", "location": "...", "recommendation": "..."}
          ]
        }
      outputs:
        - name: "security_findings"
          type: "object"

    - id: "code_quality_review"
      name: "Code Quality Review"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.3
      depends_on: ["fetch_code"]
      prompt: |
        Review code quality and best practices:

        {{steps.fetch_code.outputs.changed_files}}

        Evaluate:
        - Code style and consistency
        - Error handling
        - Code duplication
        - Function complexity
        - Naming conventions
        - Comments and documentation

        Provide:
        - Issues found
        - Suggestions for improvement
        - Overall quality score (1-10)

        Return as JSON
      outputs:
        - name: "quality_review"
          type: "object"

    - id: "performance_analysis"
      name: "Performance Analysis"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.2
      depends_on: ["fetch_code"]
      prompt: |
        Analyze potential performance impacts:

        {{steps.fetch_code.outputs.changed_files}}

        Identify:
        - Inefficient algorithms
        - Resource leaks
        - Blocking operations
        - Database query optimization opportunities

        Return JSON with findings and recommendations
      outputs:
        - name: "performance_findings"
          type: "object"

    - id: "critical_issues_check"
      name: "Check for Critical Issues"
      type: "expression"
      depends_on: ["security_review", "code_quality_review"]
      expression: |
        {{steps.security_review.outputs.security_findings.vulnerabilities |
          filter(severity='critical') | length > 0 OR
          steps.code_quality_review.outputs.quality_review.overall_quality < 5}}
      outputs:
        - name: "has_critical_issues"
          type: "boolean"

    - id: "block_merge"
      name: "Block Merge - Critical Issues"
      type: "action"
      action: "block_pr_merge"
      depends_on: ["critical_issues_check"]
      condition: "{{steps.critical_issues_check.outputs.has_critical_issues == true}}"
      params:
        reason: |
          Critical issues found:
          Security: {{steps.security_review.outputs.security_findings}}
          Quality: {{steps.code_quality_review.outputs.quality_review}}

    - id: "generate_function_docs"
      name: "Generate Function Documentation"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.4
      depends_on: ["fetch_code"]
      condition: "{{review_depth == 'thorough'}}"
      prompt: |
        Generate comprehensive documentation for each function:

        {{steps.fetch_code.outputs.changed_files}}

        For each function include:
        - Purpose and description
        - Parameters with types
        - Return value
        - Exceptions raised
        - Usage examples
        - Time/space complexity if relevant

        Use appropriate doc string format for the language
      outputs:
        - name: "function_docs"

    - id: "generate_readme_updates"
      name: "Suggest README Updates"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.5
      depends_on: ["analyze_changes", "generate_function_docs"]
      condition: "{{steps.analyze_changes.outputs.change_analysis.new_features | length > 0}}"
      prompt: |
        Based on these new features:
        {{steps.analyze_changes.outputs.change_analysis.new_features}}

        And function documentation:
        {{steps.generate_function_docs.outputs.function_docs}}

        Suggest updates to README.md including:
        - Feature descriptions
        - Usage examples
        - API changes
        - Migration guide if needed
      outputs:
        - name: "readme_suggestions"

    - id: "generate_changelog"
      name: "Generate Changelog Entry"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.4
      depends_on: ["analyze_changes"]
      prompt: |
        Create a changelog entry for these changes:

        {{steps.analyze_changes.outputs.change_analysis}}

        Format:
        ## [Version] - Date

        ### Added
        - ...

        ### Changed
        - ...

        ### Fixed
        - ...

        ### Security
        - ...
      outputs:
        - name: "changelog_entry"

    - id: "compile_review_report"
      name: "Compile Review Report"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.3
      depends_on:
        - "security_review"
        - "code_quality_review"
        - "performance_analysis"
        - "generate_changelog"
      prompt: |
        Create a comprehensive code review report:

        Security: {{steps.security_review.outputs.security_findings}}
        Quality: {{steps.code_quality_review.outputs.quality_review}}
        Performance: {{steps.performance_analysis.outputs.performance_findings}}

        Structure:
        1. Executive Summary
        2. Overall Assessment (Approve/Request Changes/Reject)
        3. Detailed Findings by Category
        4. Action Items
        5. Recommendations

        Changelog:
        {{steps.generate_changelog.outputs.changelog_entry}}
      outputs:
        - name: "review_report"

    - id: "post_review"
      name: "Post Review to PR"
      type: "action"
      action: "post_pr_comment"
      depends_on: ["compile_review_report"]
      params:
        repo: "{{repo_url}}"
        branch: "{{branch}}"
        comment: "{{steps.compile_review_report.outputs.review_report}}"
      outputs:
        - name: "comment_id"
```

---

## Summary

This guide provides a comprehensive framework for implementing YAML-based workflow automation for LLM chaining and multi-step AI tasks, including:

1. **Multiple Schema Approaches**: Semantic Kernel, Swarms, txtai, and custom schemas
2. **Variable Management**: Template substitution, nested access, scoping, and dynamic assignment
3. **Control Flow**: Conditions, loops, state machines, and multi-agent delegation
4. **Human Interaction**: Approval gates, input collection, batch review, and iterative refinement
5. **Error Handling**: Retries, fallbacks, validation gates, compensation actions, and circuit breakers
6. **State Management**: Persistence, checkpoints, recovery, and distributed synchronization
7. **Implementation Architecture**: Parser, variable substitution engine, executor, and LLM client
8. **Practical Examples**: Real-world workflows for research, support, content, and code review

The modular architecture allows you to mix and match components based on your specific needs while maintaining flexibility and extensibility.

---

## Sources and References

- [Swarms Framework Documentation](https://docs.swarms.world/en/latest/swarms/agents/create_agents_yaml/)
- [Microsoft Semantic Kernel YAML Schema](https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/yaml-schema)
- [Azure Logic Apps Multi-Agent Workflows](https://learn.microsoft.com/en-us/azure/logic-apps/create-agent-workflows)
- [Azure Logic Apps Prompt Chaining](https://azure.github.io/logicapps-labs/docs/logicapps-ai-course/build_multi_agent_systems/prompt-chaining/)
- [AWS Prompt Chaining Workflow](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-prompt-chaining.html)
- [LangChain Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [n8n AI Agent Workflows](https://blog.n8n.io/ai-agentic-workflows/)
- [AutoGen Multi-Agent Workflows](https://microsoft.github.io/autogen/0.2/docs/Use-Cases/agent_chat/)
- [StateFlow: State-Driven Workflows](https://arxiv.org/html/2403.11322v1)
