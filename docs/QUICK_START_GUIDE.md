# YAML Workflow Quick Start Guide

Get started with YAML-based LLM workflows in 5 minutes.

## Installation

```bash
# Install dependencies
pip install pyyaml openai anthropic jinja2

# Or use requirements.txt
pip install -r requirements.txt
```

## Your First Workflow (3 minutes)

### Step 1: Create workflow file `hello.yaml`

```yaml
workflow:
  name: "HelloWorkflow"
  version: "1.0"
  description: "My first LLM workflow"

  variables:
    topic: "artificial intelligence"

  steps:
    - id: "generate"
      name: "Generate Content"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.7
      prompt: |
        Write a brief explanation of {{topic}} for beginners.
        Keep it simple and engaging.
      outputs:
        - name: "explanation"
```

### Step 2: Execute with Python

```python
# run_workflow.py
import asyncio
from workflow_parser import WorkflowParser
from workflow_executor import WorkflowExecutor
from llm_client import LLMClient

async def main():
    # Parse
    parser = WorkflowParser()
    workflow = parser.parse_file('hello.yaml')

    # Execute
    llm_client = LLMClient(openai_api_key="your-key-here")
    executor = WorkflowExecutor(llm_client)

    result = await executor.execute(workflow, initial_vars={
        'topic': 'machine learning'
    })

    print(result['results']['generate'].outputs['explanation'])

asyncio.run(main())
```

### Step 3: Run it

```bash
python run_workflow.py
```

## Common Patterns

### 1. Sequential Steps

```yaml
steps:
  - id: "step1"
    prompt: "Research {{topic}}"
    outputs:
      - name: "research"

  - id: "step2"
    depends_on: ["step1"]
    prompt: |
      Based on this research:
      {{steps.step1.outputs.research}}

      Write a summary.
    outputs:
      - name: "summary"
```

### 2. Conditional Execution

```yaml
steps:
  - id: "check"
    prompt: "Rate quality from 1-10: {{content}}"
    outputs:
      - name: "score"

  - id: "approve"
    condition: "{{steps.check.outputs.score >= 8}}"
    prompt: "Content approved!"

  - id: "revise"
    condition: "{{steps.check.outputs.score < 8}}"
    prompt: "Revise: {{content}}"
```

### 3. User Approval

```yaml
steps:
  - id: "generate"
    prompt: "Create draft: {{topic}}"
    outputs:
      - name: "draft"

  - id: "review"
    type: "user_confirmation"
    depends_on: ["generate"]
    message: |
      Review this draft:
      {{steps.generate.outputs.draft}}

      Approve?
    outputs:
      - name: "approved"

  - id: "publish"
    condition: "{{steps.review.outputs.approved == true}}"
    prompt: "Format for publication"
```

### 4. Error Handling

```yaml
steps:
  - id: "main"
    prompt: "Process {{data}}"
    error_handling:
      retry:
        max_attempts: 3
        backoff: "exponential"
      on_error: "fallback"

  - id: "fallback"
    prompt: "Use simplified approach"
```

## Variable Reference

```yaml
# Global variable
{{my_variable}}

# Step output
{{steps.step_id.outputs.output_name}}

# Nested data
{{steps.step_id.outputs.data.field.subfield}}

# In conditions
condition: "{{value >= 5}}"
condition: "{{approved == true AND score > 7}}"
```

## Testing

```python
# Test with different inputs
test_cases = [
    {'topic': 'AI', 'audience': 'beginners'},
    {'topic': 'ML', 'audience': 'experts'},
]

for test_vars in test_cases:
    result = await executor.execute(workflow, initial_vars=test_vars)
    print(f"Test {test_vars}: {result['status']}")
```

## Next Steps

1. **Try Examples**
   - See `workflow_examples/` for 5 complete workflows
   - Start with `simple_chain.yaml`

2. **Read Documentation**
   - Full guide: `llm_workflow_yaml_guide.md`
   - Implementation: `workflow_implementation_guide.md`

3. **Customize**
   - Modify examples for your use case
   - Add custom actions
   - Build your workflow library

## Common Issues

**Issue:** "Step depends on non-existent step"
```yaml
# Fix: Check step ID spelling
depends_on: ["correct_step_id"]
```

**Issue:** "Variable not found"
```yaml
# Fix: Define in variables section
variables:
  my_var: "value"
```

**Issue:** "Circular dependency"
```yaml
# Fix: Remove circular reference
# step1 depends on step2, step2 depends on step1 = ERROR
```

## Cheat Sheet

### Step Types
- `llm_call` - Call LLM
- `user_confirmation` - Get approval
- `user_input` - Collect data
- `validation` - Validate output
- `action` - Custom action
- `expression` - Calculate value

### Condition Operators
- `==` Equal
- `!=` Not equal
- `>`, `<`, `>=`, `<=` Comparison
- `AND`, `OR`, `NOT` Logic

### Template Syntax
- `{{variable}}` - Insert variable
- `{{steps.id.outputs.name}}` - Step output
- Works in prompts and conditions

## Example Templates

### Content Generation
```yaml
workflow:
  name: "ContentGen"
  steps:
    - id: "outline"
      prompt: "Create outline for: {{topic}}"
    - id: "draft"
      depends_on: ["outline"]
      prompt: "Write draft from: {{steps.outline.outputs.content}}"
    - id: "polish"
      depends_on: ["draft"]
      prompt: "Polish: {{steps.draft.outputs.content}}"
```

### Data Analysis
```yaml
workflow:
  name: "DataAnalysis"
  steps:
    - id: "extract"
      prompt: "Extract data from: {{source}}"
    - id: "analyze"
      depends_on: ["extract"]
      prompt: "Analyze: {{steps.extract.outputs.data}}"
    - id: "visualize"
      depends_on: ["analyze"]
      prompt: "Create visualization for: {{steps.analyze.outputs.insights}}"
```

### Q&A Pipeline
```yaml
workflow:
  name: "QnA"
  steps:
    - id: "understand"
      prompt: "Clarify this question: {{question}}"
    - id: "research"
      depends_on: ["understand"]
      prompt: "Research: {{steps.understand.outputs.clarified}}"
    - id: "answer"
      depends_on: ["research"]
      prompt: "Answer based on: {{steps.research.outputs.findings}}"
```

## Resources

- **Full Documentation**: `llm_workflow_yaml_guide.md`
- **Examples**: `workflow_examples/`
- **UI Spec**: `workflow_builder_ui_spec.md`
- **Implementation**: `workflow_implementation_guide.md`

## Support

For questions or issues:
1. Check the examples in `workflow_examples/`
2. Read the troubleshooting section in examples README
3. Review the full guide for advanced patterns

---

**Happy workflow building!** 🚀
