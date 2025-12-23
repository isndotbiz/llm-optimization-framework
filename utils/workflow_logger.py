#!/usr/bin/env python3
"""
Workflow Logger - Structured JSON logging for workflow execution
Provides detailed execution traces with performance metrics and step-by-step logs
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Single log entry"""
    timestamp: str
    level: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        return data


@dataclass
class StepExecution:
    """Execution details for a single workflow step"""
    step_name: str
    step_type: str
    status: str  # "pending", "running", "completed", "failed"
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    logs: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    result_preview: Optional[str] = None  # First 500 chars of result
    retry_count: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class WorkflowExecutionTrace:
    """Complete execution trace for a workflow"""
    workflow_id: str
    workflow_name: str
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    status: str = "pending"  # "pending", "running", "completed", "failed"
    steps: List[StepExecution] = field(default_factory=list)
    global_logs: List[Dict] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['steps'] = [step.to_dict() for step in self.steps]
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class WorkflowLogger:
    """Structured logging for workflow execution"""

    def __init__(self, workflow_id: str, workflow_name: str):
        """
        Initialize logger for a workflow

        Args:
            workflow_id: ID of workflow
            workflow_name: Name of workflow
        """
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.trace = WorkflowExecutionTrace(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            start_time=self._iso_timestamp()
        )
        self.current_step: Optional[str] = None
        self.step_start_time: Optional[float] = None

    def set_status(self, status: str):
        """Update workflow status"""
        self.trace.status = status

    def add_global_log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Add log entry at workflow level

        Args:
            level: Log level
            message: Log message
            context: Additional context
        """
        entry = {
            "timestamp": self._iso_timestamp(),
            "level": level.value,
            "message": message,
            "context": context or {}
        }
        self.trace.global_logs.append(entry)

    def start_step(self, step_name: str, step_type: str):
        """
        Begin step execution

        Args:
            step_name: Name of step
            step_type: Type of step (prompt, template, etc.)
        """
        self.current_step = step_name
        self.step_start_time = time.time()

        step_exec = StepExecution(
            step_name=step_name,
            step_type=step_type,
            status="running",
            start_time=self._iso_timestamp()
        )
        self.trace.steps.append(step_exec)

        self.add_global_log(
            LogLevel.INFO,
            f"Starting step: {step_name}",
            {"step_type": step_type}
        )

    def end_step(
        self,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        retry_count: int = 0
    ):
        """
        Complete step execution

        Args:
            result: Step result
            error: Error message if step failed
            retry_count: Number of retries
        """
        if not self.trace.steps:
            return

        step = self.trace.steps[-1]
        now = time.time()
        duration = (now - self.step_start_time) * 1000 if self.step_start_time else None

        step.end_time = self._iso_timestamp()
        step.duration_ms = duration
        step.retry_count = retry_count

        if error:
            step.status = "failed"
            step.error = error
            self.add_global_log(
                LogLevel.ERROR,
                f"Step failed: {step.step_name}",
                {"error": error}
            )
        else:
            step.status = "completed"
            # Store preview of result
            if result:
                result_str = str(result)
                step.result_preview = result_str[:500] + ("..." if len(result_str) > 500 else "")
            self.add_global_log(
                LogLevel.INFO,
                f"Step completed: {step.step_name}",
                {"duration_ms": duration, "retry_count": retry_count}
            )

    def log_step(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Add log entry for current step

        Args:
            level: Log level
            message: Log message
            context: Additional context
        """
        if not self.trace.steps:
            return

        step = self.trace.steps[-1]
        entry = {
            "timestamp": self._iso_timestamp(),
            "level": level.value,
            "message": message,
            "context": context or {}
        }
        step.logs.append(entry)

    def set_variables(self, variables: Dict[str, Any]):
        """Store workflow variables (excluding sensitive data)"""
        self.trace.variables = self._sanitize_variables(variables)

    def finish(self, status: str, error_message: Optional[str] = None):
        """
        Complete workflow execution

        Args:
            status: Final status (completed, failed)
            error_message: Error message if workflow failed
        """
        self.trace.end_time = self._iso_timestamp()
        self.trace.status = status
        self.trace.error_message = error_message

        # Calculate total duration
        if self.trace.start_time and self.trace.end_time:
            start = datetime.fromisoformat(self.trace.start_time)
            end = datetime.fromisoformat(self.trace.end_time)
            duration = (end - start).total_seconds() * 1000
            self.trace.duration_ms = duration

    def get_summary(self) -> Dict[str, Any]:
        """
        Get execution summary

        Returns:
            Summary dictionary with key metrics
        """
        total_steps = len(self.trace.steps)
        completed_steps = sum(1 for s in self.trace.steps if s.status == "completed")
        failed_steps = sum(1 for s in self.trace.steps if s.status == "failed")

        step_durations = [
            s.duration_ms for s in self.trace.steps
            if s.duration_ms is not None
        ]
        avg_step_duration = sum(step_durations) / len(step_durations) if step_durations else 0

        return {
            "workflow_id": self.trace.workflow_id,
            "workflow_name": self.trace.workflow_name,
            "status": self.trace.status,
            "total_duration_ms": self.trace.duration_ms,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "average_step_duration_ms": avg_step_duration,
            "error": self.trace.error_message,
            "start_time": self.trace.start_time,
            "end_time": self.trace.end_time
        }

    def get_trace(self) -> Dict:
        """Get complete execution trace"""
        return self.trace.to_dict()

    def save_trace(self, output_path: Path):
        """
        Save execution trace to JSON file

        Args:
            output_path: Path to save trace file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        trace_json = self.trace.to_json()
        output_path.write_text(trace_json, encoding='utf-8')

    def save_summary(self, output_path: Path):
        """
        Save execution summary to JSON file

        Args:
            output_path: Path to save summary file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary = self.get_summary()
        output_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def print_summary(self):
        """Print execution summary to console"""
        summary = self.get_summary()

        print("\n" + "=" * 70)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Workflow: {summary['workflow_name']} ({summary['workflow_id']})")
        print(f"Status: {summary['status'].upper()}")
        print(f"Duration: {summary['total_duration_ms']:.1f}ms" if summary['total_duration_ms'] else "Duration: N/A")
        print(f"Steps: {summary['completed_steps']}/{summary['total_steps']} completed")

        if summary['failed_steps'] > 0:
            print(f"Failed: {summary['failed_steps']}")

        if summary['average_step_duration_ms']:
            print(f"Average step duration: {summary['average_step_duration_ms']:.1f}ms")

        if summary['error']:
            print(f"Error: {summary['error']}")

        print("=" * 70)

    def print_step_details(self, step_index: int = -1):
        """
        Print details for a specific step

        Args:
            step_index: Index of step (negative indices count from end)
        """
        if step_index < -len(self.trace.steps) or step_index >= len(self.trace.steps):
            print("Invalid step index")
            return

        step = self.trace.steps[step_index]

        print(f"\nStep: {step.step_name} ({step.step_type})")
        print(f"Status: {step.status}")
        print(f"Duration: {step.duration_ms:.1f}ms" if step.duration_ms else "Duration: N/A")

        if step.retry_count > 0:
            print(f"Retries: {step.retry_count}")

        if step.result_preview:
            print(f"Result preview: {step.result_preview[:200]}")

        if step.error:
            print(f"Error: {step.error}")

        if step.logs:
            print("\nStep logs:")
            for log in step.logs:
                print(f"  [{log['level']}] {log['message']}")

    @staticmethod
    def _iso_timestamp() -> str:
        """Get current time as ISO 8601 timestamp"""
        return datetime.now().isoformat(timespec='milliseconds')

    @staticmethod
    def _sanitize_variables(variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize variables for logging (remove sensitive data)

        Args:
            variables: Variables dictionary

        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        sensitive_keys = {'password', 'secret', 'token', 'api_key', 'auth', 'credential'}

        for key, value in variables.items():
            # Check if key looks sensitive
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "..."
            else:
                sanitized[key] = value

        return sanitized
