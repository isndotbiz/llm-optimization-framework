#!/usr/bin/env python3
"""
Workflow Engine v2 - Enhanced Prompt Chaining and Multi-Step AI Automation
Includes: validation, advanced conditions, retry logic, timeouts, structured logging

Features:
  - Enhanced validation with helpful error messages (WorkflowValidator)
  - Advanced condition evaluation (>, <, >=, <=, and, or, not)
  - Retry logic with exponential backoff and timeouts (RetryHandler)
  - Structured JSON logging with execution traces (WorkflowLogger)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import yaml
from dataclasses import dataclass, field
import re
import time
from datetime import datetime

# Import workflow enhancement modules (conditionally to support both old and new)
try:
    from .workflow_validator import WorkflowValidator
    from .condition_evaluator import ConditionEvaluator
    from .retry_handler import RetryHandler, RetryConfig
    from .workflow_logger import WorkflowLogger, LogLevel
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    name: str
    step_type: str  # "prompt", "template", "conditional", "loop", "sleep", "extract"
    config: Dict[str, Any]
    depends_on: Optional[List[str]] = None


@dataclass
class WorkflowExecution:
    """Workflow execution state"""
    workflow_id: str
    workflow_name: str
    steps: List[WorkflowStep]
    variables: Dict[str, Any]
    results: Dict[str, Any]  # Step name -> result
    status: str  # "pending", "running", "completed", "failed"
    current_step: int = 0
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    logger: Optional[WorkflowLogger] = None


class WorkflowEngine:
    """Execute multi-step AI workflows with variable passing and advanced features"""

    def __init__(self, workflows_dir: Path, ai_router):
        """
        Initialize WorkflowEngine

        Args:
            workflows_dir: Directory containing workflow YAML files
            ai_router: Reference to AIRouter for model execution
        """
        self.workflows_dir = workflows_dir
        self.workflows_dir.mkdir(exist_ok=True)
        self.ai_router = ai_router  # Reference to AIRouter for model execution

    def load_workflow(self, workflow_path: Path) -> WorkflowExecution:
        """
        Load workflow from YAML file with validation

        Args:
            workflow_path: Path to workflow YAML file

        Returns:
            WorkflowExecution instance ready for execution

        Raises:
            ValueError if workflow validation fails
        """
        # Validate workflow file first (if validator available)
        if ENHANCEMENTS_AVAILABLE:
            is_valid, errors = WorkflowValidator.validate_file(workflow_path)
            if not is_valid:
                error_msg = "Workflow validation failed:\n"
                for error in errors:
                    error_msg += f"  - {error}\n"
                raise ValueError(error_msg)

        try:
            data = yaml.safe_load(workflow_path.read_text(encoding='utf-8'))
        except Exception as e:
            raise ValueError(f"Failed to load workflow from {workflow_path}: {e}")

        # Parse workflow metadata
        workflow_id = data.get('id', workflow_path.stem)
        workflow_name = data.get('name', workflow_id)

        # Parse steps
        steps = []
        for step_data in data.get('steps', []):
            step = WorkflowStep(
                name=step_data['name'],
                step_type=step_data['type'],
                config=step_data,
                depends_on=step_data.get('depends_on')
            )
            steps.append(step)

        # Initialize execution state
        logger = None
        if ENHANCEMENTS_AVAILABLE:
            logger = WorkflowLogger(workflow_id, workflow_name)

        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            steps=steps,
            variables=data.get('variables', {}),
            results={},
            status="pending",
            start_time=datetime.now(),
            logger=logger
        )

        return execution

    def execute_workflow(self, execution: WorkflowExecution,
                        progress_callback: Optional[Callable] = None) -> Dict:
        """
        Execute complete workflow with variable passing

        Features:
          - Retry logic with exponential backoff
          - Configurable timeouts per step
          - Enhanced condition evaluation
          - Structured logging

        Args:
            execution: WorkflowExecution instance
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary of results keyed by step name

        Raises:
            Exception if workflow fails (unless on_error: continue)
        """
        execution.status = "running"
        execution.start_time = datetime.now()

        if execution.logger:
            execution.logger.set_status("running")
            execution.logger.set_variables(execution.variables)

        try:
            for i, step in enumerate(execution.steps):
                execution.current_step = i

                if progress_callback:
                    progress_callback(execution, step)

                # Check dependencies
                if not self._check_dependencies(step, execution):
                    if execution.logger:
                        execution.logger.add_global_log(
                            LogLevel.INFO,
                            f"Skipping step {step.name} - dependencies not met"
                        )
                    print(f"Skipping step {step.name} - dependencies not met")
                    continue

                # Log step start
                if execution.logger:
                    execution.logger.start_step(step.name, step.step_type)

                # Execute step based on type
                try:
                    # Check for retry configuration
                    retry_config = None
                    if 'retry' in step.config and ENHANCEMENTS_AVAILABLE:
                        retry_config = RetryConfig.from_dict(step.config['retry'])
                    elif 'timeout' in step.config and ENHANCEMENTS_AVAILABLE:
                        # Create minimal retry config with just timeout
                        retry_config = RetryConfig(timeout=step.config['timeout'])

                    # Execute with retry if configured
                    if retry_config:
                        def step_execute():
                            if step.step_type == "prompt":
                                return self._execute_prompt_step(step, execution)
                            elif step.step_type == "template":
                                return self._execute_template_step(step, execution)
                            elif step.step_type == "conditional":
                                return self._execute_conditional_step(step, execution)
                            elif step.step_type == "loop":
                                return self._execute_loop_step(step, execution)
                            elif step.step_type == "extract":
                                return self._execute_extract_step(step, execution)
                            elif step.step_type == "sleep":
                                return self._execute_sleep_step(step, execution)
                            else:
                                raise ValueError(f"Unknown step type: {step.step_type}")

                        retry_attempt_count = 0

                        def on_retry(attempt, delay, error):
                            nonlocal retry_attempt_count
                            retry_attempt_count = attempt
                            if execution.logger:
                                execution.logger.log_step(
                                    LogLevel.WARNING,
                                    f"Retry attempt {attempt}: {str(error)[:100]}. Waiting {delay:.1f}s...",
                                    {"error": str(error)}
                                )
                            print(f"  Retry attempt {attempt}: {error}. Waiting {delay:.1f}s...")

                        result = RetryHandler.execute_with_retry(
                            step_execute,
                            retry_config=retry_config,
                            on_retry_callback=on_retry
                        )
                    else:
                        if step.step_type == "prompt":
                            result = self._execute_prompt_step(step, execution)
                        elif step.step_type == "template":
                            result = self._execute_template_step(step, execution)
                        elif step.step_type == "conditional":
                            result = self._execute_conditional_step(step, execution)
                        elif step.step_type == "loop":
                            result = self._execute_loop_step(step, execution)
                        elif step.step_type == "extract":
                            result = self._execute_extract_step(step, execution)
                        elif step.step_type == "sleep":
                            result = self._execute_sleep_step(step, execution)
                        else:
                            raise ValueError(f"Unknown step type: {step.step_type}")

                        retry_attempt_count = 0

                    # Store result
                    execution.results[step.name] = result

                    # Update variables if step defines outputs
                    if 'output_var' in step.config:
                        execution.variables[step.config['output_var']] = result

                    # Log step completion
                    if execution.logger:
                        execution.logger.end_step(result=result, retry_count=retry_attempt_count)

                except Exception as e:
                    # Log step failure
                    if execution.logger:
                        execution.logger.end_step(error=str(e))

                    if step.config.get('on_error') == 'continue':
                        print(f"Error in step {step.name}: {e} (continuing)")
                        execution.results[step.name] = {"error": str(e)}
                    else:
                        execution.status = "failed"
                        execution.error_message = str(e)
                        execution.end_time = datetime.now()
                        if execution.logger:
                            execution.logger.finish("failed", str(e))
                        raise

            execution.status = "completed"
            execution.end_time = datetime.now()
            if execution.logger:
                execution.logger.finish("completed")
            return execution.results

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            if execution.logger:
                execution.logger.finish("failed", str(e))
            raise

    def _execute_prompt_step(self, step: WorkflowStep, execution: WorkflowExecution) -> str:
        """Execute a prompt step by calling AI model"""
        # Substitute variables in prompt
        prompt = self._substitute_variables(step.config['prompt'], execution.variables)

        # Get model
        model_id = step.config.get('model', 'auto')

        if model_id == 'auto':
            # Use auto-selection
            model_id, category, confidence = self.ai_router.model_selector.select_model(
                prompt, self.ai_router.models
            )
            model_data = self.ai_router.models[model_id]
        else:
            # Validate model exists
            if model_id not in self.ai_router.models:
                raise ValueError(f"Model '{model_id}' not found in available models")
            model_data = self.ai_router.models[model_id]

        # Log model selection
        if execution.logger:
            execution.logger.log_step(
                LogLevel.INFO,
                f"Executing model: {model_data['name']}",
                {"model_id": model_id}
            )

        # Execute model
        print(f"\n  Executing model: {model_data['name']}")
        response = self.ai_router.run_model(model_id, model_data, prompt)

        return response.text if hasattr(response, 'text') else str(response)

    def _execute_template_step(self, step: WorkflowStep, execution: WorkflowExecution) -> str:
        """Execute using a prompt template"""
        template_id = step.config['template_id']
        template = self.ai_router.template_manager.get_template(template_id)

        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        # Merge workflow variables with template variables
        template_vars = {**execution.variables, **step.config.get('variables', {})}

        # Render template
        prompt = template.render(template_vars)

        # Execute (similar to prompt step)
        model_id = step.config.get('model', 'auto')

        if model_id == 'auto':
            model_id, category, confidence = self.ai_router.model_selector.select_model(
                prompt, self.ai_router.models
            )
            model_data = self.ai_router.models[model_id]
        else:
            if model_id not in self.ai_router.models:
                raise ValueError(f"Model '{model_id}' not found")
            model_data = self.ai_router.models[model_id]

        if execution.logger:
            execution.logger.log_step(
                LogLevel.INFO,
                f"Executing template '{template_id}' with model: {model_data['name']}",
                {"template_id": template_id, "model_id": model_id}
            )

        print(f"\n  Executing template '{template_id}' with model: {model_data['name']}")
        response = self.ai_router.run_model(model_id, model_data, prompt)

        return response.text if hasattr(response, 'text') else str(response)

    def _execute_conditional_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute conditional branching with enhanced condition evaluation"""
        condition = step.config['condition']

        # Evaluate condition using enhanced evaluator if available
        if ENHANCEMENTS_AVAILABLE:
            result, explanation = ConditionEvaluator.evaluate(condition, execution.variables)
        else:
            # Fall back to simple evaluation
            result = self._evaluate_condition(condition, execution.variables)
            explanation = f"Condition evaluated to {result}"

        if execution.logger:
            execution.logger.log_step(
                LogLevel.INFO,
                explanation,
                {"condition": condition}
            )

        if result:
            then_step = step.config['then']
            # Execute then branch
            print(f"  Condition '{condition}' evaluated to TRUE, executing 'then' branch")
            return self._execute_inline_step(then_step, execution)
        else:
            else_step = step.config.get('else')
            if else_step:
                print(f"  Condition '{condition}' evaluated to FALSE, executing 'else' branch")
                return self._execute_inline_step(else_step, execution)
            else:
                print(f"  Condition '{condition}' evaluated to FALSE, no 'else' branch defined")

        return None

    def _execute_loop_step(self, step: WorkflowStep, execution: WorkflowExecution) -> List:
        """Execute loop over items"""
        items = execution.variables.get(step.config['items_var'], [])
        results = []

        if execution.logger:
            execution.logger.log_step(
                LogLevel.INFO,
                f"Looping over {len(items)} items from variable '{step.config['items_var']}'",
                {"items_count": len(items)}
            )

        print(f"  Looping over {len(items)} items from variable '{step.config['items_var']}'")

        for idx, item in enumerate(items):
            # Set loop variable
            loop_var = step.config.get('loop_var', 'item')
            execution.variables[loop_var] = item

            print(f"  Loop iteration {idx + 1}/{len(items)}: {loop_var} = {str(item)[:50]}...")

            # Execute loop body
            result = self._execute_inline_step(step.config['body'], execution)
            results.append(result)

        return results

    def _execute_extract_step(self, step: WorkflowStep, execution: WorkflowExecution) -> str:
        """Extract data from previous step result"""
        source_step = step.config['from_step']
        pattern = step.config.get('pattern')

        source_result = execution.results.get(source_step, "")

        if pattern:
            # Extract using regex
            match = re.search(pattern, str(source_result), re.DOTALL)
            if match:
                # If there are groups, return first group, otherwise return full match
                extracted = match.group(1) if match.groups() else match.group(0)
                if execution.logger:
                    execution.logger.log_step(
                        LogLevel.INFO,
                        f"Extracted text matching pattern from '{source_step}'",
                        {"pattern": pattern}
                    )
                print(f"  Extracted text matching pattern from '{source_step}': {extracted[:100]}...")
                return extracted
            else:
                if execution.logger:
                    execution.logger.log_step(
                        LogLevel.WARNING,
                        f"Pattern '{pattern}' not found in result from '{source_step}'",
                        {"pattern": pattern}
                    )
                print(f"  Warning: Pattern '{pattern}' not found in result from '{source_step}'")
                return ""

        # Return full result
        if execution.logger:
            execution.logger.log_step(
                LogLevel.INFO,
                f"Extracting full result from '{source_step}'"
            )
        print(f"  Extracting full result from '{source_step}'")
        return str(source_result)

    def _execute_sleep_step(self, step: WorkflowStep, execution: WorkflowExecution) -> str:
        """Sleep for specified duration (in seconds)"""
        duration = step.config.get('duration', 1)
        if execution.logger:
            execution.logger.log_step(
                LogLevel.INFO,
                f"Sleeping for {duration} seconds",
                {"duration": duration}
            )
        print(f"  Sleeping for {duration} seconds...")
        time.sleep(duration)
        return f"Slept for {duration} seconds"

    def _substitute_variables(self, text: str, variables: Dict) -> str:
        """
        Replace {{variable}} with actual values

        Supports:
        - {{variable_name}} - simple substitution
        - {{variable.key}} - nested dictionary access (future enhancement)
        """
        result = text
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, str(var_value))
        return result

    def _evaluate_condition(self, condition: str, variables: Dict) -> bool:
        """
        Simple condition evaluation (backward compatibility)

        Supports:
        - {{var}} == "value" - equality check
        - {{var}} != "value" - inequality check
        - {{var}} exists - existence check
        - {{var}} contains "substring" - substring check
        """
        # Substitute variables first
        condition = self._substitute_variables(condition, variables)

        if " == " in condition:
            left, right = condition.split(" == ", 1)
            return left.strip().strip('"\'') == right.strip().strip('"\'')
        elif " != " in condition:
            left, right = condition.split(" != ", 1)
            return left.strip().strip('"\'') != right.strip().strip('"\'')
        elif " contains " in condition:
            left, right = condition.split(" contains ", 1)
            return right.strip().strip('"\'') in left.strip().strip('"\'')
        elif "exists" in condition:
            var_name = condition.replace("exists", "").strip()
            return var_name in variables and variables[var_name]

        return False

    def _check_dependencies(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Check if step dependencies are met"""
        if not step.depends_on:
            return True

        for dep in step.depends_on:
            if dep not in execution.results:
                return False
            # Also check if dependency failed
            result = execution.results[dep]
            if isinstance(result, dict) and 'error' in result:
                return False

        return True

    def _execute_inline_step(self, step_config: Dict, execution: WorkflowExecution) -> Any:
        """Execute an inline step (used in conditionals/loops)"""
        step = WorkflowStep(
            name="inline",
            step_type=step_config['type'],
            config=step_config
        )

        if step.step_type == "prompt":
            return self._execute_prompt_step(step, execution)
        elif step.step_type == "template":
            return self._execute_template_step(step, execution)
        elif step.step_type == "extract":
            return self._execute_extract_step(step, execution)
        elif step.step_type == "sleep":
            return self._execute_sleep_step(step, execution)
        else:
            raise ValueError(f"Unsupported inline step type: {step.step_type}")

    def list_workflows(self) -> List[Dict]:
        """List available workflows"""
        workflows = []

        for workflow_file in self.workflows_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(workflow_file.read_text(encoding='utf-8'))
                workflows.append({
                    "id": data.get('id', workflow_file.stem),
                    "name": data.get('name', workflow_file.stem),
                    "description": data.get('description', ''),
                    "file": workflow_file,
                    "num_steps": len(data.get('steps', []))
                })
            except Exception as e:
                print(f"Warning: Could not load workflow {workflow_file}: {e}")
                continue

        return workflows

    def save_workflow_results(self, execution: WorkflowExecution, output_file: Path):
        """Save workflow execution results to JSON file"""
        import json

        data = {
            "workflow_id": execution.workflow_id,
            "workflow_name": execution.workflow_name,
            "status": execution.status,
            "results": execution.results,
            "variables": execution.variables,
            "start_time": execution.start_time.isoformat() if execution.start_time else None,
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "duration_seconds": (execution.end_time - execution.start_time).total_seconds()
                if execution.start_time and execution.end_time else None,
            "error_message": execution.error_message
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def validate_workflow(self, workflow_path: Path) -> tuple[bool, List[str]]:
        """
        Validate workflow YAML structure

        Returns:
            (is_valid, list_of_errors)
        """
        if ENHANCEMENTS_AVAILABLE:
            return WorkflowValidator.validate_file(workflow_path)

        # Fallback to simple validation
        errors = []

        try:
            data = yaml.safe_load(workflow_path.read_text(encoding='utf-8'))
        except Exception as e:
            return False, [f"Failed to parse YAML: {e}"]

        # Check required fields
        if 'steps' not in data:
            errors.append("Missing 'steps' field")
            return False, errors

        if not isinstance(data['steps'], list):
            errors.append("'steps' must be a list")
            return False, errors

        step_names = set()

        for i, step in enumerate(data['steps']):
            if 'name' not in step:
                errors.append(f"Step {i} missing 'name' field")
            else:
                # Check for duplicate step names
                if step['name'] in step_names:
                    errors.append(f"Duplicate step name: {step['name']}")
                step_names.add(step['name'])

            if 'type' not in step:
                errors.append(f"Step {i} ({step.get('name', 'unnamed')}) missing 'type' field")
            else:
                step_type = step['type']
                # Validate step type
                valid_types = ['prompt', 'template', 'conditional', 'loop', 'extract', 'sleep']
                if step_type not in valid_types:
                    errors.append(f"Step {step.get('name')}: Invalid type '{step_type}'. Valid types: {valid_types}")

                # Validate type-specific required fields
                if step_type == 'prompt' and 'prompt' not in step:
                    errors.append(f"Step {step.get('name')}: 'prompt' type requires 'prompt' field")

                if step_type == 'template' and 'template_id' not in step:
                    errors.append(f"Step {step.get('name')}: 'template' type requires 'template_id' field")

                if step_type == 'conditional' and 'condition' not in step:
                    errors.append(f"Step {step.get('name')}: 'conditional' type requires 'condition' field")

                if step_type == 'loop':
                    if 'items_var' not in step:
                        errors.append(f"Step {step.get('name')}: 'loop' type requires 'items_var' field")
                    if 'body' not in step:
                        errors.append(f"Step {step.get('name')}: 'loop' type requires 'body' field")

                if step_type == 'extract' and 'from_step' not in step:
                    errors.append(f"Step {step.get('name')}: 'extract' type requires 'from_step' field")

            # Check dependencies reference valid steps
            if 'depends_on' in step:
                for dep in step['depends_on']:
                    if dep not in step_names:
                        # This might be a forward reference, which we'll check later
                        pass

        return len(errors) == 0, errors
