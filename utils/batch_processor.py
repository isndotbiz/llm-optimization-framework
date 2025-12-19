#!/usr/bin/env python3
"""
Batch Processor - Process multiple prompts automatically with progress tracking
for AI Router application
"""

from pathlib import Path
from typing import Any, List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import time


@dataclass
class BatchJob:
    """Represents a batch processing job"""
    job_id: str
    model_id: str
    prompts: List[str]
    total_prompts: int
    completed: int = 0
    failed: int = 0
    status: str = "pending"  # pending, running, paused, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    checkpoint_file: Optional[Path] = None


@dataclass
class BatchResult:
    """Individual result within a batch"""
    prompt_index: int
    prompt: str
    response_text: str
    tokens_input: int
    tokens_output: int
    duration: float
    success: bool
    error_message: Optional[str] = None


class BatchProcessor:
    """Processes multiple prompts in batch with checkpointing"""

    def __init__(self, checkpoint_dir: Path):
        """
        Initialize batch processor

        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)
        self.current_job: Optional[BatchJob] = None

    def load_prompts_from_file(self, file_path: Path) -> List[str]:
        """
        Load prompts from text file (one per line) or JSON

        Args:
            file_path: Path to prompts file

        Returns:
            List of prompt strings
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Prompts file not found: {file_path}")

        if file_path.suffix == '.json':
            data = json.loads(file_path.read_text(encoding='utf-8'))
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'prompts' in data:
                return data['prompts']
            else:
                return [str(data)]
        else:
            # Read text file, filter empty lines and comments
            return [
                line.strip()
                for line in file_path.read_text(encoding='utf-8').splitlines()
                if line.strip() and not line.strip().startswith('#')
            ]

    def create_job(self, model_id: str, prompts: List[str]) -> BatchJob:
        """
        Create a new batch job

        Args:
            model_id: Model to use for processing
            prompts: List of prompts to process

        Returns:
            BatchJob instance
        """
        import uuid
        job_id = str(uuid.uuid4())[:8]
        checkpoint_file = self.checkpoint_dir / f"batch_{job_id}.json"

        job = BatchJob(
            job_id=job_id,
            model_id=model_id,
            prompts=prompts,
            total_prompts=len(prompts),
            checkpoint_file=checkpoint_file
        )
        return job

    def save_checkpoint(self, job: BatchJob, results: List[BatchResult]):
        """
        Save progress checkpoint

        Args:
            job: Current batch job
            results: Results so far
        """
        data = {
            "job": {
                "job_id": job.job_id,
                "model_id": job.model_id,
                "prompts": job.prompts,
                "total_prompts": job.total_prompts,
                "completed": job.completed,
                "failed": job.failed,
                "status": job.status,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "checkpoint_file": str(job.checkpoint_file) if job.checkpoint_file else None
            },
            "results": [asdict(r) for r in results],
            "timestamp": datetime.now().isoformat()
        }

        if job.checkpoint_file:
            job.checkpoint_file.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')

    def load_checkpoint(self, checkpoint_file: Path) -> tuple[BatchJob, List[BatchResult]]:
        """
        Load saved checkpoint to resume

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            Tuple of (BatchJob, List[BatchResult])
        """
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_file}")

        data = json.loads(checkpoint_file.read_text(encoding='utf-8'))

        # Reconstruct BatchJob
        job_data = data['job']
        job = BatchJob(
            job_id=job_data['job_id'],
            model_id=job_data['model_id'],
            prompts=job_data['prompts'],
            total_prompts=job_data['total_prompts'],
            completed=job_data['completed'],
            failed=job_data['failed'],
            status=job_data['status'],
            started_at=datetime.fromisoformat(job_data['started_at']) if job_data['started_at'] else None,
            completed_at=datetime.fromisoformat(job_data['completed_at']) if job_data['completed_at'] else None,
            checkpoint_file=Path(job_data['checkpoint_file']) if job_data['checkpoint_file'] else None
        )

        # Reconstruct results
        results = [
            BatchResult(**r) for r in data['results']
        ]

        return job, results

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints

        Returns:
            List of checkpoint info dicts
        """
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob("batch_*.json"):
            try:
                data = json.loads(checkpoint_file.read_text(encoding='utf-8'))
                job_data = data['job']

                checkpoints.append({
                    'file': checkpoint_file,
                    'job_id': job_data['job_id'],
                    'model_id': job_data['model_id'],
                    'status': job_data['status'],
                    'completed': job_data['completed'],
                    'total': job_data['total_prompts'],
                    'failed': job_data['failed'],
                    'timestamp': data['timestamp']
                })
            except Exception:
                # Skip corrupted checkpoint files
                continue

        # Sort by timestamp descending
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
        return checkpoints

    def process_batch(
        self,
        job: BatchJob,
        execute_fn: Callable,
        progress_callback: Optional[Callable] = None,
        error_strategy: str = "continue"
    ) -> List[BatchResult]:
        """
        Process batch job with progress tracking.

        Args:
            job: BatchJob to process
            execute_fn: Function that takes (prompt) and returns ModelResponse
            progress_callback: Optional callback for progress updates
            error_strategy: "stop", "continue", or "threshold:N" (stop after N errors)

        Returns:
            List of BatchResult objects
        """
        results = []
        job.status = "running"
        job.started_at = datetime.now()
        self.current_job = job

        error_count = 0
        error_threshold = self._parse_error_strategy(error_strategy)

        for idx, prompt in enumerate(job.prompts):
            try:
                # Execute model
                response = execute_fn(prompt)

                result = BatchResult(
                    prompt_index=idx,
                    prompt=prompt,
                    response_text=response.text if hasattr(response, 'text') else str(response),
                    tokens_input=response.tokens_input if hasattr(response, 'tokens_input') else 0,
                    tokens_output=response.tokens_output if hasattr(response, 'tokens_output') else 0,
                    duration=response.duration_seconds if hasattr(response, 'duration_seconds') else 0.0,
                    success=True
                )
                job.completed += 1

            except Exception as e:
                result = BatchResult(
                    prompt_index=idx,
                    prompt=prompt,
                    response_text="",
                    tokens_input=0,
                    tokens_output=0,
                    duration=0.0,
                    success=False,
                    error_message=str(e)
                )
                job.failed += 1
                error_count += 1

                if error_strategy == "stop" or (error_threshold and error_count >= error_threshold):
                    job.status = "failed"
                    results.append(result)
                    self.save_checkpoint(job, results)
                    break

            results.append(result)

            # Save checkpoint every 5 prompts
            if (idx + 1) % 5 == 0:
                self.save_checkpoint(job, results)

            # Progress callback
            if progress_callback:
                progress_callback(job, idx + 1)

        # Final status
        if job.status != "failed":
            job.status = "completed" if job.failed == 0 else "completed_with_errors"

        job.completed_at = datetime.now()
        self.save_checkpoint(job, results)
        self.current_job = None

        return results

    def export_results(
        self,
        job: BatchJob,
        results: List[BatchResult],
        output_file: Path,
        format: str = 'json'
    ):
        """
        Export batch results to JSON or CSV

        Args:
            job: Batch job
            results: Results to export
            output_file: Output file path
            format: 'json' or 'csv'
        """
        if format == 'json':
            data = {
                "job": {
                    "job_id": job.job_id,
                    "model_id": job.model_id,
                    "total_prompts": job.total_prompts,
                    "completed": job.completed,
                    "failed": job.failed,
                    "status": job.status,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                },
                "results": [asdict(r) for r in results],
                "summary": {
                    "total": job.total_prompts,
                    "completed": job.completed,
                    "failed": job.failed,
                    "success_rate": (job.completed / job.total_prompts * 100) if job.total_prompts > 0 else 0
                }
            }
            output_file.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')

        elif format == 'csv':
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['index', 'prompt', 'response', 'success', 'tokens_in', 'tokens_out', 'duration', 'error'])
                writer.writeheader()
                for r in results:
                    writer.writerow({
                        'index': r.prompt_index,
                        'prompt': r.prompt[:100] + '...' if len(r.prompt) > 100 else r.prompt,
                        'response': r.response_text[:100] + '...' if len(r.response_text) > 100 else r.response_text,
                        'success': r.success,
                        'tokens_in': r.tokens_input,
                        'tokens_out': r.tokens_output,
                        'duration': f"{r.duration:.2f}",
                        'error': r.error_message or ''
                    })
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _parse_error_strategy(self, strategy: str) -> Optional[int]:
        """
        Parse error strategy string

        Args:
            strategy: Error strategy string

        Returns:
            Error threshold number or None
        """
        if strategy.startswith("threshold:"):
            try:
                return int(strategy.split(':')[1])
            except (IndexError, ValueError):
                return None
        return None
