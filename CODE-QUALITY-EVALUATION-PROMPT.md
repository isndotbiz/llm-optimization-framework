# Code Quality Evaluation & Tool Recommendation Prompt

## System Context
You are a code quality expert evaluating a Python project for code health and recommending open source tools to improve it.

## Project Overview
The following Python files are part of an AI Router system - intelligent model selection and execution framework for:
- RTX 3090 GPU (WSL environment)
- MacBook M4 Pro (MLX framework)
- TrueNAS systems (RTX 4060 Ti)

Files to analyze:
1. `ai-router.py` - Main CLI router
2. `ai-router-enhanced.py` - Project/bot/memory management edition
3. `ai-router-mlx.py` - MacBook M4 optimized version
4. `ai-router-truenas.py` - TrueNAS edition with REST API
5. `ai-router-truenas-production.py` - Production TrueNAS edition

## Code Categories to Evaluate

Analyze the provided code for issues in these categories:

### 1. Syntax & Style Errors
- Code structure and formatting compliance
- PEP 8 compliance (already fixed with flake8)
- Comment quality and coverage
- Code organization and structure

### 2. Runtime Errors & Exception Handling
- Unhandled exceptions
- Try/catch block coverage
- Error propagation and logging
- File I/O error handling
- Subprocess execution error handling
- API/Network request error handling

### 3. Type Safety & Type Hints
- Missing type annotations
- Type consistency
- Optional type handling
- Generic type usage
- Type hint coverage percentage

### 4. Logic Errors
- Off-by-one errors
- Infinite loops or recursion
- Unreachable code paths
- Logic inconsistencies
- Default value problems

### 5. Security Vulnerabilities
- Command injection risks (subprocess usage)
- Path traversal vulnerabilities
- Hardcoded secrets or credentials
- Input validation gaps
- Unsafe deserialization
- OWASP Top 10 risks for this context

### 6. Resource Management
- File handle leaks
- Resource cleanup (context managers)
- Memory efficiency
- Process lifecycle management
- Temporary file handling

### 7. Performance Issues
- Inefficient algorithms
- N+1 query patterns (if database-related)
- Unnecessary computations
- String building inefficiencies
- Loop optimization opportunities

### 8. Concurrency & Threading
- Race conditions (if multi-threaded)
- Thread safety
- Lock handling
- Async/await patterns
- Deadlock potential

### 9. Logging & Debugging
- Logging coverage
- Log level appropriateness
- Debug information completeness
- Error message clarity
- Observability

### 10. Testing & Testability
- Testability of code structure
- Mock-friendly design
- Test coverage potential
- Dependency injection opportunities

### 11. Documentation
- Docstring completeness and accuracy
- README documentation
- Code comments clarity
- API documentation
- Configuration documentation

### 12. Dependencies & Compatibility
- Dependency management
- Version pinning
- Compatibility issues
- Transitive dependencies
- Alternative library options

### 13. Configuration Management
- Environment variable handling
- Configuration file management
- Secrets management
- Default value handling
- Configuration validation

## Requested Analysis Output

For each error category above, please provide:

1. **Issues Found**: Specific problems identified in the code
2. **Severity Level**: Critical, High, Medium, Low
3. **Affected Files**: Which files have this issue
4. **Example Code Locations**: Specific line numbers or function names if possible
5. **Impact**: What happens if this issue is not fixed
6. **Recommended Fix**: How to address it

## Requested Tool Recommendations

For each category with identified issues, recommend open source tools by providing:

1. **Tool Name**: Official project name
2. **Category**: What type of issues it detects/fixes
3. **Installation**: pip/brew/apt command
4. **Primary Use**: What it's best for
5. **Configuration**: How to configure it (.toml, .ini, .yaml file)
6. **Integration**: How to integrate into development workflow
7. **CI/CD Integration**: How to use in GitHub Actions, pre-commit hooks, etc.
8. **Output Format**: What it produces (JSON, XML, console output)
9. **Cost**: Free, Freemium, or Paid
10. **Language Support**: Does it support Python?

## Tool Priority Matrix

Rank the recommended tools by:
- **Impact**: How much improvement will it provide
- **Ease of Implementation**: How hard to set up and integrate
- **Maintenance Burden**: How much ongoing effort to maintain
- **Team Adoption**: Likelihood team will actually use it

Create a prioritized list of the top 10 tools to implement first.

## Implementation Roadmap

Provide a phased implementation plan:

**Phase 1 (Week 1)**: Quick wins - easiest tools to integrate (estimated 2-3 tools)
**Phase 2 (Week 2)**: Core quality tools - most impactful (estimated 3-4 tools)
**Phase 3 (Week 3)**: Advanced tools - comprehensive coverage (estimated 3-4 tools)
**Phase 4 (Ongoing)**: Maintenance and monitoring

For each phase, include:
- Tool installation steps
- Configuration requirements
- Expected time to set up
- Expected issues and how to resolve them
- Success metrics

## Pre-Commit Hook Setup

Recommend specific tools to add to `.pre-commit-config.yaml` for automatic checking before commits, with:
- Exact hook configuration
- Which files to run on
- What to do on failure (auto-fix, block, warn)

## CI/CD Pipeline Configuration

Provide GitHub Actions workflow examples that:
- Run all recommended tools
- Generate quality reports
- Enforce quality gates
- Create actionable reports

## Code Quality Metrics

Provide target metrics for the project:
- Type hint coverage %
- Test coverage %
- Documentation coverage %
- Security vulnerability count (target: 0)
- Critical issues count (target: 0)
- Code duplication %

## Final Summary

Provide a ranked list of "Top 5 Tools You Should Install This Week" with brief justification for each.

---

## Code Input

[PASTE THE 5 PYTHON FILES HERE]

---

## Expected Response Format

Structure your response with clear sections matching the evaluation categories above. Use tables where appropriate for tool comparisons. Provide specific, actionable recommendations tailored to this Python AI Router project.
