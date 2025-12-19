# YAML Workflow Examples

This directory contains practical YAML workflow examples demonstrating various patterns for LLM-based automation and multi-step AI tasks.

## Examples Overview

### 1. Simple Chain (`simple_chain.yaml`)
**Difficulty:** Beginner
**Use Case:** Basic sequential prompt chaining

Demonstrates:
- Sequential LLM calls
- Variable passing between steps
- Step dependencies
- Basic prompt templating

**Workflow:**
```
Research → Expand → Add Examples → Format
```

**Key Learning Points:**
- How to reference outputs from previous steps
- Using template variables
- Building simple sequential workflows

---

### 2. Conditional Flow (`conditional_flow.yaml`)
**Difficulty:** Intermediate
**Use Case:** Content routing with conditional branching

Demonstrates:
- Content classification
- Conditional execution
- Multiple execution paths
- Quality-based branching

**Workflow:**
```
Classify → Assess Quality
              ├─ High Quality → Enhance
              └─ Low Quality → Major Revision
                                  ↓
                            Category-Specific Processing
                                  ↓
                            Final Validation
```

**Key Learning Points:**
- Writing conditional expressions
- Branch-based workflow design
- Category-specific processing
- OR conditions for step inputs

---

### 3. Human-in-the-Loop (`human_in_loop.yaml`)
**Difficulty:** Intermediate
**Use Case:** Email campaign creation with approvals

Demonstrates:
- User confirmation steps
- User input collection
- Batch review patterns
- Iterative refinement with feedback
- Approval workflows

**Workflow:**
```
Generate Strategy → User Approval
                      ├─ Approved → Write Emails → Batch Review → Deploy
                      └─ Rejected → Collect Feedback → Revise → Retry
```

**Key Learning Points:**
- Adding approval gates
- Collecting structured user input
- Handling user feedback
- Batch review patterns
- Setting timeouts for human tasks

---

### 4. Error Handling (`error_handling.yaml`)
**Difficulty:** Advanced
**Use Case:** Data extraction with comprehensive error recovery

Demonstrates:
- Retry logic with backoff
- Fallback strategies
- Validation gates
- Iterative error correction
- Compensation actions
- Circuit breaker pattern

**Workflow:**
```
Fetch Data (with retries)
    ├─ Success → Parse → Validate
    ├─ Retry Failed → Fallback Source
    └─ All Failed → Cached Data
                        ↓
                   Validation Failed? → Auto-fix → Revalidate
                        ↓
                   Enrich → Quality Check → Save (with rollback)
```

**Key Learning Points:**
- Implementing retry mechanisms
- Fallback chain patterns
- Automated error correction
- Quality gates and validation
- Database transaction rollback

---

### 5. State Machine (`state_machine.yaml`)
**Difficulty:** Advanced
**Use Case:** Document approval process

Demonstrates:
- State-based workflow execution
- State transitions with conditions
- Timeout handling
- Escalation patterns
- Complex approval workflows

**States:**
```
SUBMITTED → INITIAL_REVIEW
              ├─ Pass → AWAITING_APPROVAL
              │           ├─ Approved → APPROVED (terminal)
              │           ├─ Changes → CHANGES_REQUESTED → REVISION_IN_PROGRESS
              │           └─ Timeout → ESCALATED
              └─ Fail → REJECTED
                          ├─ Resubmit → RESUBMITTED → INITIAL_REVIEW
                          └─ Cancel → CANCELLED (terminal)
```

**Key Learning Points:**
- State machine design patterns
- Transition conditions
- Timeout and escalation
- Terminal states
- State persistence and recovery

---

## How to Use These Examples

### 1. Understanding the Structure

All examples follow the same basic YAML structure:

```yaml
workflow:
  name: "Workflow Name"
  version: "1.0"
  description: "What this workflow does"

  variables:
    # Global workflow variables

  steps:
    # Workflow steps
```

### 2. Running Workflows

To execute these workflows with the provided executor:

```python
from workflow_parser import WorkflowParser
from workflow_executor import WorkflowExecutor
from llm_client import LLMClient

# Parse workflow
parser = WorkflowParser()
workflow = parser.parse_file('workflow_examples/simple_chain.yaml')

# Validate
errors = parser.validate_workflow(workflow)
if errors:
    print(f"Validation errors: {errors}")
    exit(1)

# Execute
llm_client = LLMClient(default_provider="openai")
executor = WorkflowExecutor(llm_client)

result = await executor.execute(workflow, initial_vars={
    'user_query': 'What are the benefits of renewable energy?'
})

print(f"Workflow completed: {result}")
```

### 3. Modifying Examples

Each example can be customized by:

**Changing Variables:**
```yaml
variables:
  topic: "Your custom topic"
  temperature: 0.8  # Increase creativity
```

**Updating Prompts:**
```yaml
steps:
  - id: "my_step"
    prompt: |
      Your custom prompt here
      Using variables: {{variable_name}}
```

**Adding Steps:**
```yaml
steps:
  # ... existing steps ...

  - id: "new_step"
    name: "My New Step"
    type: "llm_call"
    depends_on: ["previous_step"]
    prompt: "Process {{steps.previous_step.outputs.result}}"
```

### 4. Testing Workflows

Use the executor's test mode:

```python
# Test with sample data
test_inputs = {
    'topic': 'AI ethics',
    'target_audience': 'general public'
}

result = await executor.execute(workflow, initial_vars=test_inputs)

# Check outputs
for step_id, step_result in result['results'].items():
    print(f"{step_id}: {step_result.status}")
    print(f"  Outputs: {step_result.outputs}")
```

## Pattern Reference

### Variable Substitution
```yaml
# Simple variable
{{variable_name}}

# Step output
{{steps.step_id.outputs.output_name}}

# Nested object
{{steps.step_id.outputs.data.field.subfield}}

# Global variable
{{variables.name}}
```

### Conditions
```yaml
# Simple comparison
condition: "{{value >= 5}}"

# Boolean logic
condition: "{{approved == true AND score > 7}}"

# Complex expression
condition: |
  {{steps.quality.outputs.score >= 8 AND
    steps.validation.outputs.passed == true OR
    steps.override.outputs.force_approve == true}}
```

### Dependencies
```yaml
# Single dependency
depends_on: ["previous_step"]

# Multiple dependencies
depends_on: ["step1", "step2", "step3"]

# All dependencies must complete before this step runs
```

### Error Handling
```yaml
error_handling:
  retry:
    max_attempts: 3
    backoff: "exponential"
  on_error: "fallback_step"
  on_max_retries: "notify_admin"
```

## Common Patterns

### 1. Validation Gate
```yaml
- id: "validate"
  type: "validation"
  validator: "schema_validator"
  input: "{{steps.generate.outputs.data}}"

- id: "fix_if_invalid"
  condition: "{{steps.validate.outputs.is_valid == false}}"
  type: "llm_call"
  prompt: "Fix these errors: {{steps.validate.outputs.errors}}"
```

### 2. Approval Loop
```yaml
- id: "generate"
  type: "llm_call"

- id: "review"
  type: "user_confirmation"
  depends_on: ["generate"]

- id: "revise"
  condition: "{{steps.review.outputs.approved == false}}"
  type: "llm_call"
  max_iterations: 3
```

### 3. Parallel Processing
```yaml
- id: "analyze_sentiment"
  depends_on: ["fetch_data"]

- id: "extract_entities"
  depends_on: ["fetch_data"]

- id: "summarize"
  depends_on: ["fetch_data"]

# All three run in parallel after fetch_data

- id: "combine_results"
  depends_on: ["analyze_sentiment", "extract_entities", "summarize"]
```

### 4. Retry with Fallback
```yaml
- id: "primary"
  error_handling:
    retry:
      max_attempts: 3
    on_max_retries: "secondary"

- id: "secondary"
  error_handling:
    on_error: "use_default"

- id: "use_default"
  type: "static_response"
  content: "Default response"
```

## Best Practices

### 1. Naming Conventions
- **Step IDs:** Use snake_case (e.g., `analyze_sentiment`)
- **Variable names:** Use snake_case (e.g., `target_audience`)
- **Step names:** Use Title Case (e.g., "Analyze Sentiment")

### 2. Prompt Design
- Be specific and clear
- Include examples in prompts
- Use structured output formats (JSON)
- Reference previous outputs explicitly

### 3. Error Handling
- Always add retry logic for external API calls
- Implement fallback strategies
- Add validation after generation steps
- Log errors for debugging

### 4. Performance
- Minimize sequential dependencies
- Use parallel execution where possible
- Cache expensive operations
- Set appropriate timeouts

### 5. Maintainability
- Add descriptive step names
- Document complex conditions
- Use meaningful variable names
- Keep prompts in the YAML for transparency

## Troubleshooting

### Common Issues

**Issue:** "Step depends on non-existent step"
```yaml
# Wrong:
depends_on: ["typo_step_name"]

# Correct:
depends_on: ["actual_step_id"]
```

**Issue:** "Circular dependency detected"
```yaml
# Wrong:
step1:
  depends_on: ["step2"]
step2:
  depends_on: ["step1"]

# Correct: Remove circular reference
```

**Issue:** "Variable not found"
```yaml
# Wrong:
prompt: "{{undefined_variable}}"

# Correct: Define in variables section or reference step output
variables:
  defined_variable: "value"
```

**Issue:** "Condition always evaluates to false"
```yaml
# Wrong:
condition: "{{steps.check.outputs.value = 5}}"  # Single =

# Correct:
condition: "{{steps.check.outputs.value == 5}}"  # Double ==
```

## Advanced Topics

### Custom Validators
Create custom validation functions:

```python
def custom_validator(input_data, schema):
    # Your validation logic
    return is_valid, errors
```

### Custom Actions
Extend the executor with custom actions:

```python
async def custom_action(params):
    # Your action logic
    return result

executor.register_action('custom_action', custom_action)
```

### Workflow Composition
Combine multiple workflows:

```yaml
- id: "call_subworkflow"
  type: "workflow_call"
  workflow: "data_processing.yaml"
  inputs:
    data: "{{steps.fetch.outputs.raw_data}}"
```

## Resources

- [Main Guide](../llm_workflow_yaml_guide.md) - Comprehensive documentation
- [Workflow Builder UI](../workflow_builder_ui_spec.md) - Visual builder specification
- [Parser Implementation](../workflow_parser.py) - Reference implementation
- [Executor Implementation](../workflow_executor.py) - Execution engine

## Contributing

To add new examples:

1. Create a new `.yaml` file in this directory
2. Follow the established structure
3. Document the use case and key learning points
4. Add to this README with description

## License

These examples are provided as educational resources and can be freely modified and used in your projects.
