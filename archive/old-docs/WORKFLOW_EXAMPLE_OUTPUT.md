# Workflow Execution Examples - Sample Output

## Example 1: Code Review Workflow Execution

### User Input:
```
Select workflow [1-4]: 1

Workflow Variables:
code: def calculate_average(numbers):
    return sum(numbers) / len(numbers)

language: python

Execute workflow? [Y/n]: Y
```

### Execution Output:
```
Starting workflow execution...

============================================================

Step 1/3: review_code
  Type: prompt
  Executing model: Qwen3 Coder 30B Q4_K_M

[Model processing... 15 seconds]

Step 2/3: suggest_improvements
  Type: prompt
  Executing model: Qwen3 Coder 30B Q4_K_M

[Model processing... 12 seconds]

Step 3/3: generate_improved_code
  Type: prompt
  Executing model: Qwen3 Coder 30B Q4_K_M

[Model processing... 18 seconds]

============================================================

✓ Workflow completed successfully!

Workflow Results:

Step: review_code
Issues found:
1. No input validation - empty list will cause ZeroDivisionError
2. No type checking - non-numeric values will cause TypeError
3. Missing docstring
4. No error handling
Security: LOW RISK
Performance: GOOD (O(n) complexity)

Step: suggest_improvements
Priority fixes:
1. Add check for empty list before division
2. Validate all elements are numbers
3. Add comprehensive error handling
4. Include type hints for better code clarity
5. Add docstring with usage examples

Step: generate_improved_code
def calculate_average(numbers: list[float]) -> float:
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: List of numeric values

    Returns:
        The arithmetic mean of the numbers

    Raises:
        ValueError: If list is empty or contains non-numeric values
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")

    try:
        return sum(numbers) / len(numbers)
    except TypeError:
        raise ValueError("All elements must be numeric")

Results saved to: D:\models\outputs\workflow_code_review_workflow_20251208_220530.json
Execution time: 45.23 seconds
```

---

## Example 2: Research Workflow Execution

### User Input:
```
Select workflow [1-4]: 2

Workflow Variables:
topic: Quantum Machine Learning

Execute workflow? [Y/n]: Y
```

### Execution Output:
```
Starting workflow execution...

============================================================

Step 1/3: quick_overview
  Type: prompt
  Executing model: Llama 3.3 70B Instruct Q4_K_M

[Model processing... 8 seconds]

Step 2/3: deep_analysis
  Type: prompt
  Executing model: Phi-4 14B Q4_K_M

[Model processing... 25 seconds]

Step 3/3: create_summary
  Type: prompt
  Executing model: Qwen3 Coder 30B Q4_K_M

[Model processing... 12 seconds]

============================================================

✓ Workflow completed successfully!

Workflow Results:

Step: quick_overview
Quantum Machine Learning (QML) is an emerging interdisciplinary field that combines quantum computing with machine learning algorithms. It leverages quantum mechanics principles like superposition and entanglement to potentially solve...

Step: deep_analysis
TECHNICAL DETAILS:
Quantum machine learning utilizes quantum circuits as computational graphs, where quantum gates perform transformations on quantum states. Key algorithms include:

1. Variational Quantum Eigensolver (VQE)
2. Quantum Approximate Optimization Algorithm (QAOA)
3. Quantum Neural Networks (QNN)

Current research focuses on near-term algorithms compatible with NISQ (Noisy Intermediate-Scale Quantum) devices...

CURRENT STATE OF THE ART:
Leading research institutions (IBM, Google, Microsoft) have demonstrated quantum advantage in specific ML tasks...

Step: create_summary
# Quantum Machine Learning: Comprehensive Research Summary

## Introduction
Quantum Machine Learning represents the convergence of quantum computing and artificial intelligence, offering potential exponential speedups for specific computational tasks...

## Technical Overview
[Full markdown document with sections on theory, applications, challenges, future directions]

Results saved to: D:\models\outputs\workflow_research_workflow_20251208_220715.json
Execution time: 45.67 seconds
```

---

## Example 3: Advanced Code Analysis with Conditionals

### User Input:
```
Select workflow [1-4]: 4

Workflow Variables:
code:
def login(username, password):
    query = "SELECT * FROM users WHERE name='" + username + "'"
    db.execute(query)

language: python
analysis_type: general

Execute workflow? [Y/n]: Y
```

### Execution Output:
```
Starting workflow execution...

============================================================

Step 1/6: initial_scan
  Type: prompt
  Executing model: Qwen3 Coder 30B Q4_K_M

[Model processing... 10 seconds]

Step 2/6: extract_security_flag
  Type: extract
  Extracted text matching pattern from 'initial_scan': yes

Step 3/6: extract_performance_flag
  Type: extract
  Extracted text matching pattern from 'initial_scan': no

Step 4/6: security_audit
  Type: conditional
  Condition '{{has_security_issues}} == yes' evaluated to TRUE, executing 'then' branch
  Executing model: Qwen3 Coder 30B Q4_K_M

[Model processing... 20 seconds]

Step 5/6: performance_optimization
  Type: conditional
  Condition '{{has_performance_issues}} == yes' evaluated to FALSE, no 'else' branch defined

Step 6/6: final_recommendations
  Type: prompt
  Executing model: Phi-4 14B Q4_K_M

[Model processing... 15 seconds]

============================================================

✓ Workflow completed successfully!

Workflow Results:

Step: initial_scan
Security Concerns: yes
Performance Issues: no
Quality Rating: 2/10
Brief Summary: Code contains critical SQL injection vulnerability. String concatenation used for database query construction.

Step: extract_security_flag
yes

Step: extract_performance_flag
no

Step: security_audit
CRITICAL SECURITY VULNERABILITIES:

1. SQL INJECTION (CRITICAL):
   - Line 2: Direct string concatenation in SQL query
   - Attacker can inject: username = "' OR '1'='1"
   - This bypasses authentication entirely

2. MISSING INPUT VALIDATION:
   - No validation of username/password format
   - No length restrictions

3. PASSWORD HANDLING:
   - Plain text password comparison (assumed)
   - No hashing visible in code

REMEDIATION STEPS:
1. Use parameterized queries immediately
2. Implement prepared statements
3. Add input validation and sanitization
4. Hash passwords with bcrypt/argon2
5. Implement rate limiting for login attempts

Step: performance_optimization
None

Step: final_recommendations
EXECUTIVE SUMMARY:
The code contains a CRITICAL security vulnerability (SQL injection) that must be fixed immediately before deployment.

PRIORITY ACTION ITEMS:
1. [URGENT] Replace string concatenation with parameterized queries
2. [URGENT] Implement password hashing
3. [HIGH] Add input validation
4. [MEDIUM] Implement rate limiting
5. [MEDIUM] Add logging for security events

LONG-TERM IMPROVEMENTS:
- Use ORM framework (SQLAlchemy)
- Implement 2FA
- Add comprehensive error handling
- Security audit before production

CODE QUALITY CHECKLIST:
□ Security review - FAILED (SQL injection)
□ Input validation - MISSING
□ Error handling - MISSING
□ Documentation - MISSING
✓ Performance - ACCEPTABLE

Results saved to: D:\models\outputs\workflow_advanced_code_analysis_20251208_220845.json
Execution time: 55.34 seconds
```

---

## Example 4: Batch Questions Workflow

### User Input:
```
Select workflow [1-4]: 3

Workflow Variables:
questions (list):
  Item 1: What is machine learning?
  Item 2: How does deep learning differ from traditional ML?
  Item 3: What are common ML algorithms?
  Item 4:
  [empty line - finished entering items]

Execute workflow? [Y/n]: Y
```

### Execution Output:
```
Starting workflow execution...

============================================================

Step 1/2: process_questions
  Type: loop
  Looping over 3 items from variable 'questions'

  Loop iteration 1/3: question = What is machine learning?
  Executing model: Phi-4 14B Q4_K_M
  [Model processing... 8 seconds]

  Loop iteration 2/3: question = How does deep learning differ from traditional ML?
  Executing model: Qwen3 Coder 30B Q4_K_M
  [Model processing... 10 seconds]

  Loop iteration 3/3: question = What are common ML algorithms?
  Executing model: Llama 3.3 70B Instruct Q4_K_M
  [Model processing... 7 seconds]

Step 2/2: summarize_all
  Type: prompt
  Executing model: Phi-4 14B Q4_K_M

[Model processing... 15 seconds]

============================================================

✓ Workflow completed successfully!

Workflow Results:

Step: process_questions
[
  "Machine learning is a subset of AI where computers learn patterns from data...",
  "Deep learning uses neural networks with multiple layers, unlike traditional ML...",
  "Common algorithms include: Linear Regression, Decision Trees, Random Forests..."
]

Step: summarize_all
COMMON THEMES:
The questions explore fundamental machine learning concepts, progressing from basic definitions to specific implementations.

KEY INSIGHTS:
1. Machine learning enables computers to learn without explicit programming
2. Deep learning represents an evolution of ML using neural architectures
3. Various algorithms suit different problem types (regression, classification, etc.)

RELATIONSHIPS:
- Deep learning builds upon traditional ML foundations
- Algorithm selection depends on data characteristics and problem domain
- All approaches share common goal: pattern recognition and prediction

OVERALL CONCLUSIONS:
Machine learning encompasses a spectrum of techniques from simple statistical methods to complex neural networks, each with specific use cases and trade-offs.

Results saved to: D:\models\outputs\workflow_batch_questions_20251208_221015.json
Execution time: 40.18 seconds
```

---

## Example 5: Workflow Validation

### User Input:
```
Select option [0-4]: 4

Enter path to workflow YAML file: D:\models\workflows\code_review_workflow.yaml
```

### Validation Output:
```
Validating workflow...

✓ Workflow is valid!

Workflow Details:
  ID: code_review_workflow
  Name: Code Review and Improvement Workflow
  Steps: 3
  Variables: 2

Steps:
  1. review_code (prompt)
  2. suggest_improvements (prompt)
     Depends on: review_code
  3. generate_improved_code (prompt)
     Depends on: suggest_improvements
```

---

## Example 6: Workflow List Display

### User Input:
```
Select option [0-4]: 2
```

### Output:
```
╔══════════════════════════════════════════════════════════════╗
║  AVAILABLE WORKFLOWS                                         ║
╚══════════════════════════════════════════════════════════════╝

Code Review and Improvement Workflow
  ID: code_review_workflow
  File: code_review_workflow.yaml
  Steps: 3
  Description: Reviews code, suggests improvements, then generates improved version

Multi-Model Research Workflow
  ID: research_workflow
  File: research_workflow.yaml
  Steps: 3
  Description: Uses multiple models to research a topic comprehensively

Batch Question Processing with Extraction
  ID: batch_questions
  File: batch_questions_workflow.yaml
  Steps: 2
  Description: Process multiple questions and extract key insights

Advanced Code Analysis with Conditional Logic
  ID: advanced_code_analysis
  File: advanced_code_analysis.yaml
  Steps: 6
  Description: Analyzes code and conditionally performs security audit or performance optimization
```

---

## Example 7: Creating New Workflow from Template

### User Input:
```
Select option [0-4]: 3

Workflow Templates:
[1] Code Review Workflow
[2] Research Workflow
[3] Batch Questions Workflow
[4] Advanced Code Analysis Workflow
[5] Custom (blank template)

Select template [1-5]: 5

Enter workflow name: my_custom_workflow
```

### Output:
```
✓ Blank workflow created: D:\models\workflows\my_custom_workflow.yaml
Edit the file to add your steps.
```

### Created File Content:
```yaml
id: my_workflow
name: "My Custom Workflow"
description: "Description of what this workflow does"

variables:
  input_var: ""  # Define your variables here

steps:
  - name: step_1
    type: prompt
    model: auto
    prompt: |
      Your prompt here using {{input_var}}
    output_var: result_1
    on_error: continue

  # Add more steps as needed
```

---

## JSON Output File Example

**File:** `D:\models\outputs\workflow_code_review_workflow_20251208_220530.json`

```json
{
  "workflow_id": "code_review_workflow",
  "workflow_name": "Code Review and Improvement Workflow",
  "status": "completed",
  "results": {
    "review_code": "Issues found:\n1. No input validation - empty list will cause ZeroDivisionError\n2. No type checking - non-numeric values will cause TypeError\n3. Missing docstring\n4. No error handling\nSecurity: LOW RISK\nPerformance: GOOD (O(n) complexity)",
    "suggest_improvements": "Priority fixes:\n1. Add check for empty list before division\n2. Validate all elements are numbers\n3. Add comprehensive error handling\n4. Include type hints for better code clarity\n5. Add docstring with usage examples",
    "generate_improved_code": "def calculate_average(numbers: list[float]) -> float:\n    \"\"\"\n    Calculate the average of a list of numbers.\n    \n    Args:\n        numbers: List of numeric values\n        \n    Returns:\n        The arithmetic mean of the numbers\n        \n    Raises:\n        ValueError: If list is empty or contains non-numeric values\n    \"\"\"\n    if not numbers:\n        raise ValueError(\"Cannot calculate average of empty list\")\n    \n    try:\n        return sum(numbers) / len(numbers)\n    except TypeError:\n        raise ValueError(\"All elements must be numeric\")"
  },
  "variables": {
    "code": "def calculate_average(numbers):\n    return sum(numbers) / len(numbers)",
    "language": "python"
  },
  "start_time": "2025-12-08T22:05:00.123456",
  "end_time": "2025-12-08T22:05:45.357890",
  "duration_seconds": 45.234434,
  "error_message": null
}
```

---

## Error Handling Examples

### Example: Failed Workflow (Model Not Found)

```
Step 1/3: analyze_code
  Type: prompt

✗ Workflow failed: Model 'invalid-model-id' not found in available models
Check the logs for more details.

Partial results saved to: D:\models\outputs\workflow_code_review_workflow_20251208_221200_failed.json
```

### Example: Step Error with Continue

```
Step 2/3: optional_analysis
  Type: prompt
  Error in step optional_analysis: Connection timeout (continuing)

Step 3/3: final_summary
  Type: prompt
  Executing model: Phi-4 14B Q4_K_M

[Continues with next step...]
```

---

## Performance Metrics

### Typical Execution Times:

- **Simple workflow (2-3 steps):** 30-60 seconds
- **Complex workflow (4-6 steps):** 60-120 seconds
- **Batch processing (loops):** 10-20 seconds per iteration
- **Variable substitution:** <1ms per substitution
- **Workflow loading:** <100ms
- **Validation:** <50ms per workflow

### Model Speed Comparison (tokens/second):
- Llama 3.3 70B: ~10-15 tok/sec
- Phi-4 14B: ~20-30 tok/sec
- Qwen3 Coder 30B: ~25-35 tok/sec

---

This demonstrates the complete workflow system in action with realistic examples and outputs.
