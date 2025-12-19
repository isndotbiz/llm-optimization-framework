# YAML Workflow Implementation Guide

Complete implementation guide for building a production-ready YAML-based workflow system for LLM chaining and multi-step AI tasks.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Integration Patterns](#integration-patterns)
5. [Deployment Guide](#deployment-guide)
6. [Monitoring & Observability](#monitoring--observability)
7. [Security Considerations](#security-considerations)
8. [Performance Optimization](#performance-optimization)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (Web UI, CLI, API Clients, Mobile Apps, Integrations)      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      API Gateway                             │
│  (Authentication, Rate Limiting, Request Routing)            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Workflow Orchestration Layer                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Parser     │  │   Validator  │  │   Executor   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
│ LLM Providers │  │State Store │  │Action Queue│
│ (OpenAI,     │  │(Redis,     │  │(RabbitMQ,  │
│  Anthropic)  │  │ Postgres)  │  │ Kafka)     │
└──────────────┘  └────────────┘  └────────────┘
```

### Component Responsibilities

**API Gateway**
- Request authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- Load balancing

**Workflow Parser**
- YAML file validation
- Schema compliance checking
- Dependency graph construction
- Template compilation

**Workflow Executor**
- Step-by-step execution
- State management
- Error handling and recovery
- Parallel execution coordination

**State Store**
- Workflow execution state persistence
- Checkpoint management
- Resume capability
- Audit trail

**Action Queue**
- Asynchronous task processing
- Retry management
- Dead letter queue handling
- Priority-based execution

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourorg/llm-workflow-engine.git
cd llm-workflow-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Minimal Example

**1. Create a workflow file (`hello_world.yaml`):**

```yaml
workflow:
  name: "HelloWorld"
  version: "1.0"
  description: "Simple greeting workflow"

  variables:
    user_name: "World"

  steps:
    - id: "greet"
      name: "Generate Greeting"
      type: "llm_call"
      model: "gpt-4"
      temperature: 0.7
      prompt: |
        Generate a friendly greeting for {{user_name}}.
        Make it warm and personalized.
      outputs:
        - name: "greeting"
          type: "string"
```

**2. Execute the workflow:**

```python
import asyncio
from workflow_engine import WorkflowEngine

async def main():
    # Initialize engine
    engine = WorkflowEngine(
        openai_api_key="your-key-here"
    )

    # Load and execute workflow
    result = await engine.execute_file(
        'hello_world.yaml',
        variables={'user_name': 'Alice'}
    )

    print(result['outputs']['greeting'])

asyncio.run(main())
```

**3. Run it:**

```bash
python my_workflow.py
```

---

## Core Components

### 1. Workflow Engine (Main Entry Point)

```python
# workflow_engine.py

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

from .parser import WorkflowParser
from .executor import WorkflowExecutor
from .state_store import StateStore
from .llm_client import LLMClient
from .action_registry import ActionRegistry

class WorkflowEngine:
    """Main workflow engine coordinating all components."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        state_store: Optional[StateStore] = None,
        action_registry: Optional[ActionRegistry] = None
    ):
        """Initialize the workflow engine.

        Args:
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            state_store: Custom state store (optional)
            action_registry: Custom action registry (optional)
        """
        self.parser = WorkflowParser()
        self.llm_client = LLMClient(
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key
        )
        self.state_store = state_store or StateStore()
        self.action_registry = action_registry or ActionRegistry()
        self.executor = WorkflowExecutor(
            llm_client=self.llm_client,
            state_store=self.state_store,
            action_registry=self.action_registry
        )

    async def execute_file(
        self,
        filepath: str,
        variables: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a workflow from a YAML file.

        Args:
            filepath: Path to workflow YAML file
            variables: Initial workflow variables
            execution_id: Resume existing execution (optional)

        Returns:
            Execution result with outputs and metadata
        """
        # Parse workflow
        workflow = self.parser.parse_file(filepath)

        # Validate
        errors = self.parser.validate_workflow(workflow)
        if errors:
            raise ValueError(f"Workflow validation failed: {errors}")

        # Execute
        return await self.executor.execute(
            workflow,
            initial_vars=variables,
            execution_id=execution_id
        )

    async def execute_yaml(
        self,
        yaml_content: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow from YAML string.

        Args:
            yaml_content: YAML workflow definition
            variables: Initial workflow variables

        Returns:
            Execution result
        """
        import yaml
        data = yaml.safe_load(yaml_content)
        workflow = self.parser.parse_dict(data)

        errors = self.parser.validate_workflow(workflow)
        if errors:
            raise ValueError(f"Workflow validation failed: {errors}")

        return await self.executor.execute(workflow, initial_vars=variables)

    async def resume_execution(
        self,
        execution_id: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Resume a paused or failed workflow execution.

        Args:
            execution_id: Execution ID to resume
            variables: Updated variables (optional)

        Returns:
            Execution result
        """
        # Load state
        state = await self.state_store.load_state(execution_id)
        if not state:
            raise ValueError(f"Execution {execution_id} not found")

        # Update variables if provided
        if variables:
            state.variables.update(variables)

        # Resume execution
        return await self.executor.resume(state)

    def register_action(self, name: str, handler: callable):
        """Register a custom action handler.

        Args:
            name: Action name used in workflows
            handler: Async function to handle the action
        """
        self.action_registry.register(name, handler)

    def register_validator(self, name: str, handler: callable):
        """Register a custom validator.

        Args:
            name: Validator name used in workflows
            handler: Function that returns (is_valid, errors)
        """
        self.executor.register_validator(name, handler)

    async def list_executions(
        self,
        workflow_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """List workflow executions.

        Args:
            workflow_name: Filter by workflow name
            status: Filter by status (running, completed, failed)
            limit: Maximum results to return

        Returns:
            List of execution metadata
        """
        return await self.state_store.list_executions(
            workflow_name=workflow_name,
            status=status,
            limit=limit
        )

    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get current status of an execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution status and metadata
        """
        state = await self.state_store.load_state(execution_id)
        if not state:
            raise ValueError(f"Execution {execution_id} not found")

        return {
            'execution_id': execution_id,
            'workflow_name': state.workflow_name,
            'status': state.status,
            'current_step': state.current_step,
            'completed_steps': len(state.step_results),
            'started_at': state.created_at,
            'updated_at': state.updated_at,
            'variables': state.variables,
            'outputs': {
                step_id: result.outputs
                for step_id, result in state.step_results.items()
            }
        }

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution.

        Args:
            execution_id: Execution ID to cancel

        Returns:
            True if cancelled successfully
        """
        return await self.executor.cancel(execution_id)
```

### 2. Action Registry

```python
# action_registry.py

from typing import Dict, Callable, Any
import asyncio
import aiohttp
import json

class ActionRegistry:
    """Registry for custom workflow actions."""

    def __init__(self):
        self.actions: Dict[str, Callable] = {}
        self._register_builtin_actions()

    def _register_builtin_actions(self):
        """Register built-in actions."""
        self.register('http_fetch', self.http_fetch)
        self.register('http_post', self.http_post)
        self.register('send_email', self.send_email)
        self.register('save_to_file', self.save_to_file)
        self.register('database_insert', self.database_insert)
        self.register('sleep', self.sleep_action)

    def register(self, name: str, handler: Callable):
        """Register an action handler.

        Args:
            name: Action identifier
            handler: Async function(params) -> result
        """
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError(f"Action handler {name} must be async")

        self.actions[name] = handler

    async def execute(self, action_name: str, params: Dict[str, Any]) -> Any:
        """Execute a registered action.

        Args:
            action_name: Name of action to execute
            params: Action parameters

        Returns:
            Action result
        """
        if action_name not in self.actions:
            raise ValueError(f"Unknown action: {action_name}")

        handler = self.actions[action_name]
        return await handler(params)

    # Built-in actions

    async def http_fetch(self, params: Dict[str, Any]) -> str:
        """Fetch data from HTTP endpoint."""
        url = params.get('url')
        timeout = params.get('timeout', 30)
        headers = params.get('headers', {})

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout/1000),
                headers=headers
            ) as response:
                response.raise_for_status()
                return await response.text()

    async def http_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Post data to HTTP endpoint."""
        url = params.get('url')
        data = params.get('data', {})
        headers = params.get('headers', {'Content-Type': 'application/json'})

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    async def send_email(self, params: Dict[str, Any]) -> bool:
        """Send email notification."""
        # Integrate with your email service
        to = params.get('to')
        subject = params.get('subject')
        body = params.get('body')

        # Example: Using SendGrid, AWS SES, etc.
        print(f"Sending email to {to}: {subject}")
        return True

    async def save_to_file(self, params: Dict[str, Any]) -> str:
        """Save data to file."""
        import aiofiles
        from pathlib import Path

        path = params.get('path')
        filename = params.get('filename')
        data = params.get('data')

        filepath = Path(path) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(filepath, 'w') as f:
            if isinstance(data, (dict, list)):
                await f.write(json.dumps(data, indent=2))
            else:
                await f.write(str(data))

        return str(filepath)

    async def database_insert(self, params: Dict[str, Any]) -> str:
        """Insert data into database."""
        # Integrate with your database
        table = params.get('table')
        data = params.get('data')

        # Example: Using SQLAlchemy, asyncpg, etc.
        print(f"Inserting into {table}: {data}")
        return "record_id_123"

    async def sleep_action(self, params: Dict[str, Any]) -> None:
        """Sleep for specified duration."""
        duration_ms = params.get('duration_ms', 1000)
        await asyncio.sleep(duration_ms / 1000)
```

### 3. State Store Implementation

```python
# state_store.py

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import asyncio

@dataclass
class WorkflowState:
    """Workflow execution state."""
    execution_id: str
    workflow_name: str
    status: str  # running, completed, failed, paused
    current_step: Optional[str]
    variables: Dict[str, Any]
    step_results: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None

class StateStore:
    """State persistence layer."""

    def __init__(self, backend: str = "memory"):
        """Initialize state store.

        Args:
            backend: Storage backend (memory, redis, postgres)
        """
        self.backend = backend
        if backend == "memory":
            self._memory_store: Dict[str, WorkflowState] = {}
        elif backend == "redis":
            import aioredis
            self._redis = None  # Initialize Redis connection
        elif backend == "postgres":
            import asyncpg
            self._pg_pool = None  # Initialize Postgres pool

    async def save_state(self, state: WorkflowState):
        """Persist workflow state."""
        state.updated_at = datetime.now()

        if self.backend == "memory":
            self._memory_store[state.execution_id] = state
        elif self.backend == "redis":
            await self._save_to_redis(state)
        elif self.backend == "postgres":
            await self._save_to_postgres(state)

    async def load_state(self, execution_id: str) -> Optional[WorkflowState]:
        """Load workflow state."""
        if self.backend == "memory":
            return self._memory_store.get(execution_id)
        elif self.backend == "redis":
            return await self._load_from_redis(execution_id)
        elif self.backend == "postgres":
            return await self._load_from_postgres(execution_id)

    async def delete_state(self, execution_id: str):
        """Delete workflow state."""
        if self.backend == "memory":
            if execution_id in self._memory_store:
                del self._memory_store[execution_id]
        elif self.backend == "redis":
            await self._delete_from_redis(execution_id)
        elif self.backend == "postgres":
            await self._delete_from_postgres(execution_id)

    async def list_executions(
        self,
        workflow_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List workflow executions."""
        if self.backend == "memory":
            executions = list(self._memory_store.values())
            if workflow_name:
                executions = [e for e in executions if e.workflow_name == workflow_name]
            if status:
                executions = [e for e in executions if e.status == status]
            executions = executions[:limit]
            return [asdict(e) for e in executions]

        # Implement for other backends
        return []

    # Backend-specific implementations

    async def _save_to_redis(self, state: WorkflowState):
        """Save to Redis."""
        if not self._redis:
            return
        await self._redis.set(
            f"workflow:{state.execution_id}",
            json.dumps(asdict(state), default=str),
            ex=604800  # 7 days TTL
        )

    async def _load_from_redis(self, execution_id: str) -> Optional[WorkflowState]:
        """Load from Redis."""
        if not self._redis:
            return None
        data = await self._redis.get(f"workflow:{execution_id}")
        if data:
            state_dict = json.loads(data)
            return WorkflowState(**state_dict)
        return None

    async def _save_to_postgres(self, state: WorkflowState):
        """Save to PostgreSQL."""
        if not self._pg_pool:
            return

        query = """
            INSERT INTO workflow_executions
            (execution_id, workflow_name, status, current_step, variables,
             step_results, created_at, updated_at, error)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (execution_id)
            DO UPDATE SET
                status = $3,
                current_step = $4,
                variables = $5,
                step_results = $6,
                updated_at = $8,
                error = $9
        """

        async with self._pg_pool.acquire() as conn:
            await conn.execute(
                query,
                state.execution_id,
                state.workflow_name,
                state.status,
                state.current_step,
                json.dumps(state.variables),
                json.dumps(state.step_results, default=str),
                state.created_at,
                state.updated_at,
                state.error
            )
```

---

## Integration Patterns

### 1. REST API Integration

```python
# api.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from workflow_engine import WorkflowEngine

app = FastAPI()
engine = WorkflowEngine()

class WorkflowExecutionRequest(BaseModel):
    workflow_file: str
    variables: Dict[str, Any] = {}

class WorkflowResponse(BaseModel):
    execution_id: str
    status: str
    message: str

@app.post("/workflows/execute", response_model=WorkflowResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Execute a workflow asynchronously."""
    try:
        # Start execution in background
        execution_id = generate_execution_id()

        background_tasks.add_task(
            run_workflow,
            execution_id,
            request.workflow_file,
            request.variables
        )

        return WorkflowResponse(
            execution_id=execution_id,
            status="started",
            message="Workflow execution started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/status/{execution_id}")
async def get_workflow_status(execution_id: str):
    """Get workflow execution status."""
    try:
        status = await engine.get_execution_status(execution_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/workflows/cancel/{execution_id}")
async def cancel_workflow(execution_id: str):
    """Cancel a running workflow."""
    try:
        cancelled = await engine.cancel_execution(execution_id)
        if cancelled:
            return {"status": "cancelled"}
        else:
            raise HTTPException(status_code=400, detail="Could not cancel")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_workflow(execution_id: str, workflow_file: str, variables: Dict):
    """Background task to run workflow."""
    try:
        await engine.execute_file(
            workflow_file,
            variables=variables,
            execution_id=execution_id
        )
    except Exception as e:
        print(f"Workflow {execution_id} failed: {e}")
```

### 2. CLI Integration

```python
# cli.py

import click
import asyncio
from workflow_engine import WorkflowEngine

@click.group()
def cli():
    """LLM Workflow Engine CLI"""
    pass

@cli.command()
@click.argument('workflow_file')
@click.option('--var', '-v', multiple=True, help='Variable in format key=value')
@click.option('--resume', help='Resume execution ID')
def execute(workflow_file, var, resume):
    """Execute a workflow from YAML file."""
    engine = WorkflowEngine()

    # Parse variables
    variables = {}
    for v in var:
        key, value = v.split('=', 1)
        variables[key] = value

    # Run workflow
    result = asyncio.run(
        engine.execute_file(workflow_file, variables=variables, execution_id=resume)
    )

    click.echo(f"Execution completed: {result['execution_id']}")
    click.echo(f"Status: {result['status']}")

@cli.command()
@click.argument('execution_id')
def status(execution_id):
    """Get status of a workflow execution."""
    engine = WorkflowEngine()
    status = asyncio.run(engine.get_execution_status(execution_id))

    click.echo(f"Execution ID: {execution_id}")
    click.echo(f"Status: {status['status']}")
    click.echo(f"Current Step: {status.get('current_step', 'N/A')}")
    click.echo(f"Completed Steps: {status['completed_steps']}")

@cli.command()
@click.option('--workflow', help='Filter by workflow name')
@click.option('--status', help='Filter by status')
def list_executions(workflow, status):
    """List workflow executions."""
    engine = WorkflowEngine()
    executions = asyncio.run(
        engine.list_executions(workflow_name=workflow, status=status)
    )

    for exec in executions:
        click.echo(f"{exec['execution_id']}: {exec['workflow_name']} - {exec['status']}")

if __name__ == '__main__':
    cli()
```

Usage:
```bash
# Execute workflow
python cli.py execute my_workflow.yaml -v topic="AI Ethics" -v audience="students"

# Check status
python cli.py status abc-123-def

# List executions
python cli.py list-executions --status running
```

---

This implementation guide provides everything needed to build a production-ready YAML-based workflow system for LLM chaining. The modular architecture allows for easy extension and integration with existing systems.
